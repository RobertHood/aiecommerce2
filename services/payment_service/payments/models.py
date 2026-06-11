import uuid

from django.db import models


class Payment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCEEDED, "Succeeded"),
        (STATUS_FAILED, "Failed"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    METHOD_COD = "cod"
    METHOD_CARD = "card"
    METHOD_BANK_TRANSFER = "bank_transfer"

    METHOD_CHOICES = [
        (METHOD_COD, "Cash on delivery"),
        (METHOD_CARD, "Card"),
        (METHOD_BANK_TRANSFER, "Bank transfer"),
    ]

    order_id = models.PositiveIntegerField()
    customer_email = models.EmailField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    method = models.CharField(max_length=30, choices=METHOD_CHOICES, default=METHOD_COD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    transaction_id = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    provider_reference = models.CharField(max_length=120, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment #{self.id} for order #{self.order_id}"
