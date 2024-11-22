# views.py
from django.shortcuts import render, redirect
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
from .api import create_team_api, save_team_api, save_project_api
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

#チーム追加１
class CreateTeamView(TemplateView):
    template_name = "create_team.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        # 入力された情報を保持した状態でcreate_team.htmlに遷移
        return render(request, self.template_name, {
            'project_name': project_name,
            'project_description': project_description,
            'start_date': start_date,
            'end_date': end_date,
            'teams': teams
        })

#チーム追加2
class CreateTeam2View(TemplateView):
    template_name = "create_team2.html"

    def post(self, request, *args, **kwargs):
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        teams = request.POST.get('teams')
        team_size = request.POST.get('team_size')
        team_type = request.POST.get('team_type')
        auto_generate = request.POST.get('auto_generate')
        categories = Category.objects.filter(deletion_flag=False)

        # teams をリストとして扱う
        if isinstance(teams, str):
            teams = json.loads(teams)

        if auto_generate:
            # 入力された情報を保持した状態でcreate_team2.htmlに遷移
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
        else:
            # 入力された情報を保持した状態でcreate_team3.htmlに遷移
            return render(request, 'create_team3.html', {
                'project_name': project_name,
                'project_description': project_description,
                'start_date': start_date,
                'end_date': end_date,
                'teams': teams,
                'team_type': team_type,
                'categories': categories,
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

        # チームを編成するためのデータを作成
        data = {
            'team_type': team_type,
            'members': selected_members,
            'team_size': team_size
        }

        # create_team_api を呼び出してチームを編成
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
        team_members = json.loads(request.POST.get('team'))

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

        return HttpResponseRedirect(f"{reverse('canri_app:team_edit_complete')}?project_name={project_name}&project_description={project_description}&start_date={start_date}&end_date={end_date}&teams={teams}")

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

#チームメンバー編集
class TeamMemberEditView(TemplateView):
    template_name = "team_member_edit.html"



#プロジェクトリスト
class ProjectlistView(TemplateView):
    template_name="projectlist.html"
class progress_within_ProjectlistView(TemplateView):
    template_name="progress_within_projectlist.html"


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



class post_ProjectlistView(TemplateView):
    template_name="post_projectlist.html"


def Post_projectListView(request):
    template_name = "post_projectlist.html"
    ctx = {}
    query = request.GET.get('p')
    qs = Project.objects.all()
    qs=qs.filter(complete_flag=1,deletion_flag=0)
    if query:
        qs = qs.filter(project_name__icontains=query)  # プロジェクト名でフィルタリング

    ctx["project_list"] = qs
    return render(request, template_name, ctx)




# プロジェクト詳細表示
class Project_detailView(TemplateView):
    template_name="project_detail.html"


from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectAffiliationTeam, ProjectProgressStatus

def project_detail_view(request, project_id):
    # プロジェクトを取得
    project = get_object_or_404(Project, project_id=project_id)

    # プロジェクトに関連するチームを取得
    teams = ProjectAffiliationTeam.objects.filter(project=project).select_related('team')

    # プロジェクトに関連するフェーズを取得
    phases = ProjectProgressStatus.objects.filter(project=project)

    context = {
        'project': project,
        'teams': teams,
        'phases': phases,
    }

    return render(request, 'project_detail.html', context)



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




