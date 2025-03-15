# Generated by Django 4.2.16 on 2024-09-28 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clubs", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="clubmembership",
            name="owner",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name="clubmembership",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("president", "President"),
                    ("officer", "Officer"),
                    ("member", "Member"),
                ],
                default="member",
            ),
        ),
        migrations.AddConstraint(
            model_name="clubmembership",
            constraint=models.UniqueConstraint(
                condition=models.Q(("owner", True)),
                fields=("club", "owner"),
                name="Only one club owner per club.",
            ),
        ),
    ]
