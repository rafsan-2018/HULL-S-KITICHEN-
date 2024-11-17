from .models import Menu, OrderItem
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import Menu, Order, OrderItem
from django.contrib import messages
from .models import Menu, Order
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.core.mail import send_mail
import json, requests, os
from .utils import *
from dotenv import load_dotenv
load_dotenv()

@login_required(login_url='/login/')
def orderCanceled(request):
    messages.warning(request, 'Your order has been canceled.')
    return render(request, 'orders/order-canceled.html')

@login_required(login_url='/login/')
def home(request):
    user = request.user
    items = Menu.objects.all()

    try:
        added_items = OrderItem.objects.filter(user=user)
        total_sum = sum(item.total_price for item in added_items)
        order = Order.objects.filter(user=user).first()
        order_code = order.order_code
        order.total_amount = total_sum
        order.save()
        item_list = [
            {
                "name": item.menu_item.name,
                "quantity": item.quantity,  # Assuming each item is added individually
                "price": str(item.menu_item.price),
                "currency": "GBP"
            }
            for item in added_items
        ]
        quantity = len(added_items)
    except:
        added_items = None
        total_sum = 0
        order = None
        order_code = ""
        item_list = []
        quantity = 0

    host = request.get_host()

    # Generate a unique invoice number
    invoice_number = str(uuid.uuid4())

    base_url = os.getenv('PAYPAL_BASE_URL')

    # Get OAuth token
    access_token = get_paypal_oauth_token()

    approval_url = None
    if quantity > 0:
        # Create payment only if there are items in the cart
        payment_data = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(total_sum),  # Convert to string
                    "currency": "GBP"
                },
                "description": "Purchase description",
                "invoice_number": invoice_number,  # Include the invoice number here
                "item_list": {
                    "items": item_list
                }
            }],
            "redirect_urls": {
                "return_url": f"http://{host}{reverse('orders:order-completed')}",
                "cancel_url": f"http://{host}{reverse('orders:order-canceled')}",
            }
        }

        payment_response = requests.post(
            f'{base_url}/payments/payment',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
            data=json.dumps(payment_data)
        )

        payment_response_data = payment_response.json()
        print(json.dumps(payment_response_data, indent=4))  # Debugging output

        if 'links' in payment_response_data:
            for link in payment_response_data['links']:
                if link['rel'] == 'approval_url':
                    approval_url = link['href']
                    break
        else:
            print("Error: 'links' not found in payment_response_data")

    context = {
        "order_code": order_code,
        'items': items,
        'added_items': added_items,
        'total_sum': total_sum,
        "paypal_approval_url": approval_url,
    }

    return render(request, 'orders/home.html', context)


@login_required(login_url='/login/')
def orders(request):
    """
    View function to render the orders page.
    """
    # Render the 'index.html' template located in the 'templates/orders' directory
    return render(request, 'orders/orders.html')

def send_order_completion_email(user_email, order_items, token, user_name, subject_type, inv):
    subject = f'Order Receipt {subject_type}'
    
    # Calculate total price and construct the email message
    total_price = sum(float(item.total_price) for item in order_items)
    html_message = render_to_string('orders/order_completed_email.html', {'user_name': user_name, 'order_items': order_items, 'total_price': total_price, 'token': token, 'invoice': inv})
    plain_message = strip_tags(html_message)  # Strip HTML tags for the plain text email

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        html_message=html_message,
        fail_silently=False,
    )

