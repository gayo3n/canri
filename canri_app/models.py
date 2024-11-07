from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)  # VARCHAR(100)
    password = models.CharField(max_length=255)  # VARCHAR(255)
    creation_date = models.DateTimeField(auto_now_add=True)  # DATETIME
    deletion_date = models.DateTimeField(null=True, blank=True)  # DATETIME
    update_date = models.DateTimeField(auto_now=True)  # DATETIME
    deletion_flag = models.BooleanField(default=False)  # BOOLEAN
    administrator_flag = models.BooleanField(default=False)  # BOOLEAN
    user_id = models.AutoField(primary_key=True)  # INTEGER PRIMARY KEY AUTOINCREMENT

    class Meta:
        db_table = 'User'  # テーブル名を指定
