from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid

def generate_unique_id():
    return str(uuid.uuid4())[:10]

class UserManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        """
        指定された名前とパスワードで通常のユーザーを作成して返します。
        """
        if not name:
            raise ValueError("名前フィールドは必須です")

        user = self.model(name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        """
        スーパーユーザー作成
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=10, primary_key=True, default=generate_unique_id)
    name = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    deletion_flag = models.BooleanField(default=False)
    deletion_date = models.DateTimeField(null=True, blank=True)
    administrator_flag = models.BooleanField(default=False)  # 追加

    objects = UserManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    def delete(self):
        """論理削除"""
        self.deletion_flag = True
        self.deletion_date = timezone.now()
        self.save()

    def restore(self):
        """削除の解除"""
        self.deletion_flag = False
        self.deletion_date = None
        self.save()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.name
