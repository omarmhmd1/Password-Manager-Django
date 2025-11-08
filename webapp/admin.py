from django.contrib import admin
from .models import Password

# Register your models here.

@admin.register(Password)
class PasswordAdmin(admin.ModelAdmin):
    '''Admin View for Password'''
    list_display = ('username', 'password', 'email', 'web_or_app', 'state', 'note', 'created_by')
    list_filter = ('created_by',)
    readonly_fields = ('password',)
