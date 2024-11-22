# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import *
from .models import MemberList, Member, Feedback, MemberParameter, MemberCareer, JobTitleInformation, MemberHoldingQualification, Project,CareerInformation,MBTI,Credentials,Category
from django.utils import timezone
import json
from .forms import CSVUploadForm
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from .api import create_team_api, save_team_api, save_project_api, get_member_data, get_p_project_detail
from django.urls import reverse
import csv
from django.contrib import messages



# -----システムメニュー-----
class IndexView(TemplateView):
    template_name = "index.html"

# -----------ログインでセッション未設定だと思われるため、まだ機能してません--百----------

    def my_view(request):
        if request.user.is_authenticated:
            # ユーザーはログインしています
            template_name = "index.html"
            user_name = models.User.name
            return render(request, template_name, {"name" : user_name})
        else:
            # ユーザーはログインしていません
            return redirect('accounts:login/')


# -----メンバーリスト一覧-----
class MemberListView(TemplateView):
    template_name = "memberlist.html"

    def get(self, request, *args, **kwargs): 
        # カテゴリー一覧を取得
        categories = Category.objects.all()

        context = {
            "categories": categories  # カテゴリー
        }
        return render(request, self.template_name, context)


class NewProjectView(TemplateView):
    template_name = "create_new_project.html"




