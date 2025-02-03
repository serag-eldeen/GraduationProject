# Generated by Django 5.1.3 on 2025-02-01 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_signup_country_signup_date_of_birth_signup_gender_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='signup',
            name='token_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='signup',
            name='verification_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='signup',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=10, null=True),
        ),
    ]
