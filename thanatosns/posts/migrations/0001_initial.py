# Generated by Django 4.2.2 on 2023-07-03 07:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "url",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("platform", models.CharField(max_length=255)),
                ("title", models.TextField()),
                ("body", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Media",
            fields=[
                (
                    "url",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("index", models.IntegerField()),
                (
                    "content_type",
                    models.CharField(
                        choices=[("IMAGE", "Image"), ("VIDEO", "Video")], max_length=63
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="posts.post"
                    ),
                ),
            ],
            options={
                "unique_together": {("url", "index")},
            },
        ),
    ]