from django.db import models
from django.core.validators import FileExtensionValidator

class CardDetails(models.Model):
    card_number = models.CharField(max_length=19)
    expiry_date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=3)

    def __str__(self):
        return f"Card ending in {self.card_number[-4:]}"

