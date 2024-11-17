from django.shortcuts import render
from django.contrib.auth.hashers import check_password
# Create your views here.
# users/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import View

from .forms import (
    UserLoginForm,
    UserRegistrationForm,
)
from .models import CustomUser

import json
from cypto_utils import encrypt, decrypt


# Create your views here.
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        password1 = form.data['password1']
        password2 = form.data['password2']

        if password1 == password2:
            form.data = form.data.copy()
            encrypted_password = encrypt(password1)
            form.data['password1'] = encrypted_password
            form.data['password2'] = encrypted_password
            form.data['encrypted_pwd'] = encrypted_password

        if form.is_valid():
            # Save the form data
            password11 = form.cleaned_data.get("password1")
            password22 = form.cleaned_data.get("password2")
            print(password11)
            print(password22)
            user = form.save()
            # Extract the saved form data
            user_data = {
                "name": user.name,
                "email": user.email,
            }
            # Pass the form data as context to the success template
            messages.success(
                request,
                "Registration is successful, please login",
            )

            return redirect("users:login")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Check if user with provided email exists
            user = CustomUser.objects.filter(email=email).first()

            if user is not None:
                # Authenticate the user with provided email and password
                encrypted_password = user.encrypted_pwd
                decrypted_password = decrypt(encrypted_password)
                
                
                print(password)
                print(decrypted_password)
                print(check_password(password, decrypted_password))

                # Check the password
                if decrypted_password == password:
                    # If password matches, authenticate and log in the user
                    login(request, user)
                    messages.success(request, 'Logged in successfully.')
                    # Redirect to home view or any other desired view
                    return redirect('orders:home')
                else:
                    # If password doesn't match, show an error message
                    messages.error(request, 'Invalid email or password.')
            else:
                        # If user does not exist
                messages.error(request, "No user exists with this email.")
    else:
        form = UserLoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("orders:home")
