from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'last_login')
    search_fields = ('email', 'name')
    ordering = ('-last_login',)


admin.site.register(CustomUser, CustomUserAdmin)
