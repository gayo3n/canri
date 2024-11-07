from django.contrib import admin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):

    list_display = ('id', 'password', 'name')
    list_display_links =  ('id', 'password', 'name')


admin.site.register(CustomUser, CustomUserAdmin)