from django.db.models import Count, Q ,Sum, F ,Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Inventory 


@api_view(['GET'])
def data_quality_metrics(request):
    total_records = Inventory.objects.count()

    # Missing Values (null entries)
    missing_values = {
        "missing_customer_name": Inventory.objects.filter(customer_name__isnull=True).count(),
        "missing_product_name": Inventory.objects.filter(product_name__isnull=True).count(),
        "missing_region": Inventory.objects.filter(region__isnull=True).count(),
    }

    # Duplicates
    duplicate_customers = Inventory.objects.values('customer_id')\
        .annotate(count=Count('id')).filter(count__gt=1).count()

    # Uniqueness
    unique_products = Inventory.objects.values('product_id').distinct().count()

    # Data Quality Index (just a sample formula, tweak it based on your needs)
    dq_index = round(100 - ((sum(missing_values.values()) + duplicate_customers) / total_records) * 100, 2)

    return Response({
        "total_records": total_records,
        "missing_values": missing_values,
        "duplicate_customers": duplicate_customers,
        "unique_products": unique_products,
        "data_quality_index": dq_index,
    })

@api_view(['GET'])
def sales_metrics(request):
    # Revenue by Region
    sales_by_region = Inventory.objects.values('region')\
        .annotate(total_sales=Sum('sales_amount')).order_by('-total_sales')

    # Top Sales Reps
    top_sales_reps = Inventory.objects.values('sales_rep_id')\
        .annotate(total_sales=Sum('sales_amount')).order_by('-total_sales')[:5]

    # Example sales target achievement (set manual target, adjust as needed)
    sales_target = 100000  # Example target for sales reps
    target_achievement = [
        {
            "sales_rep_id": rep["sales_rep_id"],
            "sales": rep["total_sales"],
            "target": sales_target,
            "achievement": round(rep["total_sales"] / sales_target * 100, 2)
        }
        for rep in top_sales_reps
    ]

    return Response({
        "sales_by_region": list(sales_by_region),
        "top_sales_reps": list(top_sales_reps),
        "target_achievement": target_achievement,
    })

@api_view(['GET'])
def inventory_metrics(request):
    # Slow Movers (items with low quantity)
    slow_movers = Inventory.objects.filter(quantity__lt=20).count()

    # Fast Movers (items with high quantity)
    fast_movers = Inventory.objects.filter(quantity__gt=80).count()

    # Near Expiry Items (products near expiry)
    near_expiry = Inventory.objects.filter(days_to_expiry__lt=30).count()

    # Stock Turns (average stock turnover rate)
    stock_turns = Inventory.objects.aggregate(avg_turns=Avg('inventory_before'))['avg_turns']

    return Response({
        "slow_movers": slow_movers,
        "fast_movers": fast_movers,
        "near_expiry": near_expiry,
        "stock_turns": stock_turns,
    })


@api_view(['GET'])
def demand_forecast_metrics(request):
    # Demand by Product
    demand_by_product = Inventory.objects.values('product_name')\
        .annotate(demand=Sum('quantity')).order_by('-demand')

    # Forecast Gap (if lead_time > 30 days)
    forecast_gap = Inventory.objects.filter(lead_time__gt=30)\
        .values('product_name')\
        .annotate(gap=Sum('lead_time'))

    return Response({
        "demand_by_product": list(demand_by_product[:10]),  # Top 10 demanded products
        "forecast_gap": list(forecast_gap),
    })



from django.db.models import Avg, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Inventory

@api_view(['GET'])
def stock_replenishment_metrics(request):
    # Low Inventory Items (inventory_after < reorder_quantity)
    low_inventory_items = Inventory.objects.filter(inventory_after__lt=F('reorder_quantity'))\
        .values('product_name', 'inventory_after', 'reorder_quantity')

    # Average Lead Time (in days)
    avg_lead_time = Inventory.objects.aggregate(avg_lead_time=Avg('lead_time'))['avg_lead_time']

    # Total reorder volume (sum of reorder quantities for low stock items)
    total_reorder_volume = low_inventory_items.aggregate(total_reorder=Sum('reorder_quantity'))['total_reorder']

    return Response({
        "low_inventory_items": list(low_inventory_items),
        "avg_lead_time": avg_lead_time,
        "total_reorder_volume": total_reorder_volume,
    })
