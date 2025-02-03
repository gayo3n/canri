# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import *
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Project,CareerInformation,MBTI,Credentials,Category
from django.utils import timezone
from datetime import datetime
import json
from .forms import CSVUploadForm
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from .api import create_team_api, save_team_api, save_project_api, get_member_data, get_p_project_detail
from django.urls import reverse
import csv
from django.contrib import messages
from django.core import serializers
from django.test import TestCase
from django.http import HttpResponseServerError
from django.test import TestCase, override_settings
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"
    login_url = 'accounts:login'  # 未ログイン時にリダイレクトするURL


# -----メンバーリスト一覧-----
class MemberListView(TemplateView):
    template_name = "memberlist.html"

    def get(self, request, *args, **kwargs): 
        # カテゴリー一覧を取得
        categories=self.get_queryset()

        context = {
            "categories": categories  # カテゴリー
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        categories=self.get_queryset()

        context = {
            "categories": categories  # カテゴリー
        }
        return render(request, self.template_name, context)


        # カテゴリ検索
    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            categories = Category.objects.filter(category_name__icontains=query, deletion_flag=False)
        else:
            # フォーム未入力の場合はすべて
            categories = Category.objects.filter(deletion_flag=False)
        return categories


class NewProjectView(TemplateView):
    template_name = "create_new_project.html"


# -----メンバーリスト作成-----
class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"

    def get(self, request, *args, **kwargs):
        # フォームget
        form = CSVUploadForm()

        # メンバー検索
        members = self.get_queryset()

        # セッションから memberID_list を取得
        memberID_list = request.session.get('memberID_list', [])

        # member_dict を作成
        member_dict = self.get_member_dict(memberID_list)

        context = {
            'form': form,
            'members': members,
            'memberID_list': memberID_list,
            'member_dict': member_dict,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        memberID_list = request.session.get('memberID_list', [])

        # 削除リクエストの処理
        delete_member_id = request.POST.get('delete_member_id')
        if delete_member_id and delete_member_id.isdigit():
            delete_member_id = int(delete_member_id)
            if delete_member_id in memberID_list:
                memberID_list.remove(delete_member_id)
        else:
            # 追加リクエストの処理
            member_id = request.POST.get('member_id')
            if member_id and member_id.isdigit():
                member_id = int(member_id)
                if member_id not in memberID_list:
                    try:
                        Member.objects.get(member_id=member_id)
                        memberID_list.append(member_id)
                    except Member.DoesNotExist:
                        print(f"Member with ID {member_id} not found")

        # セッションに保存
        request.session['memberID_list'] = memberID_list

        # member_dict を作成
        member_dict = self.get_member_dict(memberID_list)

        members = self.get_queryset()
        context = {
            'members': members,
            'memberID_list': memberID_list,
            'member_dict': member_dict,
        }
        return render(request, self.template_name, context)

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            members = Member.objects.filter(name__icontains=query, deletion_flag=False)
        else:
            members = Member.objects.filter(deletion_flag=False)
        return members

    def get_member_dict(self, memberID_list):
        members_in_list = Member.objects.filter(member_id__in=memberID_list, deletion_flag=False)
        return {member.member_id: member.name for member in members_in_list}


# -----メンバーリスト保存-----
class MemberListMakeCompleteView(TemplateView):
    template_name = "memberlist_make_complete.html"

    def post(self, request, *args, **kwargs):
        # カテゴリ名（リスト名）と詳細を取得
        member_list_name = request.POST.get('member_list_name')
        member_list_details = request.POST.get('member_list_details')

        # エラーリストを作成
        errors = []

        # 入力チェック
        if not member_list_name:
            errors.append("メンバーリスト名を入力してください。")
        if not member_list_details:
            errors.append("メンバーリストの詳細を入力してください。")

        # カテゴリ名重複チェック
        if member_list_name and Category.objects.filter(category_name=member_list_name).exists():
            errors.append("このカテゴリ名はすでに存在します。別の名前を使用してください。")

        # エラーがあれば、エラーメッセージを表示して保存処理をスキップ
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect(reverse('canri_app:memberlist_make'))  # 元のページにリダイレクト

        # エラーがなければカテゴリを保存
        if member_list_name and member_list_details:
            # 新しいカテゴリを作成
            category = Category(
                category_name=member_list_name,
                detail=member_list_details,
                creation_date=timezone.now(),
                deletion_flag=False,
            )
            # カテゴリ保存
            category.save()

            # POSTデータから memberID_list を取得
            member_id_list = request.POST.getlist('memberID_list')

            # 各 member_id に対して MemberList を作成
            for member_id in member_id_list:
                try:
                    # メンバーを取得
                    member = Member.objects.get(member_id=member_id)
                    # MemberList オブジェク��を作成して保存
                    member_list = MemberList(
                        member_id=member.member_id,
                        category_id=category.category_id,
                        creation_date=timezone.now()
                    )
                    # メンバーリスト保存
                    member_list.save()
                    # セッションクリアｚ
                    request.session['memberID_list'] = []
                except Member.DoesNotExist:
                    # メンバーが見つからなかった場合の処理（エラーメッセージ等を追加しても良い）
                    print(f"Member with ID {member_id} not found")

            # 成功したらメンバーリスト作成完了ページにリダイレクト
            return redirect(reverse('canri_app:memberlist_make_complete'))


# -----メンバーリスト編集-----
class MemberListEditView(TemplateView):
    template_name = "memberList_edit.html"

    def get(self, request, category_id, *args, **kwargs):
        # セッションデータの初期化
        if 'memberID_list' in request.session:
            del request.session['memberID_list']

        # 初期化
        memberID_list = []
        member_dict = {}
        category = None

        # URL パラメータからリストIDを取得
        category_id_from_query = request.GET.get('category_id')

        # category_id を URL から取得した場合は優先して使用
        if category_id_from_query:
            category_id = category_id_from_query

        # category_id に基づいて MemberList をフィルタリング
        member_ids = MemberList.objects.filter(category_id=category_id, deletion_flag=False)

        # QuerySetからリストを作成
        memberID_list = [member.member_id for member in member_ids]

        # member_id に基づいて Member モデルから情報を取得
        members_in_list = Member.objects.filter(member_id__in=memberID_list, deletion_flag=False)

        # ID と名前の辞書を作成
        member_dict = {member.member_id: member.name for member in members_in_list}

        # カテゴリ名と詳細を取得
        category = get_object_or_404(Category, category_id=category_id)
        
        # カテゴリ情報をセッションに保存
        request.session['category_name'] = category.category_name
        request.session['category_detail'] = category.detail

        # セッションにリストを保存
        request.session['memberID_list'] = memberID_list

        # フォームとデータを取得
        form = CSVUploadForm()
        members = self.get_queryset()

        # コンテキストにリストと名前情報を渡す
        context = {
            'form': form,
            'members': members,
            'memberID_list': memberID_list,
            'member_dict': member_dict,  # 追加: 名前情報を渡す
            'category': category,
            'category_name': request.session.get('category_name', ''),  # セッションから取得したカテゴリ名
            'category_detail': request.session.get('category_detail', ''),  # セッションから取得したカテゴリ詳細
            'category_id': category_id,
        }
        return render(request, self.template_name, context)

    def post(self, request, category_id, *args, **kwargs):
        # セッションから memberID_list を取得
        memberID_list = request.session.get('memberID_list', [])

        # 削除リクエストがあるか判定
        delete_member_id = request.POST.get('delete_member_id')
        if delete_member_id and delete_member_id.isdigit():
            delete_member_id = int(delete_member_id)
            if delete_member_id in memberID_list:
                memberID_list.remove(delete_member_id)  # リストから削除
        else:
            # 追加リクエストの場合
            member_id = request.POST.get('member_id')
            if member_id and member_id.isdigit():
                member_id = int(member_id)
                if member_id not in memberID_list:
                    try:
                        Member.objects.get(member_id=member_id)  # メンバーIDの確認
                        memberID_list.append(member_id)  # リストに追加
                    except Member.DoesNotExist:
                        print(f"Member with ID {member_id} not found")

        # セッションに memberID_list を保存
        request.session['memberID_list'] = memberID_list

        # カテゴリ名と詳細を取得
        category = get_object_or_404(Category, category_id=category_id)

        # `memberID_list` の各 `member_id` に対応する `member_name` を取得
        members_in_list = Member.objects.filter(member_id__in=memberID_list, deletion_flag=False)

        # member_dict を作成する
        member_dict = {member.member_id: member.name for member in members_in_list}

        members = self.get_queryset()

        # セッションにカテゴリ情報を保存
        request.session['category_name'] = category.category_name
        request.session['category_detail'] = category.detail

        # コンテキストにリストと名前情報を渡す
        context = {
            'members': members,
            'memberID_list': memberID_list,
            'member_dict': member_dict,  # member_dict を渡す
            'category': category,
            'category_id': category_id,
        }
        
        return render(request, self.template_name, context)

    # メンバー検索
    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            members = Member.objects.filter(name__icontains=query, deletion_flag=False)
        else:
            # フォーム未入力の場合はすべて
            members = Member.objects.filter(deletion_flag=False)
        return members


# -----メンバーリスト編集保存-----
class MemberListEditCompleteView(TemplateView):
    template_name = "memberlist_make_complete.html"

    def post(self, request, *args, **kwargs):
        # カテゴリ名（リスト名）と詳細を取得
        category_id = request.POST.get('category_id')
        member_list_name = request.POST.get('member_list_name')
        member_list_details = request.POST.get('member_list_details')

        # エラーリストを作成
        errors = []

        # 入力チェック
        if not member_list_name:
            errors.append("メンバーリスト名を入力してください。")
        if not member_list_details:
            errors.append("メンバーリストの詳細を入力してください。")


        # エラーがあれば、エラーメッセージを表示して保存処理をスキップ
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect(reverse('canri_app:memberlist_edit'))  # 元のページにリダイレクト

        # エラーがなければカテゴリを保存
        if member_list_name and member_list_details:
            # カテゴリ情報を更新
            try:
                category = Category.objects.get(category_id=category_id)  # カテゴリを取得
                category.category_name = member_list_name  # カテゴリ名を更新
                category.detail = member_list_details  # カテゴリ詳細を更新
                category.update_date = timezone.now()  # 更新日時をセット
                category.save()  # 保存

            except Category.DoesNotExist:
                messages.error(request, "保存に失敗しました。")
                return redirect(reverse('canri_app:memberlist_edit'))

            # POSTデータから memberID_list を取得
            member_id_list = request.POST.getlist('memberID_list')

            # 既存のメンバーリストを削除フラグを立てる
            MemberList.objects.filter(category_id=category_id, deletion_flag=False).update(deletion_flag=True)  # 削除フラグを立てる

            # 新しくメンバーリストを作成
            for member_id in member_id_list:
                try:
                    # メンバーを取得
                    member = Member.objects.get(member_id=member_id)
                    # MemberList オブジェクトを作成して保存
                    member_list = MemberList(
                        member_id=member.member_id,
                        category_id=category.category_id,  # 更新されたカテゴリIDを使用
                        creation_date=timezone.now(),  # creation_date を設定
                        deletion_flag=False,
                    )
                    # メンバーリスト保存
                    member_list.save()
                    # セッションクリア
                    request.session['memberID_list'] = []
                except Member.DoesNotExist:
                    # メンバーが見つからなかった場合の処理（エラーメッセージ等を追加しても良い）
                    print(f"Member with ID {member_id} not found")

            # 成功したらメンバーリスト作成完了ページにリダイレクト
            return redirect(reverse('canri_app:memberlist_make_complete'))


# -----メンバーリスト削除確認-----
class MemberListDeleteView(TemplateView):
    template_name = "memberList_delete.html"

    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')
        category = Category.objects.get(category_id=category_id)
        context = {
            'category': category,
        }
        return render(request, 'memberlist_delete.html', context)


# -----メンバーリスト削除処理-----
class MemberListDeleteCompleteView(TemplateView):
    template_name = "memberlist_delete_complete.html"

    def get(self, request, category_id, *args, **kwargs):

        # 既存のメンバーリストを削除フラグを立てる
        MemberList.objects.filter(category_id=category_id).update(deletion_flag=True)  # 削除フラグを立てる
        # カテゴリーを削除フラグを立てる
        Category.objects.filter(category_id=category_id).update(deletion_flag=True)  # 削除フラグを立てる

        category=Category.objects.get(category_id=category_id)

        context = {
            'category': category,
        }
        return render(request, self.template_name, context)


# -----メンバー作成-----
class MemberMakeView(TemplateView):
    template_name = "member_make.html"
    def get(self, request, *args, **kwargs):
        mbti = MBTI.objects.all()  # 複数のフィールドを取得
        job_title = JobTitleInformation.objects.all()
        credentials = Credentials.objects.all()
        careerinformation = CareerInformation.objects.all()
        context = {
        'mbti': mbti,
        'job_title': job_title,
        'credentials': credentials,
        'careerinformation': careerinformation,
    }
        return render(request, 'member_make.html', context)


# -----メンバー保存-----
class MemberMakeCompleteView(TemplateView):
    template_name = 'member_make_complete.html'

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        birthdate = request.POST.get('birthday')
        job_title_id = request.POST.get('job_title')
        mbti_id = request.POST.get('MBTI')
        career_id = request.POST.get('career')
        qualification_id = request.POST.get('qualification')
        qualification2_id = request.POST.get('qualification2')
        qualification3_id = request.POST.get('qualification3')
        memo = request.POST.get('memo')

        try:
            job_title = JobTitleInformation.objects.get(job_title_id=job_title_id)
            mbti = MBTI.objects.get(mbti_id=mbti_id)
            career = CareerInformation.objects.get(career_id=career_id) if career_id else None
            qualification = Credentials.objects.get(qualification_id=qualification_id) if qualification_id else None
            qualification2 = Credentials.objects.get(qualification_id=qualification2_id) if qualification2_id else None
            qualification3 = Credentials.objects.get(qualification_id=qualification3_id) if qualification3_id else None

            # 重複チェック
            if Member.objects.filter(name=name, birthdate=birthdate, mbti_id=mbti_id).exists():
                messages.error(request, "同じメンバーは保存できません。")
                return redirect('canri_app:member_make',  member_id=kwargs['member_id'])
        
            speciality_height = 0
            planning_presentation_power = 0
            teamwork = 0
            time_management_ability = 0
            problem_solving_ability = 0

            member = Member(
                name=name,
                birthdate=birthdate,
                job=job_title,
                memo="",
                mbti=mbti,
                creation_date=timezone.now(),
                deletion_flag=False,
            )
            member.save()

            speciality_height += job_title.speciality_height
            planning_presentation_power += job_title.planning_presentation_power
            teamwork += job_title.teamwork
            time_management_ability += job_title.time_management_ability
            problem_solving_ability += job_title.problem_solving_ability

            # -----職歴の計算-----
            if career:
                speciality_height += career.speciality_height

                member_career = MemberCareer(
                    creation_date=timezone.now(),
                    career=career,
                    member=member,
                )
                member_career.save()

            # -----資格の計算-----
            if qualification:
                speciality_height += float(qualification.speciality_height)
                member_holding_qualification = MemberHoldingQualification(
                    creation_date=timezone.now(),
                    member=member,
                    qualification=qualification,
                )
                member_holding_qualification.save()

            if qualification2:
                speciality_height += float(qualification2.speciality_height)
                member_holding_qualification2 = MemberHoldingQualification(
                    creation_date=timezone.now(),
                    member=member,
                    qualification=qualification2,
                )
                member_holding_qualification2.save()

            if qualification3:
                speciality_height += float(qualification3.speciality_height)
                member_holding_qualification3 = MemberHoldingQualification(
                    creation_date=timezone.now(),
                    member=member,
                    qualification=qualification3,
                )
                member_holding_qualification3.save()

            # MBTIの計算
            planning_presentation_power += mbti.planning_presentation_power
            teamwork += mbti.teamwork
            time_management_ability += mbti.time_management_ability
            problem_solving_ability += mbti.problem_solving_ability

            # メンバーパラメータの計算
            member_parameter = MemberParameter(
                member=member,
                planning_presentation_power=planning_presentation_power,
                teamwork=teamwork,
                time_management_ability=time_management_ability,
                problem_solving_ability=problem_solving_ability,
                speciality_height=speciality_height,
            )
            member_parameter.save()

            messages.success(request, "メンバーが正常に作成されました。")
            return redirect('canri_app:member_make_complete')

        except JobTitleInformation.DoesNotExist:
            logger.error("指定された役職が見つかりません。")
            messages.error(request, "指定された役職が見つかりません。")
        except MBTI.DoesNotExist:
            logger.error("指定されたMBTIが見つかりません。")
            messages.error(request, "指定されたMBTIが見つかりません。")
        except CareerInformation.DoesNotExist:
            logger.error("指定された職歴が見つかりません。")
            messages.error(request, "指定された職歴が見つかりません。")
        except Credentials.DoesNotExist:
            logger.error("指定された資格が見つかりません。")
            messages.error(request, "指定された資格が見つかりません。")
        except Exception as e:
            logger.error(f"メンバーの作成中にエラーが発生しました: {e}")
            messages.error(request, f"メンバーの作成中にエラーが発生しました: {e}")

        return render(request, self.template_name)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


# -----メンバー編集-----
class MemberEditView(TemplateView):
    template_name = "member_edit.html"

    def get(self, request, *args, **kwargs):
        member_id = self.kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)
        mbti = MBTI.objects.all()  # 複数のフィールドを取得
        job_title = JobTitleInformation.objects.all()
        credentials = Credentials.objects.all()
        careerinformation = CareerInformation.objects.all()

        # 役職
        mem_job = JobTitleInformation.objects.get(job_title_id=int(member.job_id))

        # 職歴
        mem_careers = MemberCareer.objects.filter(member_id=member.member_id)
        mem_career = mem_careers.first() if mem_careers.exists() else None

        # 資格情報を取得
        qualifications = MemberHoldingQualification.objects.filter(member_id=member.member_id, deletion_flag=False)
        if qualifications.exists():
            qualification_ids = qualifications.values_list('qualification_id', flat=True)
            mem_credentials = Credentials.objects.filter(qualification_id__in=qualification_ids)
        else:
            mem_credentials = []

        # MBTI
        mem_mbti = MBTI.objects.get(mbti_id=member.mbti_id)

        context = {
            'member': member,
            'mbti': mbti,
            'job_title': job_title,
            'credentials': credentials,
            'careerinformation': careerinformation,
            'mem_job': mem_job,
            'mem_career': mem_career,
            'mem_credentials': mem_credentials,
            'mem_mbti': mem_mbti,
            'member_id': member.member_id,
        }
        return render(request, 'member_edit.html', context)


# -----メンバー編集保存-----
class MemberEditCompleteView(TemplateView):
    template_name = "member_make_complete.html"

    def post(self, request, *args, **kwargs):
        member_id = self.kwargs.get('member_id')
        
        # フォームからの入力を取得
        name = request.POST.get('name')
        birthdate = request.POST.get('birthday')  # 日付は適切なフォーマットで受け取る
        job_title_id = request.POST.get('job_title')  # JobTitleInformation ID
        mbti_id = request.POST.get('MBTI')  # MBTI ID を取得

        # 職歴と資格
        career = request.POST.get('career')
        qualifications = [
            request.POST.get('qualification'),
            request.POST.get('qualification2'),
            request.POST.get('qualification3'),
        ]


        try:
            # 外部キー関連のデータを取得
            member = Member.objects.get(member_id=member_id)
            job_title = JobTitleInformation.objects.get(job_title_id=int(job_title_id))
            mbti = MBTI.objects.get(mbti_id=mbti_id)

            # 更新が必要かチェック
            fields_updated = False

            if member.name != name:
                member.name = name
                fields_updated = True
            if str(member.birthdate) != birthdate:
                member.birthdate = birthdate
                fields_updated = True
            if member.job != job_title:
                member.job = job_title
                fields_updated = True
            if member.mbti != mbti:
                member.mbti = mbti
                fields_updated = True

            # 変更があった場合に保存
            if fields_updated:
                member.save()

            # 職歴の更新処理
            if career:
                career_obj = CareerInformation.objects.get(career_id=career)
                existing_career = MemberCareer.objects.filter(member=member, career=career_obj).exists()
                if not existing_career:
                    # 新規職歴を保存
                    MemberCareer.objects.update(
                        member=member,
                        career=career_obj,
                        creation_date=timezone.now()
                    )

            # 資格の更新処理
            existing_qualifications = set(
                MemberHoldingQualification.objects.filter(
                    member=member, deletion_flag=False
                ).values_list('qualification_id', flat=True)
            )
            new_qualifications = set(filter(None, qualifications))  # None を除外
            if existing_qualifications != new_qualifications:
                # 資格を一旦無効化
                MemberHoldingQualification.objects.filter(member=member).update(deletion_flag=True)

                # 新しい資格情報を登録
                for quali_id in new_qualifications:
                    quali = Credentials.objects.get(qualification_id=quali_id)
                    MemberHoldingQualification.objects.create(
                        member=member,
                        qualification=quali,
                        creation_date=timezone.now()
                    )

            # メンバーのパラメータ計算（必要なら実施）
            member_parameter, _ = MemberParameter.objects.get_or_create(member=member)
            member_parameter.planning_presentation_power = (
                int(job_title.planning_presentation_power) + int(mbti.planning_presentation_power)
            )
            member_parameter.teamwork = (
                int(job_title.teamwork) + int(mbti.teamwork)
            )
            member_parameter.time_management_ability = (
                int(job_title.time_management_ability) + int(mbti.time_management_ability)
            )
            member_parameter.problem_solving_ability = (
                int(job_title.problem_solving_ability) + int(mbti.problem_solving_ability)
            )
            member_parameter.speciality_height = int(job_title.speciality_height) + int(career_obj.speciality_height) + sum(
                map(
                    float,
                    Credentials.objects.filter(qualification_id__in=new_qualifications).values_list('speciality_height', flat=True)
                )
            )
            member_parameter.save()

        except JobTitleInformation.DoesNotExist:
            messages.error(request, "指定された職業が見つかりません。")
            return redirect('canri_app:member_edit', member_id=member_id)
        except MBTI.DoesNotExist:
            messages.error(request, "指定されたMBTIが見つかりません。")
            return redirect('canri_app:member_edit', member_id=member_id)
        except CareerInformation.DoesNotExist:
            messages.error(request, "指定された職歴が見つかりません。")
            return redirect('canri_app:member_edit', member_id=member_id)
        except Credentials.DoesNotExist:
            messages.error(request, "指定された資格が見つかりません。")
            return redirect('canri_app:member_edit', member_id=member_id)
        except Exception as e:
            messages.error(request, f"メンバーの保存中にエラーが発生しました: {e}")
            return redirect('canri_app:member_edit', member_id=member_id)

        # 保存が成功した場合にmember_make_completeへ遷移
        return render(request, self.template_name, {"member": member})


# -----CSVファイル処理-----
class FileUploadView(TemplateView):
    template_name = 'memberlist_make.html'

    def post(self, request, *args, **kwargs):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'static/uploads'))
            filename = fs.save(csv_file.name, csv_file)
            file_url = fs.url(filename)

            # CSVファイルのパスをセッションに保存
            request.session['csv_file_path'] = fs.path(filename)

            try:
                # CSVファイルを読み込み、行数をカウント
                with open(fs.path(filename), newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for row in reader) - 1  # ヘッダー行を除く

                # 重複メンバーリストを初期化
                duplicate_members = []

                # CSVファイルを再度読み込み、1行ずつMemberモデルに保存
                with open(fs.path(filename), newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    next(reader)  # ヘッダー行をスキップ
                    for row in reader:
                        try:
                            birthdate = self.parse_date(row[1])
                            job_title = JobTitleInformation.objects.get(job_title=row[2])
                            mbti = MBTI.objects.get(mbti_name=row[7])

                            # 重複チェック
                            existing_members = Member.objects.filter(name=row[0], birthdate=birthdate, mbti=mbti, deletion_flag=False)
                            if existing_members.exists():
                                duplicate_members.extend(existing_members)
                                continue

                            member = Member(
                                name=row[0],
                                birthdate=birthdate,
                                job=job_title,
                                mbti=mbti,
                                creation_date=timezone.now(),
                                deletion_flag=False,
                            )
                            member.save()

                        except Exception as e:
                            messages.error(request, f"行の保存中にエラーが発生しました: {e}")
                            return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))

                if duplicate_members:
                    context = {
                        'form': form,
                        'duplicate_members': duplicate_members,
                        'show_modal': True,
                    }

                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return render(request, 'canri_app/memberList_make.html', context)
                    
                    return render(request, self.template_name, context)
                
                messages.success(request, f"CSVファイルが正常にアップロードされました。{row_count} 行が処理されました。")
                return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))

            except UnicodeDecodeError:
                messages.error(request, "CSVファイルのエンコーディングが正しくありません。")
                return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))
            
            except Exception as e:
                messages.error(request, f"ファイルの処理中にエラーが発生しました: {e}")
                return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))

        # フォームが無効な場合の処理
        return render(request, self.template_name, {'form': form})
    
    def get(self, request, *args, **kwargs):
        form = CSVUploadForm()
        return render(request, self.template_name, {'form': form})

    def parse_date(self, date_str):
        for fmt in ('%Y/%m/%d', '%Y-%m-%d'):
            try:
                return timezone.make_aware(datetime.strptime(date_str, fmt))
            except ValueError:
                continue
        raise ValueError(f"日付のフォーマットが正しくありません: {date_str}")


