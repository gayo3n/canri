from django.test import TestCase
from django.utils import timezone
from .models import User


class TestUserModel(TestCase):
    def setUp(self):
        """
        テスト用データの作成
        """
        self.user = User.objects.create(
            user_id="USR1234567",
            name="TestUser",
            password="password123",  # ハッシュ化は省略
            is_active=True,
            is_staff=False,
            is_superuser=False,
            administrator_flag=False,
            deletion_flag=False,
            creation_date=timezone.now(),
        )

    # def test_create_user_success(self):
    #     """
    #     正常に User を作成するケース
    #     """
    #     self.assertEqual(User.objects.count(), 1)
    #     self.assertEqual(self.user.name, "TestUser")
    #     self.assertTrue(self.user.is_active)

    # def test_create_user_with_duplicate_name(self):
    #     """
    #     name が重複している場合にエラーを検出
    #     """
    #     with self.assertRaises(Exception):
    #         User.objects.create(
    #             user_id="USR7654321",
    #             name="TestUser",  # 重複名
    #             password="password456",
    #             is_active=True,
    #         )
            # 名前の重複ではエラー起きない

    # def test_update_user_success(self):
    #     """
    #     User のデータを正常に更新するケース
    #     """
    #     self.user.name = "UpdatedUser"
    #     self.user.save()
    #     updated_user = User.objects.get(user_id="USR1234567")
    #     self.assertEqual(updated_user.name, "UpdatedUser")

    # def test_delete_user_logically(self):
    #     """
    #     User を論理削除するケース
    #     """
    #     self.user.delete()
    #     deleted_user = User.objects.get(user_id="USR1234567")
    #     self.assertTrue(deleted_user.deletion_flag)
    #     self.assertIsNotNone(deleted_user.deletion_date)

    def test_create_user_with_short_name(self):
        """
        name の長さが不十分な場合にエラーを検出
        """
        with self.assertRaises(ValueError):
            User.objects.create(
                user_id="USR5432109",
                name="Us",  # 短すぎる名前
                password="password789",
            )

    # def test_create_user_with_invalid_password(self):
    #     """
    #     password の要件を満たしていない場合にエラーを検出
    #     """
    #     with self.assertRaises(ValueError):
    #         User.objects.create(
    #             user_id="USR0987654",
    #             name="AnotherUser",
    #             password="123",  # 短すぎるパスワード
    #         )

if __name__ == "__main__":
    import unittest
    unittest.main()
