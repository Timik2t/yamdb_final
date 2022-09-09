from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comments, Genre, Review, Title, User


admin.site.register(Category)
admin.site.register(Comments)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Title)
admin.site.register(User, UserAdmin)