# -----CSVファイル上書き処理-----
class MemberOverwriteView(TemplateView):
    template_name = 'memberlist_overwrite.html'

    def post(self, request, *args, **kwargs):
        selected_member_ids = [id for id in request.POST.getlist('members') if id]
        if not selected_member_ids:
            messages.error(request, "メンバーが選択されていません。")
            return redirect(request.META.get('HTTP_REFERER', 'canri_app:member_overwrite'))
        
        try:
            # セッションからCSVファイルのパスを取得
            csv_file_path = request.session.get('csv_file_path')
            if not csv_file_path:
                messages.error(request, "CSVファイルのパスが見つかりません。")
                return redirect(request.META.get('HTTP_REFERER', 'canri_app:member_overwrite'))
        
            # ファイルパスのデバッグメッセージを追加
            print(f"CSV File Path: {csv_file_path}")
        
            # ファイルが存在するか確認
            if not os.path.exists(csv_file_path):
                messages.error(request, "CSVファイルが存在しません。")
                return redirect(request.META.get('HTTP_REFERER', 'canri_app:member_overwrite'))
        
            # ファイルを開く前にデバッグメッセージを追加
            print(f"Opening file: {csv_file_path}")
        
            with open(csv_file_path, newline='', encoding='utf-8-sig') as f:
                print("File opened successfully")  # ファイルが開かれたことを確認するデバッグメッセージ
                reader = csv.reader(f)
                next(reader)  # ヘッダー行をスキップ
                for row in reader:
                    print(f"Processing row: {row}")  # デバッグメッセージを追加
                    member_name = row[0]
                    selected_members = Member.objects.filter(member_id__in=selected_member_ids, name=member_name)
                    if selected_members.exists():
                        for member in selected_members:
                            print(f"Processing member NAME: {member.name}")  # デバッグメッセージを追加
                            new_job_title_name = row[2]
                            new_mbti_name = row[7]
                            new_career_name = row[3]
                            new_qualification_names = [row[4], row[5], row[6]]
        
                            # デバッグメッセージを追加
                            print(f"Job Title: {new_job_title_name}, MBTI: {new_mbti_name}, Career: {new_career_name}, Qualifications: {new_qualification_names}")
        
                            try:
                                job_title = JobTitleInformation.objects.get(job_title=new_job_title_name)
                                print(f"Job title found: {job_title}")  # デバッグメッセージを追加
                            except JobTitleInformation.DoesNotExist:
                                messages.error(request, f"指定された役職 '{new_job_title_name}' が見つかりません。")
                                return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))
        
                            try:
                                mbti = MBTI.objects.get(mbti_name=new_mbti_name)
                                print(f"MBTI found: {mbti}")  # デバッグメッセージを追加
                            except MBTI.DoesNotExist:
                                messages.error(request, f"指定されたMBTI '{new_mbti_name}' が見つかりません。")
                                return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))
                            
                            if not new_career_name == "":
                                try:
                                    career = CareerInformation.objects.get(career=new_career_name)
                                    print(f"Career found: {career}")  # デバッグメッセージを追加
                                except CareerInformation.DoesNotExist:
                                    messages.error(request, f"指定された職歴 '{new_career_name}' が見つかりません。")
                                    return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))
            
                            qualifications = []
                            if not new_qualification_names == []:
                                for name in new_qualification_names:
                                    if name:
                                        try:
                                            qualification = Credentials.objects.get(qualification_name=name)
                                            qualifications.append(qualification)
                                            print(f"Qualification found: {qualification}")  # デバッグメッセージを追加
                                        except Credentials.DoesNotExist:
                                            messages.error(request, f"指定された資格 '{name}' が見つかりません。")
                                            return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))
        
                            member.job = job_title
                            member.mbti = mbti
                            member.save()
                            print(f"Member: {member}")
        
                            # 役職の更新処理
                            print(f"Updating job for member ID: {member.member_id} to job ID: {job_title.job_title_id}")
                            Member.objects.filter(member_id=member.member_id).update(job_id=job_title.job_title_id)
                            print("Job update completed")
                            
                            # MBTIの更新処理
                            print(f"Updating MBTI for member ID: {member.member_id} to MBTI ID: {mbti.mbti_id}")
                            Member.objects.filter(member_id=member.member_id).update(mbti_id=mbti.mbti_id)
                            print("MBTI update completed")
                            
                            # 職歴の更新処理
                            if not career == "":
                                print(f"Updating career for member ID: {member.member_id} to career ID: {career.career_id}")
                                MemberCareer.objects.filter(
                                    member_id=member.member_id,
                                ).update(
                                    member_id=member.member_id,
                                    career=career.career_id,
                                    creation_date=timezone.now()
                                )
                                print("Career update completed")
                            
                            # 資格の更新処理
                            print(f"Updating qualifications for member ID: {member.member_id}")
                            MemberHoldingQualification.objects.filter(member_id=member.member_id).update(deletion_flag=True)
                            if not qualifications == []:
                                for qualification in qualifications:
                                    print(f"Adding qualification ID: {qualification.qualification_id} for member ID: {member.member_id}")
                                    MemberHoldingQualification.objects.create(
                                        member_id=member.member_id,
                                        qualification=qualification,
                                        creation_date=timezone.now()
                                    )
                                print("Qualifications update completed")
        
                            # メンバーパラメータの計算
                            planning_presentation_power = job_title.planning_presentation_power + mbti.planning_presentation_power
                            teamwork = job_title.teamwork + mbti.teamwork
                            time_management_ability = job_title.time_management_ability + mbti.time_management_ability
                            problem_solving_ability = job_title.problem_solving_ability + mbti.problem_solving_ability
                            speciality_height = int(job_title.speciality_height)
                            if career: 
                                speciality_height += int(career.speciality_height)
                            if qualification: 
                                speciality_height += sum(float(qualification.speciality_height) for qualification in qualifications)
        
                            member_parameter, created = MemberParameter.objects.update_or_create(
                                member=member,
                                defaults={
                                    'planning_presentation_power': planning_presentation_power,
                                    'teamwork': teamwork,
                                    'time_management_ability': time_management_ability,
                                    'problem_solving_ability': problem_solving_ability,
                                    'speciality_height': speciality_height,
                                }
                            )
                            print("Member parameters updated")  # デバッグメッセージを追加
        
            messages.success(request, "上書き保存が正常に完了しました。")
            return redirect('canri_app:memberlist_make')
        
        except Member.DoesNotExist:
            messages.error(request, "選択されたメンバーが見つかりません。")
            return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))
        except Exception as e:
            print(f"Exception occurred: {e}")  # 例外が発生した場合のデバッグメッセージ
            messages.error(request, f"保存中にエラーが発生しました: {e}")
            return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))
    def get(self, request, *args, **kwargs):
        # セッションからCSVファイルのパスを取得
        csv_file_path = request.session.get('csv_file_path')
        if not csv_file_path:
            messages.error(request, "CSVファイルのパスが見つかりません。")
            return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))

        duplicate_members = []
        try:
            with open(csv_file_path, newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)  # ヘッダー行をスキップ
                for row in reader:
                    print(f"Processing row: {row}")  # デバッグメッセージを追加
                    birthdate = self.parse_date(row[1])
                    job_title = JobTitleInformation.objects.get(job_title=row[2])
                    mbti = MBTI.objects.get(mbti_name=row[7])

                    existing_members = Member.objects.filter(name=row[0], birthdate=birthdate, mbti=mbti)
                    if existing_members.exists():
                        duplicate_members.extend(existing_members)

        except Exception as e:
            print(f"Exception occurred: {e}")  # 例外が発生した場合のデバッグメッセージ
            messages.error(request, f"CSVファイルの読み込み中にエラーが発生しました: {e}")
            return redirect(request.META.get('HTTP_REFERER', 'canri_app:memberlist_make'))

        return render(request, self.template_name, {'members': duplicate_members})

    def parse_date(self, date_str):
        for fmt in ('%Y/%m/%d', '%Y-%m-%d'):
            try:
                return timezone.make_aware(datetime.strptime(date_str, fmt))
            except ValueError:
                continue
        raise ValueError(f"日付のフォーマットが正しくありません: {date_str}")


