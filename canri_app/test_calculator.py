import unittest
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta 
from .models import (
    Category, Project, Team, ProjectAffiliationTeam, MBTI,
    JobTitleInformation, Member, TeamMember, MemberList, CareerInformation,
    MemberCareer, Credentials, MemberHoldingQualification, ProjectProgressStatus,
    Feedback, MemberParameter
)

class TestModels(TestCase):

    # def test_create_category(self):
    #     category = Category.objects.create(
    #         category_name='Test Category',
    #         detail='This is a test category.',
    #         creation_date=timezone.now()
    #     )
    #     self.assertEqual(Category.objects.count(), 1)
    #     self.assertEqual(category.category_name, 'Test Category')

    # def test_create_project(self):
    #     project = Project.objects.create(
    #         project_name='Test Project',
    #         project_detail='This is a test project.',
    #         project_start_date='2025-01-01',
    #         project_end_date='2025-12-31',
    #         creation_date=timezone.now()
    #     )
    #     self.assertEqual(Project.objects.count(), 1)
    #     self.assertEqual(project.project_name, 'Test Project')

    # def test_create_team(self):
    #     team = Team.objects.create(
    #         team_name='Test Team',
    #         count=5,
    #         objective='Achieve test objectives.',
    #         creation_date=timezone.now()
    #     )
    #     self.assertEqual(Team.objects.count(), 1)
    #     self.assertEqual(team.team_name, 'Test Team')

    # def test_create_mbti(self):
    #     mbti = MBTI.objects.create(
    #         mbti_name='INTJ',
    #         planning_presentation_power=8,
    #         teamwork=6,
    #         time_management_ability=7,
    #         problem_solving_ability=9
    #     )
    #     self.assertEqual(MBTI.objects.count(), 1)
    #     self.assertEqual(mbti.mbti_name, 'INTJ')

    # def test_create_job_title_information(self):
    #     job_title = JobTitleInformation.objects.create(
    #         job_title='Software Engineer',
    #         speciality_height=10,
    #         planning_presentation_power=8,
    #         teamwork=9,
    #         time_management_ability=7,
    #         problem_solving_ability=8
    #     )
    #     self.assertEqual(JobTitleInformation.objects.count(), 1)
    #     self.assertEqual(job_title.job_title, 'Software Engineer')

    # def test_create_member(self):
    #     job_title = JobTitleInformation.objects.create(
    #         job_title='Manager',
    #         speciality_height=10,
    #         planning_presentation_power=8,
    #         teamwork=9,
    #         time_management_ability=8,
    #         problem_solving_ability=9
    #     )
    #     mbti = MBTI.objects.create(
    #         mbti_name='INFJ',
    #         planning_presentation_power=7,
    #         teamwork=8,
    #         time_management_ability=6,
    #         problem_solving_ability=7
    #     )
    #     member = Member.objects.create(
    #         name='John Doe',
    #         birthdate='1990-01-01',
    #         job=job_title,
    #         memo='Test memo for John Doe.',
    #         mbti=mbti,
    #         creation_date=timezone.now()
    #     )
    #     self.assertEqual(Member.objects.count(), 1)
    #     self.assertEqual(member.name, 'John Doe')

    # def test_create_team_member(self):
    #     team = Team.objects.create(
    #         team_name='Development Team',
    #         count=5,
    #         creation_date=timezone.now()
    #     )
    #     job_title = JobTitleInformation.objects.create(
    #         job_title='Developer',
    #         speciality_height=8,
    #         planning_presentation_power=7,
    #         teamwork=8,
    #         time_management_ability=6,
    #         problem_solving_ability=7
    #     )
    #     mbti = MBTI.objects.create(
    #         mbti_name='ENTP',
    #         planning_presentation_power=7,
    #         teamwork=8,
    #         time_management_ability=6,
    #         problem_solving_ability=7
    #     )
    #     member = Member.objects.create(
    #         name='Jane Doe',
    #         birthdate='1995-05-15',
    #         job=job_title,
    #         memo='Test memo for Jane Doe.',
    #         mbti=mbti,
    #         creation_date=timezone.now()
    #     )
    #     team_member = TeamMember.objects.create(
    #         team=team,
    #         member=member,
    #         creation_date=timezone.now(),
    #         update_date=timezone.now()
    #     )
    #     self.assertEqual(TeamMember.objects.count(), 1)
    #     self.assertEqual(team_member.team.team_name, 'Development Team')
    #     self.assertEqual(team_member.member.name, 'Jane Doe')

    # def test_view_500_error(self):
    #     """
    #     500エラーを検出するテスト
    #     """
    #     # 意図的にエラーを発生させる
    #     response = self.client.get('/non_existent_view/')  # 存在しないURLを指定
    #     self.assertEqual(response.status_code, 500)  # ステータスコードが500であることを確認


    def setUp(self):
        self.category = Category.objects.create(
            category_name='Test Category',
            detail='This is a test category.',
            creation_date=timezone.now(),
            update_date=timezone.now(),
            deletion_flag=False
        )

    def test_category_creation(self):
        self.assertEqual(self.category.category_name, 'Test Category')
        self.assertEqual(self.category.detail, 'This is a test category.')
        self.assertFalse(self.category.deletion_flag)

    def test_category_string_representation(self):
        self.assertEqual(str(self.category), self.category.category_name)

    def test_category_update(self):
        self.category.category_name = 'Updated Test Category'
        self.category.save()
        self.assertEqual(self.category.category_name, 'Updated Test Category')

    def test_category_soft_deletion(self):
        self.category.deletion_flag = True
        self.category.save()
        self.assertTrue(self.category.deletion_flag)
        
    def test_mbti_defaults(self):
        # デフォルト値のテスト
        new_mbti = MBTI.objects.create(mbti_name='ENTP')
        self.assertEqual(new_mbti.planning_presentation_power, 0)
        self.assertEqual(new_mbti.teamwork, 0)
        self.assertEqual(new_mbti.time_management_ability, 0)
        self.assertEqual(new_mbti.problem_solving_ability, 0)
   
    def test_mbti_creation(self):
        mbti = MBTI.objects.create(
            mbti_name="INTJ",
            planning_presentation_power=8,
            teamwork=6,
            time_management_ability=7,
            problem_solving_ability=9
        )
        self.assertEqual(mbti.mbti_name, "INTJ")
        self.assertEqual(mbti.planning_presentation_power, 8)
        self.assertEqual(mbti.teamwork, 6)
        self.assertEqual(mbti.time_management_ability, 7)
        self.assertEqual(mbti.problem_solving_ability, 9)


