# Generated by Django 5.1.3 on 2025-02-02 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_signup_is_verified_signup_token_expiry_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
