from django.urls import path
from .views import DataAnalysisAPIView

urlpatterns = [
    path('api/analyze/', DataAnalysisAPIView.as_view(), name='data_analysis'),
] 