# -----メンバー削除確認-----
class MemberDeleteView(TemplateView):
    template_name = "member_delete.html"
    def get(self, request, *args, **kwargs):
        member_id=kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)
        context = {
            'member': member
        }
        return render(request, self.template_name, context)


# -----メンバー削除処理-----
class MemberDeleteCompleteView(TemplateView):
    template_name = "member_delete_complete.html"

    def get(self, request, *args, **kwargs):

        # メンバー削除フラグを立てる
        member_id=kwargs.get('member_id')
        Member.objects.filter(member_id=member_id).update(deletion_flag=True)  # 削除フラグを立てる

        member=Member.objects.get(member_id=member_id)

        context = {
            'member': member,
        }
        return render(request, self.template_name, context)


#新規プロジェクト作成
class NewProjectView(TemplateView):
    template_name = "new_project.html"

#新規プロジェクト編集
class NewProjectEditView(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 空のチームリストを追加
        teams = []

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})
#新規プロジェクト編集に戻る
class NewProjectEdit2View(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})
# チーム追加用のビュー
class CreateTeamView(TemplateView):
    template_name = "create_team.html"

    def post(self, request, *args, **kwargs):
        # POSTデータからプロジェクト情報を取得
        project_name = request.POST.get('project_name')  # プロジェクト名
        project_description = request.POST.get('project_description')  # プロジェクト説明
        start_date = request.POST.get('start_date')  # 開始日
        end_date = request.POST.get('end_date')  # 終了日
        teams = request.POST.get('teams')  # チーム情報（JSON文字列）

        # チーム情報をリスト形式に変換
        # POSTデータでは文字列として受け取るため、JSON形式でパースする
        if isinstance(teams, str):
            teams = json.loads(teams)

        # 入力された情報を保持したまま create_team.html テンプレートをレンダリング
        return render(request, self.template_name, {
            'project_name': project_name,  # プロジェクト名
            'project_description': project_description,  # プロジェクト説明
            'start_date': start_date,  # 開始日
            'end_date': end_date,  # 終了日
            'teams': teams  # チーム情報（リスト形式）
        })



