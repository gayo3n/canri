from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError("The Name field must be set")
        user = self.model(name=name, **extra_fields)
        user.set_password(password)  # パスワードをハッシュ化
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=10)

    is_active = models.BooleanField(default=True) #ログインしているかどうか
    is_staff = models.BooleanField(default=False)  # 管理者権限
    is_superuser = models.BooleanField(default=False)  # スーパーユーザー権限

    creation_date = models.DateTimeField(auto_now_add=True)
    deletion_date = models.DateTimeField(null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True)
    deletion_flag = models.BooleanField(default=False)
    administrator_flag = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'  # テーブル名を'user'に設定

    def __str__(self):
        return self.name

