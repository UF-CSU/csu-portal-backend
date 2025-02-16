# Generated by Django 4.2.19 on 2025-02-16 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("clubs", "0015_teammembership_user_single_team_membership"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="club",
            options={
                "permissions": [
                    ("preview_club", "Can view a set of limited fields for a club.")
                ]
            },
        ),
        migrations.RemoveField(
            model_name="clubmembership",
            name="role",
        ),
        migrations.CreateModel(
            name="ClubRole",
            fields=[
                (
                    "group_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="auth.group",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "default",
                    models.BooleanField(
                        default=False,
                        help_text="New members would be automatically assigned this role.",
                    ),
                ),
                ("role_name", models.CharField(max_length=32)),
                (
                    "club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="clubs.club",
                    ),
                ),
            ],
            bases=("auth.group", models.Model),
        ),
        migrations.AddField(
            model_name="clubmembership",
            name="roles",
            field=models.ManyToManyField(to="clubs.clubrole"),
        ),
        migrations.AddConstraint(
            model_name="clubrole",
            constraint=models.UniqueConstraint(
                condition=models.Q(("default", True)),
                fields=("default",),
                name="only_one_default_club_role",
            ),
        ),
        migrations.AddConstraint(
            model_name="clubrole",
            constraint=models.UniqueConstraint(
                fields=("role_name", "club"), name="unique_rolename_per_club"
            ),
        ),
    ]
