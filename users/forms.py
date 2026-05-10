from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True, label='Email Address')
    first_name = forms.CharField(max_length=50, required=True, label='First Name')
    last_name  = forms.CharField(max_length=50, required=True, label='Last Name')
    phone      = forms.CharField(max_length=20, required=True, label='Phone Number',
                    help_text='Shared with the other party only after a booking is accepted.')

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise forms.ValidationError('Phone number is required.')
        if len(phone) < 10:
            raise forms.ValidationError('Enter a valid phone number (minimum 10 digits).')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = Profile
        fields = ['phone', 'bio', 'avatar']