# チーム追加のステップ2用ビュー
class CreateTeam2View(TemplateView):
    template_name = "create_team2.html"

    def post(self, request, *args, **kwargs):
        # POSTデータからプロジェクトとチーム関連の情報を取得
        #プロジェクト情報
        project_name = request.POST.get('project_name')  # プロジェクト名
        project_description = request.POST.get('project_description')  # プロジェクト説明
        start_date = request.POST.get('start_date')  # 開始日
        end_date = request.POST.get('end_date')  # 終了日
        #チーム情報
        teams = request.POST.get('teams')  # チーム情報（JSON文字列）
        team_size = request.POST.get('team_size')  # チームの規模
        team_type = request.POST.get('team_type')  # チームの種類
        auto_generate = request.POST.get('auto_generate')  # 自動生成フラグ
        # 削除フラグが立っていないカテゴリを取得
        categories = Category.objects.filter(deletion_flag=False)

        # チーム情報をリスト形式に変換
        if isinstance(teams, str):
            teams = json.loads(teams)

        if auto_generate:
            # 自動生成が有効な場合、create_team2.html にレンダリング
            # メンバー選択画面
            return render(request, self.template_name, {
                'project_name': project_name,  # プロジェクト名
                'project_description': project_description,  # プロジェクト説明
                'start_date': start_date,  # 開始日
                'end_date': end_date,  # 終了日
                'teams': teams,  # チーム情報（リスト形式）
                'team_size': team_size,  # チームの規模
                'team_type': team_type,  # チームの種類
                'categories': categories,  # カテゴリ情報
            })
        else:
            # 自動生成が無効な場合、create_team3.html にレンダリング
            # チーム詳細画面
            return render(request, 'create_team3.html', {
                'project_name': project_name,  # プロジェクト名
                'project_description': project_description,  # プロジェクト説明
                'start_date': start_date,  # 開始日
                'end_date': end_date,  # 終了日
                'teams': teams,  # チーム情報（リスト形式）
                'team_type': team_type,  # チームの種類
                'categories': categories,  # カテゴリ情報
            })
#チーム追加2に戻る
class CreateTeam2BackView(TemplateView):
    template_name = "create_team2.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_size = request.POST.get('team_size')
        team_type = request.POST.get('team_type')
        categories = Category.objects.filter(deletion_flag=False)

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # 入力された情報を保持した状態でcreate_team.htmlに遷移
        return render(request, self.template_name, {
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
                'teams': teams,
                'team_size': team_size,
                'team_type': team_type,
                'categories': categories,
            })
#チーム追加3
class CreateTeam3View(TemplateView):
    template_name = "create_team3.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_size = request.POST.get('team_size')
        team_type = request.POST.get('team_type')
        categories = Category.objects.filter(deletion_flag=False)
        selected_members = json.loads(request.POST.get('selected_members'))

        print(f"Creating team with project_name: {project_name}, team_size: {team_size}, team_type: {team_type}, selected_members: {selected_members}")

        data = {
            'team_type': team_type,
            'members': selected_members,
            'team_size': team_size
        }

        request._body = json.dumps(data).encode('utf-8')
        response = create_team_api(request)
        response_data = json.loads(response.content)

        print(f"Team creation response: {response_data}")

        if response.status_code == 200:
            team = response_data['team']
        else:
            team = []

        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams,
            'team_size': team_size,
            'team_type': team_type,
            'categories': categories,
            'selected_members': selected_members,
            'team': team
        })
#チーム保存
class SaveTeamView(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_name = request.POST.get('team_name')
        team_type = request.POST.get('team_type')
        team = request.POST.get('team')

        try:
            teams = json.loads(teams)
            team = json.loads(team)
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # チームを保存するためのデータを作成
        data = {
            'team_name': team_name,
            'team_type': team_type,
            'team': team
        }

        # save_team_api を呼び出してチームを保存
        request._body = json.dumps(data).encode('utf-8')
        response = save_team_api(request)
        response_data = json.loads(response.content)

        if response.status_code == 200:
            team_id = response_data['team_id']
            if isinstance(teams, list):
                teams.append(team_id)
            else:
                teams = [team_id]
            print("チームが保存されました:", team_id)  # チームIDをターミナルに表示
        else:
            print(response_data)
            print("チームの保存に失敗しました")  # エラーメッセージをターミナルに表示

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})
#新規プロジェクト保存
class SaveNewProjectView(TemplateView):
    template_name = "save_new_project.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description') 
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # プロジェクトを保存するためのデータを作成
        data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': json.loads(teams)
        }

        # save_project_api を呼び出してプロジェクトを保存
        request._body = json.dumps(data).encode('utf-8')
        response = save_project_api(request)
        response_data = json.loads(response.content)

        if response.status_code == 200:
            project_id = response_data['project_id']
            print("プロジェクトが保存されました:", project_id)  # プロジェクトIDをターミナルに表示
        else:
            print(response_data)
            print("プロジェクトの保存に失敗しました")  # エラーメッセージをターミナルに表示

        # 入力された情報を保持した状態でsave_new_project.htmlに遷移
        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams
        })