# -----メンバーリスト作成-----
class MemberListMakeView(TemplateView):
    template_name = "memberList_make.html"

    def get(self, request, *args, **kwargs):

        # フォームget
        form = CSVUploadForm()
        # メンバー検索(未入力の場合はすべて)
        members = self.get_queryset()

        # セッションから memberID_list を取得
        memberID_list = request.session.get('memberID_list', [])

        # `memberID_list` の各 `member_id` に対応する `member_name` を取得
        members_in_list = Member.objects.filter(member_id__in=memberID_list)

        # member_dict を作成する
        member_dict = {member.member_id: member.name for member in members_in_list}

        messages.error(request , '')

        context = {
            'form': form, # フォーム
            'members': members, # 検索メンバー
            'memberID_list': memberID_list,  # 現在のリストを表示
            'member_dict':member_dict,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
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

        # `memberID_list` の各 `member_id` に対応する `member_name` を取得
        members_in_list = Member.objects.filter(member_id__in=memberID_list)

        # member_dict を作成する
        member_dict = {member.member_id: member.name for member in members_in_list}

        members = self.get_queryset()
        context = {
            'members': members,
            'memberID_list': memberID_list,
            'member_dict': member_dict,  # member_dict を渡す
        }
        return render(request, self.template_name, context)


    # メンバー検索
    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            members = Member.objects.filter(name__icontains=query)
        else:
            # フォーム未入力の場合はすべて
            members = Member.objects.all()
        return members
    
    def upload_csv(request):
        if request.method == 'POST':
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                
                for row in reader:
                    # 各行のデータを処理する
                    print(row)
                
                # 成功した場合のレスポンス
                return render(request, 'upload_success.html')
        else:
            form = CSVUploadForm()

        return render(request, 'upload_csv.html', {'form': form})



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

        if member_list_name and member_list_details:

            # 新しいカテゴリを作成
            category = Category(
                category_name=member_list_name,
                detail=member_list_details,
                creation_date=timezone.now()
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
                    # MemberList オブジェクトを作成して保存
                    member_list = MemberList(
                        member_id=member.member_id,
                        category_id=category.category_id,
                        creation_date=timezone.now()
                    )
                    # メンバーリスト保存
                    member_list.save()
                    
                    # memberID_listを初期化
                    memberID_list = []
                    # セッションに保存
                    request.session['memberID_list'] = memberID_list
                except Member.DoesNotExist:
                    print(f"Member with ID {member_id} not found")

            # 成功したらメンバーリストページにリダイレクト
            return redirect(request, 'canri_app:memberlist_make_complete')

        else:
            # エラーメッセージを1回にまとめて表示
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect(reverse('canri_app:memberList_make'))


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
    
# -----CSVファイル処理-----
class FileUploadView(TemplateView):
    def upload_csv(request):
        if request.method == 'POST':
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                
                for row in reader:
                    # 各行のデータを処理する
                    print(row)
                
                # 成功した場合のレスポンス
                return render(request, 'upload_success.html')
        else:
            form = CSVUploadForm()

        return render(request, 'upload_csv.html', {'form': form})


# -----メンバー保存-----
class MemberMakeCompleteView(TemplateView):
    template_name = "member_make_complete.html"
    
    def post(self, request, *args, **kwargs):
        # フォームからの入力を取得
        name = request.POST.get('name')
        birthdate = request.POST.get('birthday')  # 日付は適切なフォーマットで受け取る
        job_title = request.POST.get('job_title')
        memo = request.POST.get('memo', '')  # メモは任意なのでデフォルト値を設定
        mbti_id = request.POST.get('MBTI')  # MBTI ID を取得

        # 入力検証
        if not name:
            messages.error(request, "名前を入力してください。")
            return redirect('canri_app:member_make')
        if not birthdate:
            messages.error(request, "生年月日を設定してください。")
            return redirect('canri_app:member_make')
        
        try:
            # Member オブジェクトを作成して保存
            member = Member(
                name=name,
                birthdate=birthdate,
                job_id=job_title.job_id,
                memo=memo,
                mbti=mbti_id,  # 外部キーとして関連付け
                creation_date=timezone.now(),  # 作成日を現在時刻に設定
                deletion_flag=False,  # 削除フラグは初期状態でFalse
            )
            member.save()
        except Exception as e:
            # 保存に失敗した場合の処理
            messages.error(request, f"An error occurred while saving the member: {e}")
            return redirect('canri_app:member_make')
        
        # 保存が成功した場合にmember_make_completeへ遷移
        return render(request, self.template_name, {"member": member})


class MemberMakeDeleteView(TemplateView):
    template_name = "member_make_delete.html"

class MemberListDeleteView(TemplateView):
    template_name = "memberlist_delete.html"

class MemberListDeleteOkView(TemplateView):
    template_name = "memberlist_delete_complete.html"

class MemberMakeDeleteOkView(TemplateView):
    template_name = "member_make_delete_complete.html"

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

        # 入力された情��を保持した状態でnew_project_edit.htmlに遷移
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

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # チームを編��するためのデータを作成
        data = {
            'team_type': team_type,
            'members': selected_members,
            'team_size': team_size
        }

        # create_team_api を呼び出し���チームを編成
        request._body = json.dumps(data).encode('utf-8')
        response = create_team_api(request)
        response_data = json.loads(response.content)

        if response.status_code == 200:
            team = response_data['team']
            print("チームが作成されました:", team)  # メンバー情報をターミナルに表示
        else:
            team = None
            print("チームの作成に失敗しました")  # エラーメッセージをターミナルに表示

        # 入力された情報を保持した状態でcreate_team3.htmlに遷移
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

        # デバッグ用にリクエストボディを表示
        print("リクエストボディ:", request.body)

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

        # ���力された情報を保持した状態でnew_project_edit.htmlに遷移
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
            print("プロジェクト��保存されました:", project_id)  # プロジェクトIDをターミナルに表示
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
class ProjectlistView(TemplateView):
    template_name="projectlist.html"
class progress_within_ProjectlistView(TemplateView):
    template_name="progress_within_projectlist.html"

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



# 過去プロジェクト
class post_ProjectlistView(TemplateView):
    template_name="post_projectlist.html"


# プロジェクト詳細表示
class Project_detailView(TemplateView):
    template_name="project_detail.html"


from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectAffiliationTeam, ProjectProgressStatus

#プロジェクト詳細表示時に利用
#project_idを使用してデータを取得
def project_detail_view(request, project_id):
    # プロジェクトを取得
    #project_idに当てはまるprojectテーブルのデータを取得
    project = get_object_or_404(Project, project_id=project_id)

    #プロジェクトに関連するチームを取得
    #プロジェクト所属チームテーブルのprojectに当てはまるデータを取得
    teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

    # プロジェクトに関連するフェーズを取得
    # 上と同じ感じ
    phases = ProjectProgressStatus.objects.filter(project=project)

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



# プロジェクト詳細変更モーダル保存時
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Project
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])
# プロジェクト詳細変更モーダル保存時
def project_detail_update(request, project_id):
    """
    プロジェクト詳細の更新処理を行うビュー関数

    Args:
        request (HttpRequest): HTTPリクエスト
        project_id (int): 更新対象のプロジェクトID

    Returns:
        HttpResponse: プロジェクト詳細ページまたはエラーメッセージを含むレンダリング結果
    """
    # テンプレート名の定義
    templatename = f"project_detail.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            project_name = request.POST.get('project_name')
            project_description = request.POST.get('project_description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # 必須項目の入力チェック
            if not all([project_name, project_description, start_date, end_date]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # 開始日と終了日の論理チェック
            if start_date > end_date:
                # 開始日が終了日より後の場合、エラーメッセージを表示して再表示
                messages.error(request, '開始日は終了日よりも前の日付である必要があります。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # プロジェクト情報の更新
            project.project_name = project_name
            project.project_detail = project_description
            project.project_start_date = start_date
            project.project_end_date = end_date

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
            teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases = ProjectProgressStatus.objects.filter(project=project)

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





        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return render(request, templatename, {
                'project': project,
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})







# フェーズ追加時
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Project
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])
# フェーズ追加
def project_phase_add(request, project_id):

    # テンプレート名の定義
    templatename = f"project_detail.html"

    # 指定されたIDのプロジェクトを取得（削除されていないプロジェクトのみ）
    project = get_object_or_404(Project, project_id=project_id, deletion_flag=False)

    if request.method == "POST":
        try:
            # POSTデータから各プロジェクト情報を取得
            project_name = request.POST.get('project_name')
            project_description = request.POST.get('project_description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            phase_name = request.POST.get('phase_name')
            end_date2 = request.POST.get('end_date2')

            # 必須項目の入力チェック
            if not all([project_name, project_description, start_date, end_date,phase_name,end_date2]):
                # 必須項目が未入力の場合、エラーメッセージを表示して再表示
                messages.error(request, '全ての必須項目を入力してください。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # 開始日と終了日の論理チェック
            if start_date > end_date:
                # 開始日が終了日より後の場合、エラーメッセージを表示して再表示
                messages.error(request, '開始日は終了日よりも前の日付である必要があります。')
                return render(request, templatename, {
                    'project': project,
                    'project_name': project_name,
                    'project_description': project_description,
                    'start_date': start_date,
                    'end_date': end_date,
                })

            # プロジェクト情報の更新
            project.project_name = project_name
            project.project_detail = project_description
            project.project_start_date = start_date
            project.project_end_date = end_date

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
            teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

            # プロジェクトに関連するフェーズを取得
            # 上と同じ感じ
            phases = ProjectProgressStatus.objects.filter(project=project)

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





        except Exception as e:
            # 予期しないエラーが発生した場合のエラーハンドリング
            messages.error(request, f'更新中にエラーが発生しました: {str(e)}')
            return render(request, templatename, {
                'project': project,
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
            })

    # GETリクエストの場合、プロジェクト詳細ページを表示
    return render(request, templatename, {'project': project})




# 進行中プロジェクト用のチーム追加用のビュー
class project_detail_Create_TeamView(TemplateView):
    template_name = "create_team.html"

    def post(self, request, *args, **kwargs):
        # POSTデータからプロジェクト情報を取得
        project_name = request.POST.get('project_name')  # プロジェクト名
        project_description = request.POST.get('project_description')  # プロジェクト説明
        start_date = request.POST.get('start_date')  # 開始日
        end_date = request.POST.get('end_date')  # 終了日

        # teams = request.POST.get('teams')  # チーム情報（JSON文字列）

        # チーム情報をリスト形式に変換
        # POSTデータでは文字列として受け取るため、JSON形式でパースする
        # if isinstance(teams, str):
        #     teams = json.loads(teams)

        # 入力された情報を保持したまま create_team.html テンプレートをレンダリング
        return render(request, self.template_name, {
            'project_name': project_name,  # プロジェクト名
            'project_description': project_description,  # プロジェクト説明
            'start_date': start_date,  # 開始日
            'end_date': end_date,  # 終了日
            # 'teams': teams  # チーム情報（リスト形式）
        })

class team_detailView(TemplateView):
    template_name="team_detail.html"
    

def team_detail_view(request, team_id):
    template_name = "post_projectlist.html"
    ctx = {}
    team = get_object_or_404(Project, team_id=team_id)
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=1,deletion_flag=0)
    if team:
        qs = qs.filter(project_id=team)

    ctx["team_detail"] = qs
    return render(request, template_name, ctx)

    # ctx["project_list"] = qsequest, self.template_name, {'members': members}

# 過去プロジェクトリスト
class Past_ProjectListView(TemplateView):
    template_name = "past_project_list.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get('p')
        qs = Project.objects.all()
        qs=qs.filter(complete_flag=1,deletion_flag=0)
        if query:
            qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

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
        qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

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

        context = {
            'project': project_data
        }
        return render(request, self.template_name, context)

class Past_ProjectDeletingView(TemplateView):
    template_name = "past_project_deleting_confirmation.html"

class Project_DeletedView(TemplateView):
    template_name = "project_deleted.html"

class Project_Save_CompleteView(TemplateView):
    template_name = "project_save_complete.html"

#フィードバックモーダル表示
class FeedbackView(TemplateView):
    template_name = "feedback_application.html"

    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        context = {
            'project_id': project_id
        }
        return render(request, self.template_name, context)

#フィードバック保存
class FeedbackSaveView(TemplateView):
    template_name = "feedback_save_complete.html"

    def post(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)
    # def post(self, request, *args, **kwargs):
    #     project_id = request.POST.get('project_id')
    #     feedback_content = request.POST.get('feedback')

    #     # デバッグ用に受け取った値を表示
    #     print("Received project_id:", project_id)
    #     print("Received feedback_content:", feedback_content)

    #     context = {
    #         'project_id': project_id,
    #         'feedback_content': feedback_content
    #     }
    #     return render(request, self.template_name, context)
