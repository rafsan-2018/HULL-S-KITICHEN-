# Generated by Django 5.0.4 on 2024-04-17 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="encrypted_pwd",
            field=models.CharField(
                default="", max_length=2000, verbose_name="Encrypted Password"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="name",
            field=models.CharField(max_length=150, verbose_name="Name"),
        ),
    ]