#チーム編集
class TeamEditView(TemplateView):
    template_name = "team_edit.html"

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.objects.get(team_id=team_id)
        members = TeamMember.objects.filter(team=team)
        categories = Category.objects.filter(deletion_flag=False)

        project_name = request.GET.get('project_name')
        project_description = request.GET.get('project_description')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        teams = request.GET.get('teams')
        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        context = {
            'team': team,
            'members': members,
            'categories': categories,
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.objects.get(team_id=team_id)
        team_name = request.POST.get('team_name')
        team_memo = request.POST.get('team_memo')
        team_members = request.POST.get('team')
        if not team_members:
            team_members = []
        else:
            team_members = json.loads(team_members)
        print("team_memo:", team_memo)

        team.team_name = team_name
        team.memo = team_memo
        team.save()

        TeamMember.objects.filter(team=team).delete()
        for member_id in team_members:
            member = Member.objects.get(member_id=member_id)
            TeamMember.objects.create(
                team=team,
                member=member,
                creation_date=timezone.now(),
                update_date=timezone.now()
            )

        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        return HttpResponseRedirect(f"{reverse('canri_app:team_edit_complete')}?project_name={project_name}&project_description={project_description}&start_date={start_date}&end_date={end_date}&teams={teams}&team_members={team_members}")

#チーム編集完了
class TeamEditCompleteView(TemplateView):
    template_name = "new_project_edit.html"

    def get(self, request, *args, **kwargs):
        project_name = request.GET.get('project_name')
        project_description = request.GET.get('project_description')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        teams = request.GET.get('teams')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        return render(request, self.template_name, {'project': project_data, 'teams': teams})
    
#チーム削除
class TeamDeleteView(TemplateView):
    template_name = "new_project_edit.html"

    def post(self, request, *args, **kwargs):
        team_id = request.POST.get('team_id')
        teams = request.POST.get('teams')
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        try:
            # チームとチームメンバーの削除フラグを1に設定
            team = Team.objects.get(team_id=team_id)
            team.deletion_flag = True
            team.save()

            TeamMember.objects.filter(team=team).update(deletion_flag=True)

            # teamsからチームIDを削除
            teams = [t for t in teams if t != int(team_id)]
        except Team.DoesNotExist:
            return HttpResponseNotFound("Team not found")

        # 入力された情報をリスト化
        project_data = {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date
        }

        # 入力された情報を保持した状態でnew_project_edit.htmlに遷移
        return render(request, self.template_name, {'project': project_data, 'teams': teams})
#チームメンバー編集
class TeamMemberEditView(TemplateView):
    template_name = "team_edit.html"

    def get(self, request, *args, **kwargs):
        member_id = kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)

        project_name = request.GET.get('project_name')
        project_description = request.GET.get('project_description')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        teams = request.GET.get('teams')
        team_id = request.GET.get('team_id')
        team_name = request.GET.get('team_name')
        team_memo = request.GET.get('team_memo')
        team_members = request.GET.get('team_members')
        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # APIエンドポイントを呼び出してメンバー情報を取得
        response = get_member_data(request, member_id)
        member_info = json.loads(response.content).get('member_data')

        context = {
            'member': member_info,
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams,
            'team_id': team_id,
            'team_name': team_name,
            'team_memo': team_memo,
            'team_members': team_members,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        member_id = kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)
        member_name = request.POST.get('member_name')
        member_memo = request.POST.get('member_memo')

        member.name = member_name
        member.memo = member_memo
        member.save()

        return JsonResponse({'status': 'success'})
#チームメンバー編集保存
class TeamMemberEditSaveView(TemplateView):
    template_name = "team_edit.html"

    def post(self, request, *args, **kwargs):
        member_id = request.POST.get('member_id')
        member = Member.objects.get(member_id=member_id)
        member_name = request.POST.get('member_name')
        member_memo = request.POST.get('member_memo')

        member.name = member_name
        member.memo = member_memo
        member.save()

        return JsonResponse({'status': 'success'})
#プロジェクトリスト
# class ProjectlistView(TemplateView):
#     template_name="projectlist.html"
# プロジェクトリスト表示
# class progress_within_ProjectlistView(TemplateView):
#     template_name="progress_within_projectlist.html"
# プロジェクトリスト表示
def projectListView(request):
    template_name = "progress_within_projectlist.html"
    ctx = {}
    query = request.GET.get('q')
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=0,deletion_flag=0)
    if query:
        qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)
from django.shortcuts   import render, get_object_or_404
from .models            import Project, ProjectAffiliationTeam, ProjectProgressStatus
#プロジェクト詳細表示時に利用
#project_idを使用してデータを取得
def project_detail_view(request, project_id):
    # プロジェクトを取得
    #project_idに当てはまるprojectテーブルのデータを取得
    project = get_object_or_404(Project, project_id=project_id)

    #プロジェクトに関連するチームを取得
    #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
    # teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')
    teams = ProjectAffiliationTeam.objects.filter(project=project, team__deletion_flag=0  # 関連する Team モデルの deletion_flag が 0 のものに限定
    ).select_related('team')


    # プロジェクトに関連するフェーズを取得
    # 上と同じ感じ
    phases = ProjectProgressStatus.objects.filter(project=project,deletion_flag=0).order_by('expiration_date')

    context = {
        #プロジェクトテーブルの情報
        'project': project,
        #プロジェクト所属チームテーブルの情報
        'teams': teams,
        #フェーズテーブルの情報
        'phases': phases,
    }
    # 情報を保持した状態でrender
    return render(request, 'project_detail.html', context)



# プロジェクト詳細変更保存時
from django.shortcuts               import render, redirect, get_object_or_404
from django.contrib                 import messages
from django.utils                   import timezone
from .models                        import Project
from django.views.decorators.http   import require_http_methods
@require_http_methods(["GET", "POST"])
# プロジェクト詳細変更保存時
def project_detail_update(request, project_id):
    # テンプレート名の定義
    templatename = f"project_detail.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            project_name        = request.POST.get('project_name')
            project_description = request.POST.get('project_description')
            start_date          = request.POST.get('start_date')
            end_date            = request.POST.get('end_date')

            # 必須項目の入力チェック
            if not all([project_name, project_description, start_date, end_date]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project'               : project,
                    'project_name'          : project_name,
                    'project_description'   : project_description,
                    'start_date'            : start_date,
                    'end_date'              : end_date,
                })

            # 開始日と終了日の論理チェック
            if start_date > end_date:
                # 開始日が終了日より後の場合、エラーメッセージを表示して再表示
                messages.error(request, '開始日は終了日よりも前の日付である必要があります。')
                return  render(request, templatename, {
                    'project'               : project,
                    'project_name'          : project_name,
                    'project_description'   : project_description,
                    'start_date'            : start_date,
                    'end_date'              : end_date,
                })

            # プロジェクト情報の更新
            project.project_name        = project_name
            project.project_detail      = project_description
            project.project_start_date  = start_date
            project.project_end_date    = end_date

            # 更新日時の設定
            project.update_date = timezone.now()

            # プロジェクト情報の保存
            project.save()

            # 成功メッセージの追加
            messages.success(request, 'プロジェクトが正常に更新されました。')

            # プロジェクトを取得
            #project_idに当てはまるprojectテーブルのデータを取得
            project = get_object_or_404(Project, project_id=project_id)
            #プロジェクトに関連するチームを取得
            #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
            teams   = ProjectAffiliationTeam.objects.filter(project=project,team__deletion_flag=0).select_related('team')
            # プロジェクトに関連する���ェーズを取得
            # 上と同じ感じ
            phases  = ProjectProgressStatus.objects.filter(project=project,deletion_flag=0).order_by('expiration_date')
            context = {
                #プロジェクトテーブルの情報
                'project'   : project,
                #プロジェクト所属チームテーブルの情報
                'teams'     : teams,
                #フェーズテーブルの情報
                'phases'    : phases,
            }
            # 情報を保持した状態でrender
            return render(request, 'project_detail.html', context)

        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return  render(request, templatename, {
                'project'               : project,
                'project_name'          : project_name,
                'project_description'   : project_description,
                'start_date'            : start_date,
                'end_date'              : end_date,
            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})
# プロジェクト完了
def ProjectComplete(request, project_id):
    # テンプレート名の定義
    template_name = "progress_within_projectlist.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    # プロジェクトの削除フラグを立てる
    project.complete_flag = 1

    # 更新日時の設定
    project.update_date     = timezone.now()
    project.complete_date   = timezone.now()

    # プロジェクト情報の保存
    project.save()

    # 成功メッセージの追加
    # messages.success(request, 'プロジェクトが正常に更新されました。')

    #これ以降は再度進行中プロジェクトを表示する処理------------------------------------
    ctx     = {}
    query   = request.GET.get('q')
    qs      = Project.objects.all()
    qs      =qs.filter(complete_flag=0,deletion_flag=0)
    if query:
        qs  = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)
# フェーズ追加時
from django.shortcuts               import render, redirect, get_object_or_404
from django.contrib                 import messages
from django.utils                   import timezone
from .models                        import Project
from django.views.decorators.http   import require_http_methods
@require_http_methods(["GET", "POST"])
# フェーズ追加
def project_phase_add(request, project_id):

    # テンプレート名の定義
    templatename = f"project_detail.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    # project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            phase_name  = request.POST.get('phase_name')
            end_date2   = request.POST.get('end_date2')

            # # 必須項目の入力チェック
            if not all([project_id,phase_name,end_date2]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project_id'    : project_id,
                    'phase_name'    : phase_name,
                    'end_name2'     : end_date2,
                })

            ProjectProgressStatus.objects.create(
                project_id      =project_id,
                phase_name      =phase_name,  # メンバーの数をカウント
                expiration_date =end_date2,
                creation_date   =timezone.now()  # 現在の日時を設定
            )

            # 成功メッセージの追加
            messages.success(request, 'フェーズの追加がかんりょうしました')
            #-------------ここまででフェーズの追加完了-----------------

            #‐‐‐‐‐‐‐‐‐‐‐ここから進行中プロジェクト表示用の処理----------
            # プロジェクトを取得
            #project_idに当てはまるprojectテーブルのデータを取得
            project = get_object_or_404(Project, project_id=project_id)

            #プロジェクトに関連するチームを取得
            #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
            teams   = ProjectAffiliationTeam.objects.filter(project=project,team__deletion_flag=0).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases  = ProjectProgressStatus.objects.filter(project=project,deletion_flag=0).order_by('expiration_date')

            context = {
                #プロジェクトテーブルの情報
                'project'   : project,
                #プロジェクト所属チームテーブルの情報
                'teams'     : teams,
                #フェーズテーブルの情報
                'phases'    : phases,
            }
            # 情報を保持した状態でrender
            return render(request, 'project_detail.html', context)

        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return  render(request, templatename, {
                'project': project,
            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})

