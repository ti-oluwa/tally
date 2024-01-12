from __future__ import annotations

from django.db import models
import uuid
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from django.utils.translation import gettext_lazy as _
from django_utz.models.mixins import UTZModelMixin


class ProductCategories(models.TextChoices):
    """Choices for product categories."""
    FASHION = "fashion", _("Fashion")
    ELECTRONICS = "electronics", _("Electronics")
    FOOD = "food", _("Food")
    BEAUTY = "beauty", _("Beauty")
    HEALTH = "health", _("Health")
    HOME = "home", _("Home")
    BOOKS = "books", _("Books")
    SPORTS = "sports", _("Sports")
    AUTOMOBILE = "automobile", _("Automobile")
    OTHERS = "others", _("Others")


class Product(UTZModelMixin, models.Model):
    """Model representing a product in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = MoneyField(
        max_digits=10, decimal_places=2, 
        default_currency="NGN", 
        validators=[MinMoneyValidator(0)]
    )
    quantity = models.IntegerField(default=0)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(_("Weight in grams"), max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=50, choices=ProductCategories.choices, default=ProductCategories.OTHERS)
    group = models.ForeignKey("ProductGroup", blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    brand = models.ForeignKey("ProductBrand", blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="products")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("added_at", "updated_at")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def __eq__(self, other: Product):
        return isinstance(other, self.__class__) and self.pk == other.pk
    


class ProductGroup(UTZModelMixin, models.Model):
    """Model representing a product group in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="product_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("created_at", "updated_at")

    class Meta:
        verbose_name = "Product Group"
        verbose_name_plural = "Product Groups"
        ordering = ["name"]

    def __str__(self):
        return self.name



class ProductBrand(UTZModelMixin, models.Model):
    """Model representing a product brand in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="product_brands")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("created_at", "updated_at")

    class Meta:
        verbose_name = "Product Brand"
        verbose_name_plural = "Product Brands"
        ordering = ["name"]

    def __str__(self):
        return self.name
