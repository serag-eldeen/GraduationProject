from django.contrib import admin
from .models import CardDetails

@admin.register(CardDetails)
class CardDetailsAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'expiry_date')
    search_fields = ('card_number',)
