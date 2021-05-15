# Generated by Django 3.1.6 on 2021-05-14 22:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModerationStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('result', models.CharField(choices=[('M', 'Moderating'), ('A', 'Approved'), ('D', 'Denied')], default='M', max_length=2)),
                ('denial_detail', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PostDenialReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(10)])),
            ],
        ),
    ]