@require_http_methods(["GET", "POST"])
# フェーズ変更
def project_phase_edit(request, project_id):

    # テンプレート名の定義
    templatename = f"project_detail.html"

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            phaseid     = request.POST.get('phase_id')
            phase_name  = request.POST.get('phase_name')
            end_date3   = request.POST.get('expirationdate')

            project_progress_status=ProjectProgressStatus.objects.get(project_id=project_id,progress_status_id=phaseid)

            # # 必須項目の入力チェック
            if not all([project_progress_status,project_id,phaseid,phase_name,end_date3]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project_id': project_id,
                    'phase_id'  : phaseid,
                    'phase_name': phase_name,
                    'end_name3' : end_date3,
                })

            # 更新日時の設定
            # creation_date = timezone.now()

            project_progress_status.phase_name      = phase_name
            project_progress_status.expiration_date = end_date3
            project_progress_status.creation_date   = timezone.now()


# インスタンスをデータベースに保存
            project_progress_status.save()

            # 成功メッセージの追加
            messages.success(request, 'フェーズの追加がかんりょうしました')
            #-------------ここまででフェーズの追加完了-----------------

            #‐‐‐‐‐‐‐‐‐‐‐ここから進行中プロジェクト表示用の処理----------
            # プロジェクトを取得
            #project_idに当てはまるprojectテーブルのデータを取得
            project = get_object_or_404(Project, project_id=project_id)

            #プロジェクトに関連するチームを取得
            #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
            teams   = ProjectAffiliationTeam.objects.filter(project=project,team__deletion_flag=0).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases  = ProjectProgressStatus.objects.filter(project=project,deletion_flag=0).order_by('expiration_date')

            context = {
                #プロジェクトテーブルの情報
                'project'   : project,
                #プロジェクト��属チームテーブルの情報
                'teams'     : teams,
                #フェーズテーブルの情報
                'phases'    : phases,
            }
            # 情報を保持した状態でrender
            return render(request, 'project_detail.html', context)

        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return render(request, templatename, {
                'project': project,

            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})

#進行中プロジェクトのフェーズ削除
#フェーズ変更のコピペ
from datetime import datetime
def project_phase_delete(request, project_id):

    # テンプレート名の定義
    templatename = f"project_detail.html"

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            phaseid                 = request.POST.get('phase_id')
            project_progress_status = ProjectProgressStatus.objects.get(project_id=project_id,progress_status_id=phaseid)

            # # 必須項目の入力チェック
            if not all([project_id,phaseid,]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return  render(request, templatename, {
                    'project_id': project_id,
                    'phase_id'  : phaseid,
                })
            project_progress_status.deletion_flag   = 1
            project_progress_status.creation_date   =timezone.now()

            # インスタンスをデータベースに保存
            project_progress_status.save()

            # 成功メッセージの追加
            messages.success(request, 'フェーズの削除がかんりょうしました')
            #-------------ここまででフェーズの削除完了-----------------

            #‐‐‐‐‐‐‐‐‐‐‐ここから進行中プロジェクト表示用の処理----------
            # プロジェクトを取得
            #project_idに当てはまるprojectテーブルのデータを取得
            project = get_object_or_404(Project, project_id=project_id)

            #プロジェクトに関連するチームを取得
            #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
            teams   = ProjectAffiliationTeam.objects.filter(project=project,team__deletion_flag=0).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases  = ProjectProgressStatus.objects.filter(project=project,deletion_flag=0).order_by('expiration_date')

            context = {
                #プロジェクトテーブルの情報
                'project'   : project,
                #プロジェクト��属チームテーブルの情報
                'teams'     : teams,
                #フェーズテーブルの情報
                'phases'    : phases,
            }
            # 情報を保持した状態でrender
            return  render(request, 'project_detail.html', context)

        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return  render(request, templatename, {
                'project': project,

            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})

# 進行中プロジェクトのフェーズ完了
def project_phase_coplete(request, project_id):

    # テンプレート名の定義
    templatename = f"project_detail.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    # project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    if request.method == "GET":
        try:
            # POSTデータから各プロジェクト情報を取得
            phaseid             = request.GET.get('phase_id')

            project_progress_status =ProjectProgressStatus.objects.get(project_id=project_id,progress_status_id=phaseid)

            # # 必須項目の入力チェック
            if not all([project_progress_status,project_id,phaseid]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project_id': project_id,
                    'phase_id'  : phaseid,
                })

            project_progress_status.complete_flag   = 1
            project_progress_status.creation_date   =timezone.now()
            project_progress_status.complete_date   =timezone.now()


            # インスタンスをデータベースに保存
            project_progress_status.save()

            # 成功メッセージの追加
            messages.success(request, 'フェーズの削除がかんりょうしました')
            #-------------ここまででフェーズの削除完了-----------------

            #‐‐‐‐‐‐‐‐‐‐‐ここから進行中プロジェクト表示用の処理----------
            # プロジェクトを取得
            #project_idに当てはまるprojectテーブルのデータを取得
            project = get_object_or_404(Project, project_id=project_id)

            #プロジェクトに関連するチームを取得
            #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
            teams = ProjectAffiliationTeam.objects.filter(project=project,team__deletion_flag=0).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases = ProjectProgressStatus.objects.filter(project=project,deletion_flag=0).order_by('expiration_date')

            context = {
                #プロジェクトテーブルの情報
                'project': project,
                #プロジェクト属チームテーブルの情報
                'teams': teams,
                #フェーズテーブルの情報
                'phases': phases,
            }
            # 情報を保持した状態でrender
            return render(request, 'project_detail.html', context)

        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return render(request, templatename, {
                'project': project,

            })

# 進行中プロジェクト用のチーム追加用のビュー
class project_detail_Create_TeamView(TemplateView):
    template_name = "project_detail_create_team.html"
    def post(self, request, *args, **kwargs):
        # POSTデータからプロジェクト情報を取得
        project_id          = request.POST.get('project_id')            # プロジェクト名
        project_name        = request.POST.get('project_name')          # プロジェクト名
        project_description = request.POST.get('project_description')   # プロジェクト説明
        start_date          = request.POST.get('start_date')            #  開始日
        end_date            = request.POST.get('end_date')              # 終了日

        projectaffilitionteam_all= ProjectAffiliationTeam.objects.all()     #プロジェクト所属チームを全部取得
        teams=projectaffilitionteam_all.filter(project=project_id)          #プロジェクト所属チームからプロジェクト情報を利用して
                                                                            #プロジェクトに所属するものを取得
        # teamにプロジェクトに所属しているチームが入っているprojectaffilitionteamテーブルのチームIDを取得
        # それをもとにチームテーブルから情報を取得
        #そこからメンバー情報を抽出
        team_ids    =teams.values_list('team_id',flat=True)                 #テーブルからteam_idだけ取得
        #team_idsにはteeam_idだけが入っている
        teammembers = TeamMember.objects.filter(team_id__in=team_ids)  # チームIDに基づいてメンバーをフィルタリング チームが同じ奴だけ取得
        members     = list(teammembers.values_list('member_id', flat=True))
        # 入力された情報を保持したまま create_team.html テンプレートをレンダリング
        return render(request, self.template_name, {
            'project_id'            :project_id,
            'project_name'          :project_name,            # プロジェクト名
            'project_description'   :project_description,     # プロジェクト説明
            'start_date'            :start_date,              # 開始日
            'end_date'              :end_date,                # 終了日
            'member'                :members,
        })


# 進行中プロジェクト用のチーム追加のステップ2用ビュー
import json
from django.shortcuts import render
from .models import TeamMember
class project_detail_Create_Team2View(TemplateView):
    template_name = "project_detail_create_team2.html"

    def post(self, request, *args, **kwargs):
        # プロジェクト情報の取得
        project_id          = request.POST.get('project_id')
        project_name        = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date          = request.POST.get('start_date')
        end_date            = request.POST.get('end_date')
        member              = request.POST.get('member')
        # category=request.POST.get('category')

        # チーム情報の取得
        team_size       = request.POST.get('team_size')
        team_type       = request.POST.get('team_type')
        auto_generate   = request.POST.get('auto_generate')

        categories      = Category.objects.filter(deletion_flag=False)

        if auto_generate:
            # 自動生成が有効な場合、create_team2.html にレンダリング
            # メンバー選択画面
            return render(request, self.template_name, {
                'project_id'            :project_id,
                'project_name'          : project_name,             # プロジェクト名
                'project_description'   : project_description,      # プロジェクト説明
                'start_date'            : start_date,               # 開始日
                'end_date'              : end_date,                 # 終了日
                'member'                : json.dumps(member),       # メンバーIDをJSON形式で渡す
                'team_size'             : team_size,                # チームの規模
                'team_type'             : team_type,                # チームの種類
                'categories'            : categories,               # カテゴリ情報
            })
        else:
            # 自動生成が無効な場合、create_team3.html にレンダリング
            #memberとteam_sizeが変更される
            # チーム詳細画面
            return render(request, 'project_detail_create_team3.html', {
                'project_id'            :project_id,
                'project_name'          : project_name,             # プロジェクト名
                'project_description'   : project_description,      # プロジェクト説明
                'start_date'            : start_date,               # 開始日
                'end_date'              : end_date,                 # 終了日
                'member'                : member,
                'team_type'             : team_type,                # チームの種類
                'categories'            : categories,               # カテゴリ情報
            })
