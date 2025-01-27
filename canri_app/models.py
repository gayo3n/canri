from django.db import models
from django.utils import timezone


# class Member (models.Model):

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    detail = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'Category'

    def __str__(self):
        return self.category_name


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    project_detail = models.TextField(null=True, blank=True)
    project_start_date = models.DateField()
    project_end_date = models.DateField()
    creation_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateField(null=True, blank=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    post_evaluation_memo = models.TextField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)
    complete_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'Project'


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=255)
    count = models.IntegerField(null=True, blank=True)
    objective = models.TextField(null=True, blank=True)
    memo = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True, blank=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'Team'


class ProjectAffiliationTeam(models.Model):
    project_affiliation_team_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    deletion_flag = models.BooleanField(default=False)
    creation_date = models.DateTimeField()
    change_date = models.DateTimeField(null=True, blank=True)
    deletion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Project_Affiliation_Team'

class MBTI(models.Model):
    mbti_id = models.AutoField(primary_key=True)
    mbti_name = models.CharField(max_length=255)
    planning_presentation_power = models.IntegerField(default=0)
    teamwork = models.IntegerField(default=0)
    time_management_ability = models.IntegerField(default=0)
    problem_solving_ability = models.IntegerField(default=0)

    class Meta:
        db_table = 'MBTI'

class JobTitleInformation(models.Model):
    job_title_id = models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=255)
    speciality_height = models.IntegerField()
    planning_presentation_power = models.IntegerField()
    teamwork = models.IntegerField()
    time_management_ability = models.IntegerField()
    problem_solving_ability = models.IntegerField()

    class Meta:
        db_table = 'job_title_information'

class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    birthdate = models.DateTimeField()
    job = models.ForeignKey(JobTitleInformation, on_delete=models.CASCADE)
    memo = models.TextField()
    mbti = models.ForeignKey(MBTI, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'Member'

class TeamMember(models.Model):
    team_member_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    deletion_flag = models.BooleanField(default=False)
    creation_date = models.DateTimeField()
    update_date = models.DateTimeField()
    deletion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Team_Member'



class MemberList(models.Model):
    member_list_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # job_title = models.CharField(max_length=255)
    # memo = models.TextField()
    # mbti = models.ForeignKey(MBTI, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'Member_List'


class CareerInformation(models.Model):
    career_id = models.AutoField(primary_key=True)
    career = models.CharField(max_length=255)
    speciality_height = models.IntegerField()


    class Meta:
        db_table = 'career_information'


class MemberCareer(models.Model):
    member_career_id = models.AutoField(primary_key=True)
    career = models.ForeignKey(CareerInformation, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()

    class Meta:
        db_table = 'member_career'


class Credentials(models.Model):
    qualification_id = models.AutoField(primary_key=True)
    qualification_name = models.CharField(max_length=255)
    speciality_height = models.CharField(max_length=255)

    class Meta:
        db_table = 'credentials'


class MemberHoldingQualification(models.Model):
    holding_qualification_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    qualification = models.ForeignKey(Credentials, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    deletion_date = models.DateTimeField(null=True, blank=True)
    deletion_flag = models.BooleanField(default=False)

    class Meta:
        db_table = 'member_holding_qualification'


class ProjectProgressStatus(models.Model):
    progress_status_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    phase_name = models.CharField(max_length=255)
    complete_flag = models.BooleanField(default=False)
    deletion_flag = models.BooleanField(default=False)
    expiration_date = models.DateField()
    creation_date = models.DateTimeField()
    complete_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'project_progress_status'


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    member1 = models.ForeignKey(Member, related_name='feedback_member1', on_delete=models.CASCADE)
    member2 = models.ForeignKey(Member, related_name='feedback_member2', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority_flag = models.BooleanField()
    deletion_flag = models.BooleanField()
    # expiration_date = models.DateTimeField(null=True, blank=True)
    creation_date = models.DateTimeField()
    deletion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'feedback'


class MemberParameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    planning_presentation_power = models.IntegerField()
    teamwork = models.IntegerField()
    time_management_ability = models.IntegerField()
    problem_solving_ability = models.IntegerField()
    speciality_height = models.FloatField()

    class Meta:
        db_table = 'member_parameter'


# class JobTitleInformation(models.Model):
#     job_title_id = models.AutoField(primary_key=True)
#     job_title = models.CharField(max_length=255)
#     speciality_height = models.IntegerField()
#     planning_presentation_power = models.IntegerField()
#     teamwork = models.IntegerField()
#     time_management_ability = models.IntegerField()
#     problem_solving_ability = models.IntegerField()

#     class Meta:
#         db_table = 'job_title_information'