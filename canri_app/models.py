from django.db import models

class User(models.Model):
    user_id=models.CharField(primary_key=True,max_length=20)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True)
    deletion_flag = models.BooleanField(default=False)
    administrator_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'user'  # テーブル名を指定

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    detail = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'category'  # テーブル名を指定

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    project_detail = models.TextField(null=True, blank=True)
    project_start_date = models.DateTimeField()
    project_end_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    post_evaluation_memo = models.TextField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)
    complete_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'project'  # テーブル名を指定

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=255)
    count = models.IntegerField(null=True, blank=True)
    objective = models.TextField(null=True, blank=True)
    memo = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'team'  # テーブル名を指定

class ProjectAffiliationTeam(models.Model):
    project_affiliation_team_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    deletion_flag = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    change_date = models.DateTimeField(auto_now=True)
    deletion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'project_affiliation_team'  # テーブル名を指定

class TeamMember(models.Model):
    team_member_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deletion_flag = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    deletion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'team_member'  # テーブル名を指定

class MBTI(models.Model):
    mbti_id = models.AutoField(primary_key=True)
    mbti_name = models.CharField(max_length=255)
    planning_presentation_power = models.TextField()
    teamwork = models.TextField()
    time_management_ability = models.TextField()
    problem_solving_ability = models.TextField()

    class Meta:
        db_table = 'mbti'  # テーブル名を指定

class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    birthdate = models.DateTimeField()
    job_title = models.CharField(max_length=255)
    memo = models.TextField()
    mbti = models.ForeignKey(MBTI, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'member'  # テーブル名を指定

class MemberList(models.Model):
    member_list_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    memo = models.TextField()
    mbti = models.ForeignKey(MBTI, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'member_list'  # テーブル名を指定
