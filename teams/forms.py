from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CreateTeamForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'is_active']


class UpdateTeamForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'is_active']