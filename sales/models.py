from __future__ import annotations

from typing import Any
import uuid
from django.db import models
from django_utz.decorators import model
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money
from django.core.exceptions import ValidationError


@model
class Sale(models.Model):
    """Model for a product sale."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="sales"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="sales"
    )
    quantity = models.PositiveIntegerField()
    made_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ("-made_at",)

    class UTZMeta:
        datetime_fields = ["made_at", "updated_at"]


    @property
    def revenue(self) -> Money:
        """Returns the total amount made from the sale."""
        return self.quantity * self.product.price

    @property
    def currency(self) -> str:
        """Returns the currency used to make the sale."""
        return self.amount.currency

    
    def __str__(self) -> str:
        return f"{self.store.name} - {self.product.name} - {self.quantity} - {self.revenue}"


    def __add__(self, other: Sale) -> Sale:
        """Add two sales together."""
        if self.product != other.product:
            raise ValueError("Cannot add sales of different products")
        return Sale(
            store=self.store,
            product=self.product,
            quantity=self.quantity + other.quantity,
        )
    
    __iadd__ = __add__
    __radd__ = __add__
    

    def __sub__(self, other: Sale) -> Sale:
        """Subtract two sales."""
        if self.product != other.product:
            raise ValueError("Cannot subtract sales of different products")
        return Sale(
            store=self.store,
            product=self.product,
            quantity=self.quantity - other.quantity,
        )
    
    __isub__ = __sub__
    __rsub__ = __sub__


    def save(self, *args: str, **kwargs: Any) -> None:
        """Save the sale."""
        if self.quantity == 0:
            raise ValidationError("Sale quantity cannot be zero")
        if self.quantity > self.product.quantity:
            raise ValidationError(f"Sale quantity cannot be greater than available product quantity ({self.product.quantity})")
        
        self.product.quantity -= self.quantity
        # Save the sale first before saving the product. This is to avoid reducing the product quantity
        # without a corresponding sale.
        super().save(*args, **kwargs)
        self.product.save()

    
    def delete(self, *args: str, **kwargs: Any) -> None:
        """Delete the sale."""
        self.product.quantity += self.quantity
        super().delete(*args, **kwargs)
        self.product.save()


    @classmethod
    def get_total_revenue(cls, currency, **filter) -> Money:
        """
        Returns the total revenue made from all sales based on the filter.

        :param currency: Currency to get the revenue in.
        :param filter: Filter to apply to the sales.
        """
        return sum(
            map(lambda sale: convert_money(sale.revenue, currency), cls.objects.filter(**filter))
        ) or Money(0, currency)


    @classmethod
    def get_count(cls, **filters) -> int:
        """
        Returns the number of sales based on the filter.

        :param filter: Filter to apply to the sales.
        """
        return cls.objects.filter(**filters).count()
