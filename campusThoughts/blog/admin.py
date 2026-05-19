from django.contrib import admin
from .models import Post  # Make sure 'Post' is defined in models.py

# Register your models here.
admin.site.register(Post)