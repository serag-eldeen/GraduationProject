from django.db import models

class Signup(models.Model):
    ROLE_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]

    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='free')
    agreed_to_terms = models.BooleanField(default=False)
