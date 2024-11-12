from django.contrib import admin

from .models import CustomUser


#Register your models here.


class CustomUserAdmin(admin.ModelAdmin):

    list_display = ('userid', 'password', 'username')
    list_display_links =  ('userid', 'password', 'username')

admin.site.register(CustomUser, CustomUserAdmin)