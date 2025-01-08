from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        """
        指定された名前とパスワードで通常のユーザーを作成して返します。
        """
        # 名前が提供されていない場合はエラーを発生させる
        if not name:
            raise ValueError("名前フィールドは必須です")

        # ユーザーインスタンスを作成
        user = self.model(name=name, **extra_fields)

        # パスワードをハッシュ化して設定
        user.set_password(password)

        # データベースにユーザーを保存
        user.save(using=self._db)

        # 作成したユーザーを返す
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        """
        指定された名前とパスワードでスーパーユーザーを作成して返します。
        """
        # スタッフ権限をデフォルトでTrueに設定
        extra_fields.setdefault('is_staff', True)

        # スーパーユーザー権限をデフォルトでTrueに設定
        extra_fields.setdefault('is_superuser', True)

        # スーパーユーザーを作成して返す
        return self.create_user(name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)  # ユーザーがアクティブかどうかを示します
    is_staff = models.BooleanField(default=False)  # ユーザーが管理者権限を持っているかどうかを示します
    is_superuser = models.BooleanField(default=False)  # ユーザーがスーパーユーザー権限を持っているかどうかを示します

    creation_date = models.DateTimeField(auto_now_add=True)  # ユーザーが作成された日時
    deletion_date = models.DateTimeField(null=True, blank=True)  # ユーザーが削除された日時
    update_date = models.DateTimeField(auto_now=True)  # ユーザーが更新された日時
    deletion_flag = models.BooleanField(default=False)  # ユーザーが削除されたかどうかを示すフラグ
    administrator_flag = models.BooleanField(default=False)  # 追加の管理者権限を示すカスタムフラグ

    objects = UserManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'  # テーブル名を'user'に設定

    def __str__(self):
        return self.name