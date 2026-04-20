
from django.contrib import admin
from .models import Plot

@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'is_approved')
    list_editable = ('is_approved',)