class JobTitleInformationTestCase(TestCase):
    def setUp(self):
        JobTitleInformation.objects.create(
            job_title="ソフトウェアエンジニア",
            speciality_height=5,
            planning_presentation_power=8,
            teamwork=7,
            time_management_ability=6,
            problem_solving_ability=9
        )

    def test_job_title_information(self):
        job_title_info = JobTitleInformation.objects.get(job_title="ソフトウェアエンジニア")
        self.assertEqual(job_title_info.speciality_height, 5)
        self.assertEqual(job_title_info.planning_presentation_power, 8)
        self.assertEqual(job_title_info.teamwork, 7)
        self.assertEqual(job_title_info.time_management_ability, 6)
        self.assertEqual(job_title_info.problem_solving_ability, 9)


class TeamMemberTestCase(TestCase):
    def test_team_member_creation(self):
        self.assertEqual(self.team_member.team, self.team)
        self.assertEqual(self.team_member.member, self.member)
        self.assertEqual(self.team_member.deletion_flag, False)
        self.assertIsNotNone(self.team_member.creation_date)
        self.assertIsNotNone(self.team_member.update_date)
        
    def test_team_member_string_representation(self):
        self.assertEqual(str(self.team_member), str(self.team_member.team_member_id))
        
    def test_team_member_soft_deletion(self):
        self.team_member.deletion_flag = True
        self.team_member.deletion_date = timezone.now()
        self.team_member.save()
        self.assertTrue(self.team_member.deletion_flag)
        self.assertIsNotNone(self.team_member.deletion_date)

if __name__ == "__main__":
    unittest.main()
