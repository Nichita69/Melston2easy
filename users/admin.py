from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User  # Импортируйте вашу модель

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'full_name', 'data', 'is_subscribed', 'phone', 'person')  # Определяем, какие поля отображать в списке
    search_fields = ('chat_id', 'full_name', 'phone', 'person')  # Добавляем поиск по указанным полям
    list_filter = ('is_subscribed', 'data')  # Добавляем фильтры
