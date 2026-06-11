from django.db import models


class Carrier(models.Model):
    code = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=160)
    contact_phone = models.CharField(max_length=40, blank=True)
    service_level = models.CharField(max_length=80, default="standard")
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Shipment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ASSIGNED = "assigned"
    STATUS_PICKED_UP = "picked_up"
    STATUS_IN_TRANSIT = "in_transit"
    STATUS_DELIVERED = "delivered"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_PICKED_UP, "Picked up"),
        (STATUS_IN_TRANSIT, "In transit"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    order_id = models.PositiveIntegerField(unique=True)
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, related_name="shipments", null=True, blank=True)
    tracking_number = models.CharField(max_length=80, unique=True, blank=True)
    recipient_name = models.CharField(max_length=160)
    recipient_phone = models.CharField(max_length=40, blank=True)
    destination_address = models.CharField(max_length=255)
    destination_city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    estimated_delivery = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Shipment for order #{self.order_id}"


class RouteEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="route_events")
    status = models.CharField(max_length=20, choices=Shipment.STATUS_CHOICES)
    location = models.CharField(max_length=180, blank=True)
    note = models.TextField(blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["occurred_at"]

    def __str__(self):
        return f"{self.status} @ {self.location}"
