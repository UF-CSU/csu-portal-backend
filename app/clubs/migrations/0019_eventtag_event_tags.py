# Generated by Django 4.2.19 on 2025-03-06 17:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clubs", "0018_alter_clubmembership_roles"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        max_length=16,
                        validators=[django.core.validators.MinLengthValidator(2)],
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("red", "Red"),
                            ("orange", "Orange"),
                            ("yellow", "Yellow"),
                            ("green", "Green"),
                            ("blue", "Blue"),
                            ("purple", "Purple"),
                            ("grey", "Grey"),
                        ],
                        default="grey",
                    ),
                ),
                ("order", models.IntegerField(blank=True, default=0)),
            ],
            options={
                "ordering": ["order", "name"],
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="event",
            name="tags",
            field=models.ManyToManyField(blank=True, to="clubs.eventtag"),
        ),
    ]
