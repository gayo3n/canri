# Generated by Django 5.1.3 on 2024-11-11 04:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("canri_app", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="memberlist",
            name="member",
        ),
        migrations.AddField(
            model_name="memberlist",
            name="member",
            field=models.ManyToManyField(
                related_name="member_lists", to="canri_app.member"
            ),
        ),
    ]
