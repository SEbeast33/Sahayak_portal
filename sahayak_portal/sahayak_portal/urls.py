# myscheme_clone/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('schemes.urls')),  # 👈 This includes the app's routes
]
