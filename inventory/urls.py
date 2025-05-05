from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard/customer-data-quality/', views.data_quality_metrics, name='customer-data-quality'),
    path('api/dashboard/sales/', views.sales_metrics, name='sales-metrics'),
    path('api/dashboard/inventory/', views.inventory_metrics, name='inventory-metrics'),
    path('api/dashboard/demand-forecast/', views.demand_forecast_metrics, name='demand-forecast'),
    path('api/dashboard/stock-replenishment/', views.stock_replenishment_metrics, name='stock-replenishment'),
]
