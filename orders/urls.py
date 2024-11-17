from django.urls import path
from . import views  

app_name = 'orders'

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.orders, name='orders'),
    # path('', views.order_code, name='order_code'),
    path('add_order/', views.add_order, name='add_order'),
    path('order-completed/', views.orderCompleted, name='order-completed'),
    path('order-completed-cash/', views.orderCashOrder, name='order-completed-cash'),
    path('order-canceled/', views.orderCanceled, name='order-canceled'),
]
