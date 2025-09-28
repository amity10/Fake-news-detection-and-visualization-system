# fakenewsapp/admin.py
from django.contrib import admin
from .models import NewsCheck, CustomUser, News, PasswordResetRequest

@admin.register(NewsCheck)
class NewsCheckAdmin(admin.ModelAdmin):
    list_display = (
        'news_title', 'user', 'prediction', 'probability', 
        'language', 'email_sent', 'email_to', 'date_checked', 'category'
    )
    list_filter = ('prediction', 'language', 'email_sent', 'category')
    search_fields = ('news_title', 'news_content', 'user__username', 'email_to')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_fake', 'language', 'created_at')
    list_filter = ('is_fake', 'language')
    search_fields = ('title', 'content')


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_at', 'processed', 'email_sent', 'admin_generated_password')
    list_filter = ('processed', 'email_sent')
    search_fields = ('user__username',)
