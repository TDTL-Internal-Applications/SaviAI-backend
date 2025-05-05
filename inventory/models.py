# models.py

from django.db import models
 
class Inventory(models.Model):

    transaction_id = models.CharField(max_length=50, unique=True)

    date = models.DateField()

    customer_id = models.CharField(max_length=50)

    customer_name = models.CharField(max_length=100)

    customer_segment = models.CharField(max_length=50)

    region = models.CharField(max_length=50)

    warehouse_id = models.CharField(max_length=50)

    sales_rep_id = models.CharField(max_length=50)

    product_id = models.CharField(max_length=50)

    product_name = models.CharField(max_length=100)

    product_category = models.CharField(max_length=50)

    quantity = models.IntegerField()

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    discount = models.DecimalField(max_digits=5, decimal_places=2)

    sales_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=50)

    lead_time = models.IntegerField(help_text="Days to deliver")

    reorder_quantity = models.IntegerField()

    inventory_before = models.IntegerField()

    inventory_after = models.IntegerField()

    days_to_expiry = models.IntegerField()
 
    def __str__(self):

        return f"{self.transaction_id} - {self.product_name}"

 