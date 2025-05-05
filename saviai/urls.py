
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include ('users.urls')),
    path('transactions/',include('inventory.urls')),
     path('', include('data_analysis_api.urls')),
]
