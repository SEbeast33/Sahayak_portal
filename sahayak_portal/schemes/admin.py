from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Scheme

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'state', 'category', 'url', 'created_at')
    search_fields = ('title', 'description', 'state', 'category')
    list_filter = ('language', 'state', 'category')
