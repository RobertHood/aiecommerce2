from django.db import models


class Warehouse(models.Model):
    code = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=160)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class InventoryItem(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="inventory_items")
    product_id = models.PositiveIntegerField()
    sku = models.CharField(max_length=80)
    product_name = models.CharField(max_length=180)
    quantity_available = models.PositiveIntegerField(default=0)
    quantity_reserved = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sku", "warehouse__code"]
        constraints = [
            models.UniqueConstraint(fields=["warehouse", "sku"], name="unique_sku_per_warehouse"),
        ]

    def __str__(self):
        return f"{self.sku} @ {self.warehouse.code}"

    @property
    def quantity_total(self):
        return self.quantity_available + self.quantity_reserved

    @property
    def needs_reorder(self):
        return self.quantity_available <= self.reorder_level


class StockMovement(models.Model):
    TYPE_INBOUND = "inbound"
    TYPE_OUTBOUND = "outbound"
    TYPE_ADJUSTMENT = "adjustment"
    TYPE_RESERVE = "reserve"
    TYPE_RELEASE = "release"

    TYPE_CHOICES = [
        (TYPE_INBOUND, "Inbound"),
        (TYPE_OUTBOUND, "Outbound"),
        (TYPE_ADJUSTMENT, "Adjustment"),
        (TYPE_RESERVE, "Reserve"),
        (TYPE_RELEASE, "Release"),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movement_type} {self.quantity} for {self.inventory_item.sku}"
