# Generated by Django 4.2.2 on 2023-07-04 06:43

import django.contrib.postgres.fields
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
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
                ("name", models.CharField(max_length=255)),
                (
                    "other_names",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "urls",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Post",
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
                ("url", models.CharField(max_length=255, unique=True)),
                ("platform", models.CharField(max_length=255)),
                ("title", models.TextField()),
                ("body", models.TextField()),
                ("published_at", models.DateTimeField()),
                ("authors", models.ManyToManyField(to="posts.author")),
            ],
        ),
        migrations.CreateModel(
            name="Media",
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
                ("url", models.CharField(max_length=255, unique=True)),
                ("index", models.PositiveIntegerField()),
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
        ),
        migrations.AddIndex(
            model_name="author",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["other_names"], name="posts_autho_other_n_605dcf_gin"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="media",
            unique_together={("url", "index")},
        ),
    ]
