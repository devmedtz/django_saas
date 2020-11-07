import re

from django import forms

from .models import Payment, Business


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        x = re.search("^2557[0-9]{8}$", phone)

        if not x:
            raise forms.ValidationError(
                "Phone number must in format 2557xxxxxxxx")
        return phone


class BusinessForm(forms.ModelForm):

    class Meta:
        model = Business
        fields = ['name', 'location', ]
