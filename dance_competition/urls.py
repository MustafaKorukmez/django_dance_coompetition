from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('competitions.urls')),  # competitions uygulamasının urls'ini dahil ediyoruz
]
