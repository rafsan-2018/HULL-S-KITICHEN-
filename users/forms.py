from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser

ALLOWED_EMAILS = ["gmail.com", "outlook.com", "yahoo.com"]


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"


class UserRegistrationForm(FormSettings, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("name", "email", "password1",
                  "password2", "encrypted_pwd")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].placeholder = "Full Name"
        self.fields["email"].placeholder = "Email Address"
        self.fields["password1"].placeholder = "Password"
        self.fields["password2"].placeholder = "Confirm Password"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith(tuple(ALLOWED_EMAILS)):
            raise forms.ValidationError("This email is not allowed.")
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        ),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
