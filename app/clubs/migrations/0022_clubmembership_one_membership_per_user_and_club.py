# Generated by Django 4.2.20 on 2025-03-15 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clubs", "0021_event_other_clubs"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="clubmembership",
            constraint=models.UniqueConstraint(
                fields=("club", "user"), name="one_membership_per_user_and_club"
            ),
        ),
    ]
