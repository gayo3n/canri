# Generated by Django 5.1.3 on 2024-11-26 01:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_user_is_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="user_id",
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]