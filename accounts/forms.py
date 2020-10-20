from django import forms

from django.contrib.auth import get_user_model

User = get_user_model()

# todo: #26 add forms for adding and updating user


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        if len(password1) < 8:
            raise forms.ValidationError('It must be 8 character or more')
        return password2

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