@login_required(login_url='/login/')
def orderCashOrder(request):
    if request.method == 'POST':
        order_code = request.POST.get('order_code')
        
        if order_code:
            # Retrieve the order using the order_code
            order = Order.objects.filter(order_code=order_code).first()
            if order:
                # Assuming the order completion involves deleting items from the cart or a similar action
                added_items = OrderItem.objects.filter(user=request.user)
                
                # Get the order items and their details
                order_items = list(added_items)  # Convert to list to avoid multiple queries in the loop
                
                # Send email to the user with order details (implement this function as needed)
                send_order_completion_email(request.user.email, order_items, order_code, request.user.name, 'Cash Payment', 'Null')

                # Calculate total price for display on the order completed page
                total_price = sum(float(item.total_price) for item in order_items)

                # Delete the items from the database
                added_items.delete()

                # Show success message using Django messages framework
                messages.success(request, 'Your order has been completed successfully.')

                # Render the order completed template with total price
                return render(request, 'orders/order-completed.html', {'order_items': order_items, 'total_price': total_price})
            else:
                return HttpResponse('Error: Invalid order code')
        else:
            return HttpResponse('Error: Order code not found')
    else:
        return HttpResponse('Error: Invalid request method')

@login_required(login_url='/login/')
def orderCompleted(request):
    # Extract 'paymentId' and 'PayerID' from the query parameters
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    base_url = os.getenv('PAYPAL_BASE_URL')

    if payment_id and payer_id:
        # Get OAuth token for the API request
        try:
            access_token = get_paypal_oauth_token()
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
        
        # Execute payment
        execute_payment_url = f'{base_url}/payments/payment/{payment_id}/execute'
        execute_data = {
            "payer_id": payer_id
        }
        
        execute_response = requests.post(
            execute_payment_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
            json=execute_data
        )

        if execute_response.status_code == 200:
            execute_response_data = execute_response.json()
            payment_state = execute_response_data['state']

            if payment_state == 'approved':
                transactions = execute_response_data.get('transactions', [])
                transaction_id = transactions[0].get('related_resources', [])[0].get('sale', {}).get('id')
                invoice_number = transactions[0].get('invoice_number')

                # Payment successful
                added_items = OrderItem.objects.filter(user=request.user)
                
                order_items = list(added_items)
                send_order_completion_email(request.user.email, order_items, transaction_id, request.user.name, 'PayPal Online', invoice_number)
                total_price = sum(float(item.total_price) for item in order_items)
                added_items.delete()
                messages.success(request, 'Your order has been completed successfully.')
                return render(request, 'orders/order-completed.html', {
                    'order_items': order_items,
                    'total_price': total_price,
                    'transaction_id': transaction_id,
                    'invoice_number': invoice_number
                })            
            else:
                return HttpResponse(f"Payment not approved: {payment_state}")
        else:
            return HttpResponse(f"Payment execution failed: {execute_response.status_code} {execute_response.text}")
    else:
        return HttpResponse('Error: Payment ID or Payer ID not found')
    

@login_required(login_url='/login/')
def add_order(request):
    if request.method == 'POST':
        menu_item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('qty'))


        user = request.user
        menu_item = get_object_or_404(Menu, pk=menu_item_id)

        # Calculate total price for the current request
        total_price = menu_item.price * quantity
        # Retrieve or create the order for the user
        # Get or create the order
        order, order_created = Order.objects.get_or_create(user=user)
        print(order)
        # Check if the order item already exists
        order_item = OrderItem.objects.filter(
            user=user,
            order=order,
            menu_item=menu_item
        ).first()

        if order_item:
            # Update the existing order_item
            order_item.quantity += quantity
            if menu_item.price is not None:
                order_item.total_price = menu_item.price * order_item.quantity
            else:
                # Handle case where menu_item.price is None
                order_item.total_price = 0
        else:
            # Create a new order_item
            if menu_item.price is not None:
                total_price = menu_item.price * quantity
            else:
                # Handle case where menu_item.price is None
                total_price = 0
            
            order_item = OrderItem.objects.create(
                user=user,
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                total_price=total_price
            )

        # Save the updated order_item
        order_item.save()

        # Update the total amount on the order
        order.total_amount = sum(item.total_price for item in OrderItem.objects.filter(order=order))
        order.save()


        messages.success(request, "Menu item added/updated successfully.")
        return redirect('orders:home')