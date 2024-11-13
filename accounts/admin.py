from django.contrib import admin

from .models import User


# #Register your models here.

class CustomUserAdmin(admin.ModelAdmin):

    list_display = ('user_id', 'password', 'name')
    list_display_links =  ('user_id', 'password', 'name')

admin.site.register(User, CustomUserAdmin)
