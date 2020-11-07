from django import forms
from django.contrib.auth import get_user_model

from accounts.forms import SignUpForm

User = get_user_model()


class CreateTeamForm(SignUpForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.HiddenInput()
        self.fields['password2'].widget = forms.HiddenInput()


class UpdateTeamForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', ]
