from django.contrib import admin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):

    list_display = ('id', 'password')
    list_display_links =  ('id', 'password')


admin.site.register(CustomUser, CustomUserAdmin)