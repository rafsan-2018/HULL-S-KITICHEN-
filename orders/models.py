from django.db import models
from django.conf import settings
from django.utils import timezone

import random
import string

from django.db import models
from django.conf import settings
from django.utils import timezone


class Menu(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True)

    def __str__(self):
        return f"{self.name} - {self.price}"

    class Meta:
        ordering = ['name']
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    order_code = models.CharField(max_length=10, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.email} on {self.order_date}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = generate_id()
        # Calculate the total amount based on the sum of order items
        # total_price = self.order_items.through.objects.filter(
        #     order=self).aggregate(total=models.Sum('total_price'))['total']
        # total_price = sum(item.total_price for item in self.order_items.all())
        # self.total_amount = total_price or 0
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(
        Menu, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for {self.user.name}"

    def save(self, *args, **kwargs):
        # Calculate the total price for this order item
        self.total_price = self.quantity * self.menu_item.price
        super().save(*args, **kwargs)


def generate_id():
    # Generate 5 random numbers
    random_numbers = ''.join(random.choices(string.digits, k=5))
    
    # Generate 2 random letters
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    
    # Concatenate the components to form the ID
    id_number = f"ID{random_numbers}{random_letters}"
    
    return id_number