#プロジェクト進行チーム追加3
# memberが必要かどう
# 多分メンバー追加時に必要になる気がする
class project_detail_CreateTeam3View(TemplateView):
    # 使用するテンプレートファイルを指定
    template_name = "project_detail_create_team3.html"

    def post(self, request, *args, **kwargs):
        # フォームから送信されたデータを取得
        project_id          = request.POST.get('project_id')
        project_name        = request.POST.get('project_name')                  # プロジェクト名
        project_description = request.POST.get('project_description')           # プロジェクトの説明
        start_date          = request.POST.get('start_date')                    # 開始日
        end_date            = request.POST.get('end_date')                      # 終了日
        # チームの編成に関する情報を取得
        team_size           = request.POST.get('team_size')                     # チームサイズ
        team_type           = request.POST.get('team_type')                     # チームタイプ
        categories          = Category.objects.filter(deletion_flag=False)      # 削除されていないカテゴリを取得
        selected_members    = json.loads(request.POST.get('selected_members'))  # 選択されたメンバー情報をJSON形式からPythonオブジェクトに変換

        # チーム編成APIに送信するデータを準備
        data = {
            'team_type' : team_type,         # チームタイプ
            'members'   : selected_members,  # 選択されたメンバー
            'team_size' : team_size          # チームサイズ
        }

        # `request` の `_body` 属性にAPIリクエスト用のデータを設定
        request._body   = json.dumps(data).encode('utf-8')
        response        = create_team_api(request)                 # 外部API呼び出し

        # APIのレスポンスを解析
        response_data = json.loads(response.content)

        if response.status_code == 200:
            # チーム作成成功時の処理
            team = response_data['team']
            print("チームが作成されました:", team)      # ターミナルに作成されたチーム情報を表示
        else:
            # チーム作成失敗時の処理
            team = None
            print("チームの作成に失敗しました")        # エラーメッセージをターミナルに表示

        # ユーザ��入力の内容を保持しながらテンプレートをレンダリング
        return render(request, self.template_name, {
            'project_id'            : project_id,
            'project_name'          : project_name,            # プロジェクト名
            'project_description'   : project_description,     # プロジェクトの説明
            'start_date'            : start_date,              # 開始日
            'end_date'              : end_date,                # 終了日
            'team_size'             : team_size,               # チームサイズ
            'team_type'             : team_type,               # チームタイプ
            'categories'            : categories,              # 利用可能なカテゴリリスト
            'selected_members'      : selected_members,        # 選択されたメンバー
            'team'                  : team                     # 作成されたチーム情報（または失敗した場合はNone）
        })

#チーム新規作成保存
class project_detail_SaveTeamView(TemplateView):
    # 保存後の画面に使用するテンプレート
    template_name = "project_detail_create_team_complete.html"

    def post(self, request, *args, **kwargs):
        # POSTリクエストからプロジェクト情報を取得
        # projectの情報
        project_id              = request.POST.get('project_id')            # プロジェクトID
        project_name            = request.POST.get('project_name')          # プロジェクト名
        project_description     = request.POST.get('project_description')   # プロジェクトの説明
        start_date              = request.POST.get('start_date')            # プロジェクト開始日
        end_date                = request.POST.get('end_date')              # プロジェクト終了日
        team_name   = request.POST.get('team_name')     # チーム名
        team_type   = request.POST.get('team_type')     # チームの種類
        team        = request.POST.get('team')          # チーム情報（JSON形式）   member_idのみ

        print(team)

        # デバッグ用: リクエストボディをターミナルに表示
        print("リクエストボディ:", request.body)

        try:
            # JSON形式のデータをPythonオブジェクトに変換
            # teams = json.loads(teams)  # チームリスト
            team = json.loads(team)  # チームメンバー情報
        except json.JSONDecodeError as e:
            # JSONの解析エラー時の処理
            print("JSONDecodeError:", e)
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # チームを保存するためのデータを作成
        data = {
            'team_name': team_name,  # チーム名
            'team_type': team_type,  # チームの種類
            'team': team             # チームメンバー情報
        }

        # チーム保存APIを呼び出し
        request._body   = json.dumps(data).encode('utf-8')  # データをJSON形式に変換しリクエストボディとして設定
        response        = save_team_api(request)  # API呼び出し
        response_data   = json.loads(response.content)  # APIのレスポンスをJSON形式で取得

        if response.status_code == 200:
            # チーム保存成功時の処理
            team_id = response_data['team_id']  # 保存されたチームIDを取得
            ProjectAffiliation_Team = ProjectAffiliationTeam.objects.create(
            team_id=team_id,
            project_id=project_id,
            creation_date=timezone.now()  # 現在の日時を設定
        )
            print("チームが保存されました:", team_id)  # チームIDをターミナルに表示
            print("プロジェクトへの保存も完了;",ProjectAffiliation_Team)
        else:
            # チーム保存失敗時の処理
            print(response_data)  # レスポンスのエラー内容を表示
            print("チームの保存に失敗しました")  # エラーメッセージをターミナルに表示

        # プロジェクト情報を辞書形式にまとめる
        project_data = {
            'project_name'          : project_name,            # プロジェクト名
            'project_description'   : project_description,  # プロジェクトの説明
            'start_date'            : start_date,               # プロジェクト開始日
            'end_date'              : end_date                    # プロジェクト終了日
        }

        # プロジェクト情報とチームリストをテンプレートに渡し、新しいプロジェクト編集画面をレンダリング
        return render(request, self.template_name, {
            'project_id' : project_id,
        })
# 進行中プロジェクトのチーム詳細表示用と編集時の保存用ビュー
class projectTeamEditView(TemplateView):
    template_name = "team_detail.html"  # 使用するテンプレートを定義
    # getメソッドで画面表示  postメソッドでデータ保存
    # GETリクエストを処理して、データを取得・表示する
    def get(self, request, *args, **kwargs):
        team_id     = kwargs    .get            ('team_id')                     # URLパラメータからチームIDを取得
        team        = Team      .objects.get    (team_id=team_id)               # チームIDを使ってTeamオブジェクトを取得
        members     = TeamMember.objects.filter (team=team,deletion_flag=0)     # チームのメンバーを取得
        categories  = Category  .objects.filter (deletion_flag=0)               # 削除されていないカテゴリーを取得

        # プロジェクト関連のパラメータをGETリクエストから取得
        project_id = request.GET.get('project_id')

        # ここからteamsのための処理
        # プロジェクト所属チームテーブルからプロジェクトIDに基づいてチームを取得
        projectaffilitionteam_all= ProjectAffiliationTeam.objects.all()
        #取得したプロジェクトIDに基づいてチームを取得
        tem     =projectaffilitionteam_all.filter(project=project_id,deletion_flag=0)
        # チームIDを取得
        team_ids=tem.values_list('team_id',flat=True)
        # チームテーブルからチーム情報を取得
        teams   =Team.objects.filter(team_id__in=team_ids)

        # 取得したデータをコンテキストとしてテンプレートに渡す
        context = {
            'team'      : team,
            'members'   : members,
            'categories': categories,
            'project_id': project_id,
            'teams'     : teams
        }
        return render(request, self.template_name, context)

    # POSTリクエストを処理して、チームとプロジェクト情報を更新
    def post(self, request, *args, **kwargs):
        team_id         = kwargs.get('team_id')  # URLパラメータからチームIDを取得
        team            = Team.objects.get(team_id=team_id)  # チームIDを使ってTeamオブジェクトを取得
        team_name       = request.POST.get('team_name')  # フォームから新しいチーム名を取得
        team_memo       = request.POST.get('team_memo')  # フォームから新しいチームメモを取得
        team_members    = request.POST.get('team')  # フォームから選択されたメンバーのIDリストを取得

        # メンバーが空の場合は空リストを設定
        if not team_members:
            team_members = []
        else:
            # 'team_members' が文字列（JSON形式）で渡されている場合、リストに変換
            team_members = json.loads(team_members)

        print("team_memo:", team_memo)  # デバッグ用にチームメモを表示

        # チームの名前とメモを更新
        team.team_name  = team_name
        team.memo       = team_memo
        team.save()  # チーム情報を保存

        # 既存のチームメンバーを削除
        TeamMember.objects.filter(team=team).delete()

        # 新しいメンバーをチームに追加
        for member_id in team_members:
            member = Member.objects.get(member_id=member_id)  # メンバーIDを使ってMemberオブジェクトを取得
            TeamMember.objects.create(
                team=team,
                member=member,
                creation_date=timezone.now(),  # メンバーが追加された日時
                update_date=timezone.now()  # メンバーが追加された日時
            )

        # プロジェクト関連のパラメータをPOSTリクエストから取得
        # project_name = request.POST.get('project_name')
        # project_description = request.POST.get('project_description')
        # start_date = request.POST.get('start_date')
        # end_date = request.POST.get('end_date')
        project_id=request.POST.get('project_id')
        teams = request.POST.get('teams')

        # 更新後、完了ページへリダイレクト。更新されたプロジェクト情報やチームメンバーをURLパラメータとして渡す
        return render(request, "project_detail_create_team_complete.html", {
            'project_id' : project_id,
        })
# 進行中プロジェクトのチーム削除用のビュー
class project_team_delete(TemplateView):
    template_name = "project_detail_create_team_complete.html"

    def get(self, request, *args, **kwargs):
        team_id     = kwargs.       get('team_id')      # URLパラメータから取得
        project_id  = request.GET.  get('project_id')   # クエリパラメータから取得
        team        = Team.objects. get(team_id=team_id)# チームIDを使ってTeamオブジェクトを取得
        team.deletion_flag  = 1             # 削除フラグを立てる
        team.update_date    =timezone.now() # 更新日時を設定
        team.deletion_date  =timezone.now() # 削除日時を設定
        team.save()                         # データベースに変更を保存
        # 関連するTeamMemberの削除フラグを設定
        TeamMember.objects.filter(team=team).update(deletion_flag=1, update_date=timezone.now(),deletion_date=timezone.now())
        ProjectAffiliationTeam.objects.filter(team=team).update(deletion_flag=1,deletion_date=timezone.now())

        return render(request, self.template_name, {'project_id': project_id})
# 過去プロジェクトリスト
class Past_ProjectListView(TemplateView):
    template_name = "past_project_list.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        qs = Project.objects.filter(complete_flag=1, deletion_flag=0)
        if query:
            qs = qs.filter(project_name__icontains(query))  # プロジェクト名でフィルタリング

        context = {
            'project_list': qs
        }
        return render(request, self.template_name, context)
