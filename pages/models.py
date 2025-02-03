from django.db import models

class Signup(models.Model):
    ROLE_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    COUNTRY_CHOICES = [
        ('EG', 'Egypt'),
        ('US', 'United States'),
        ('UK', 'United Kingdom'),
        ('IN', 'India'),
        ('FR', 'France'),
        # Add more countries as needed
    ]
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    verification_token = models.CharField(max_length=255, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False) 
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, default='EG')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='free')
    agreed_to_terms = models.BooleanField(default=False)
