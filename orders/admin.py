from django.contrib import admin
from .models import Menu, Order, OrderItem


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_date', 'total_amount')
    search_fields = ('user__email', 'user__name')
    list_filter = ('order_date', 'total_amount')
    ordering = ('-order_date',)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'quantity', 'total_price')
    search_fields = ('menu_item__name',)
    ordering = ('menu_item__name',)


admin.site.register(Menu, MenuAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
