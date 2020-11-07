from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail.message import EmailMessage
from django.template.loader import get_template
from django.urls.base import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import account_activation_token

User = get_user_model()

# todo: #26 add forms for adding and updating user

BASE_URL = 'http://127.0.0.1:8000'


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        if len(password1) < 8:
            raise forms.ValidationError('It must be 8 character or more')
        return password2

    def send_confirmation_email(self, user):
        token = account_activation_token.make_token(user)
        user_id = urlsafe_base64_encode(force_bytes(user.id))
        url = BASE_URL + reverse('accounts:confirm-email',
                                 kwargs={'user_id': user_id, 'token': token})
        message = get_template(
            'accounts/account_activation_email.html').render(
            {'confirm_url': url})
        mail = EmailMessage(
            'Account Confirmation',
            message,
            to=[user.email],
            from_email=settings.EMAIL_HOST_USER)
        mail.content_subtype = 'html'
        mail.send()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CreateStaffForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'is_active']


class UpdateStaffForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'is_active']
