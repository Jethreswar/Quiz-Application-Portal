# Generated by Django 4.2.7 on 2023-12-02 22:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quiz_generator", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Questions",
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
                ("question", models.CharField(max_length=255)),
                ("option1", models.CharField(max_length=50)),
                ("option2", models.CharField(max_length=50)),
                ("option3", models.CharField(max_length=50)),
                ("option4", models.CharField(max_length=50)),
                ("correct_answer", models.CharField(max_length=50)),
                ("course", models.JSONField(max_length=20)),
            ],
        ),
    ]