# 過去プロジェクト検索
def Post_projectListView(request):
    template_name = "past_project_list.html"
    ctx = {}
    query = request.GET.get('p')
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=1,deletion_flag=0)
    if query:
        qs = qs.filter(project_name__icontains(query))  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)
# 過去プロジェクト閲覧
class Past_ProjectView(TemplateView):
    template_name = "past_project_view.html"

    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        response = get_p_project_detail(request, project_id)
        project_data = json.loads(response.content).get('project_data')

        if not project_data:
            return HttpResponseNotFound("Project not found")

        # project_idに当てはまるProjectAffiliationTeamテーブルのデータを取得
        affiliation_teams = ProjectAffiliationTeam.objects.filter(project_id=project_id)
        teams = Team.objects.filter(team_id__in=[team.team.team_id for team in affiliation_teams])

        # フィードバックデータを取得
        feedbacks = Feedback.objects.filter(project_id=project_id, deletion_flag=0)
        team_members = TeamMember.objects.filter(team_id__in=teams, deletion_flag=0)
        members = Member.objects.filter(member_id__in=team_members, deletion_flag=0)

        # project_dataに日付フィールドが含まれていることを確認
        project_start_date = project_data.get('project_start_date')
        project_end_date = project_data.get('project_end_date')

        # 日付をパースしてからテンプレートに渡す
        if project_start_date:
            project_start_date = datetime.strptime(project_start_date, "%Y-%m-%d").date()
        if project_end_date:
            project_end_date = datetime.strptime(project_end_date, "%Y-%m-%d").date()

        context = {
            'project': project_data,
            'teams': teams,
            'members': members,
            'feedbacks': feedbacks,
            'project_start_date': project_start_date,
            'project_end_date': project_end_date
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        if 'delete' in request.POST:
            try:
                project = Project.objects.get(project_id=project_id)
                project.deletion_flag = 1
                project.save()
                return HttpResponseRedirect(reverse('canri_app:delete_past_project'))
            except Project.DoesNotExist:
                return HttpResponseNotFound("Project not found")
        else:
            post_evaluation_memo = request.POST.get('post_evaluation_memo')
            try:
                project = Project.objects.get(project_id=project_id)
                project.post_evaluation_memo = post_evaluation_memo
                if not project.project_end_date:
                    project.project_end_date = timezone.now()
                project.save()
                return HttpResponseRedirect(reverse('canri_app:save_past_project'))
            except Project.DoesNotExist:
                return HttpResponseNotFound("Project not found")

# 過去プロジェクト削除確認
class Past_ProjectDeletingView(View):
    template_name = "past_project_deleting_confirmation.html"

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, project_id=project_id)
        context = {
            'project_id': project_id,
            'project': project
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, project_id=project_id)
        context = {
            'project_id': project_id,
            'project': project
        }
        return render(request, self.template_name, context)

# 過去プロジェクト削除完了
class Past_Project_DeletedView(View):
    template_name = "past_project_deleted.html"

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        try:
            project = Project.objects.get(project_id=project_id)
            project.deletion_flag = 1
            project.save()
            return render(request, self.template_name, {'project': project})
        except Project.DoesNotExist:
            return render(request, "past_project_delete_error.html", {'message': 'Project not found'})
        except Exception as e:
            return render(request, "past_project_delete_error.html", {'message': str(e)})

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        try:
            project = Project.objects.get(project_id=project_id)
            project.deletion_flag = 1
            project.save()
            return render(request, self.template_name, {'project': project})
        except Project.DoesNotExist:
            return render(request, "past_project_delete_error.html", {'message': 'Project not found'})
        except Exception as e:
            return render(request, "past_project_delete_error.html", {'message': str(e)})

#フィードバックモーダル表示
class FeedbackView(TemplateView):
    template_name = "feedback_application.html"

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, project_id=project_id)
        context = {
            'project_id': project_id,
            'project': project
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, project_id=project_id)
        context = {
            'project_id': project_id,
            'project': project
        }
        return render(request, self.template_name, context)

# 過去プロジェクト削除完了
class Past_Project_DeletedView(View):
    template_name = "past_project_deleted.html"

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        try:
            project = Project.objects.get(project_id=project_id)
            project.deletion_flag = 1
            project.save()
            return render(request, self.template_name, {'project': project})
        except Project.DoesNotExist:
            return render(request, "past_project_delete_error.html", {'message': 'Project not found'})
        except Exception as e:
            return render(request, "past_project_delete_error.html", {'message': str(e)})

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        try:
            project = Project.objects.get(project_id=project_id)
            project.deletion_flag = 1
            project.save()
            return render(request, self.template_name, {'project': project})
        except Project.DoesNotExist:
            return render(request, "past_project_delete_error.html", {'message': 'Project not found'})
        except Exception as e:
            return render(request, "past_project_delete_error.html", {'message': str(e)})

# プロジェクト保存完了
class Project_Save_CompleteView(TemplateView):
    template_name = "save_past_project.html"

#フィードバック保存
class FeedbackSaveView(TemplateView):
    template_name = "feedback_save_complete.html"
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        project_id = data.get('project_id')
        existing_feedbacks = data.get('existing_feedbacks')
        new_feedbacks = data.get('new_feedbacks')

        # 既存のフィードバックを更新
        for feedback in existing_feedbacks:
            print('ddd',feedback.get('feedback_id'))
            feedback_id = feedback.get('feedback_id')
            member1_id = feedback.get('member1')
            member2_id = feedback.get('member2')
            priority = feedback.get('priority')

            feedback_instance = Feedback.objects.get(feedback_id=feedback_id)
            feedback_instance.member1_id = member1_id
            feedback_instance.member2_id = member2_id
            feedback_instance.priority_flag = (priority == 'True')
            feedback_instance.save()

        # 新しいフィードバックを作成
        for feedback in new_feedbacks:
            print('wwww',feedback.get('feedback_id'))
            member1_id = feedback.get('member1')
            member2_id = feedback.get('member2')
            priority = feedback.get('priority')

            Feedback.objects.create(
                member1_id=member1_id,
                member2_id=member2_id,
                project_id=project_id,
                priority_flag=(priority == 'True'),
                creation_date=timezone.now(),
                deletion_flag=False
            )

        context = {}
        return render(request, self.template_name, context)

# フィードバック削除
@require_http_methods(["POST"])
def delete_feedback(request):
    data = json.loads(request.body)
    feedback_id = data.get('feedback_id')
    feedback = get_object_or_404(Feedback, feedback_id=feedback_id)
    feedback.deletion_flag = True
    feedback.save()
    return JsonResponse({'status': 'success'})

#過去プロジェクトチーム編集
class TeamEditPastView(TemplateView):
    template_name = "team_edit_past.html"

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.objects.get(team_id=team_id)
        members = TeamMember.objects.filter(team=team)
        categories = Category.objects.filter(deletion_flag=False)
        project_id = request.GET.get('project_id')

        context = {
            'team': team,
            'members': members,
            'categories': categories,
            'project_id': project_id
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.objects.get(team_id=team_id)
        team_name = request.POST.get('team_name')
        team_memo = request.POST.get('team_memo')
        team_members = request.POST.get('team')
        if not team_members:
            team_members = []
        else:
            team_members = json.loads(team_members)
        print("team_memo:", team_memo)

        team.team_name = team_name
        team.memo = team_memo
        team.save()

        TeamMember.objects.filter(team=team).delete()
        for member_id in team_members:
            member = Member.objects.get(member_id=member_id)
            TeamMember.objects.create(
                team=team,
                member=member,
                creation_date=timezone.now(),
                update_date=timezone.now()
            )

        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        project_id = request.POST.get('project_id')
        return HttpResponseRedirect(f"{reverse('canri_app:team_edit_past_complete', kwargs={'project_id': project_id})}?project_name={project_name}&project_description={project_description}&start_date={start_date}&end_date={end_date}&teams={teams}&team_members={team_members}")
#過去プロジェクトチーム編集完了
class TeamEditPastCompleteView(TemplateView):
    template_name = "past_project_view.html"

    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        response = get_p_project_detail(request, project_id)
        project_data = json.loads(response.content).get('project_data')

        if not project_data:
            return HttpResponseNotFound("Project not found")

        # project_idに当てはまるProjectAffiliationTeamテーブルのデータを取得
        affiliation_teams = ProjectAffiliationTeam.objects.filter(project_id=project_id)
        teams = Team.objects.filter(team_id__in=[team.team.team_id for team in affiliation_teams])

        context = {
            'project': project_data,
            'teams': teams
        }

        return render(request, self.template_name, context)
#過去プロジェクトチームメンバー編集
class TeamMemberEditPastView(TemplateView):
    template_name = "team_edit_past.html"

    def get(self, request, *args, **kwargs):
        member_id = kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)

        team_id = request.GET.get('team_id')
        team_name = request.GET.get('team_name')
        team_memo = request.GET.get('team_memo')
        team_members = request.GET.get('team_members')

        # APIエンドポイントを呼び出してメンバー情報を取得
        response = get_member_data(request, member_id)
        member_info = json.loads(response.content).get('member_data')

        context = {
            'member': member_info,
            'team_id': team_id,
            'team_name': team_name,
            'team_memo': team_memo,
            'team_members': team_members,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        member_id = kwargs.get('member_id')
        member = Member.objects.get(member_id=member_id)
        member_name = request.POST.get('member_name')
        member_memo = request.POST.get('member_memo')

        member.name = member_name
        member.memo = member_memo
        member.save()

        return JsonResponse({'status': 'success'})
#過去プロジェクトチームメンバー編集保存
class TeamMemberEditSavePastView(TemplateView):
    template_name = "team_edit_past.html"

    def post(self, request, *args, **kwargs):
        member_id = request.POST.get('member_id')
        member = Member.objects.get(member_id=member_id)
        member_name = request.POST.get('member_name')
        member_memo = request.POST.get('member_memo')

        member.name = member_name
        member.memo = member_memo
        member.save()

        return JsonResponse({'status': 'success'})
    
class DeletePastProjectView(TemplateView):
    template_name = "delete_past_project.html"

# エラー画面を表示するためのビュー
def trigger_error(request):
    raise Exception("Intentional 500 Error")

class errorhtmlView(TemplateView):
    template_name = "500.html"