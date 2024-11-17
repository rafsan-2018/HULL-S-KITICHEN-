# Import Necessary Modules
- Import necessary modules and libraries

# Define Models
- Define `Menu` model with fields: `name`, `description`, `price`
- Define `Order` model with fields: `user`, `order_code`, `total_amount`, `created_at`
- Define `OrderItem` model with fields: `user`, `order`, `menu_item`, `quantity`, `total_price`

                # Define Registration Function
- If POST request:
  - Get user data, create and save new user
  - Show success message and redirect to login
- Else:
  - Render registration template

# Define Login Function
- If POST request:
  - Get credentials, authenticate user
  - If successful: log user in and redirect to home
  - Else: show error message
- Render login template

# Define Home Function
- Ensure user is logged in
- Get user, menu items, and user's order items
- If items exist: update order total, create payment item list
- Else: set default values
- Generate invoice number, get PayPal token
- If items in cart: create and send payment data, get approval URL
- Render home template with context

# Define Orders Function
- Ensure user is logged in
- Render orders template

# Define Send Order Completion Email Function
- Calculate total price, render email message, send email

# Define Order Cash Order Function
- Ensure user is logged in and POST request
- Get order code
- If valid order: get order and items, send email, delete items, show success, render order completed template
- Else: return error

# Define Order Completed Function
- Ensure user is logged in
- Get paymentId and PayerID
- If valid: get token, execute PayPal payment
  - If approved: get transaction details, send email, delete items, show success, render order completed template
  - Else: return error
- Else: return error

# Define Add Order Function
- Ensure user is logged in and POST request
- Get menu item ID and quantity
- Get user and menu item, calculate total price
- Get or create order and order item, update or create order item
- Save order item, update order total
- Show success message, redirect to home
