from datetime import datetime
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView, FormView, DeleteView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import authenticate, login, logout
#from .utils import get_all_perms, selected_perms
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

from .tokens import account_activation_token
from .forms import SignUpForm, CreateStaffForm, UpdateStaffForm
from .models import Profile
from membership.models import Business, BusinessTeamMember, Subscription, Plan


User = get_user_model()

BASE_URL = 'http://127.0.0.1:8000'


class Login(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        elif self.request.user.is_admin:
            return reverse('membership')
        elif self.request.user.is_manager or self.request.user.is_staff:
            return reverse('membership')
        else:
            return f'/admin/'


def signup(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        user_email = form.cleaned_data['email']
        user.is_manager = True
        user.save()

        # create profile
        profile = Profile(user=user)
        profile.save()

        # create business
        business = Business(user=user)
        business.save()

        # create BusinessTeamMember
        business_team = BusinessTeamMember.objects.get_or_create(
            business=business, user=user)

        # create free subscription
        ends_time = timezone.now() + timedelta(days=14)

        subscription = Subscription.objects.get_or_create(
            plan_id=1,
            business=business,
            start_time=timezone.now(),
            ends_time=ends_time,
            is_active=True,
        )

        # send confirmation email
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
            to=[user_email],
            from_email=settings.EMAIL_HOST_USER)
        mail.content_subtype = 'html'
        mail.send()

        return render(request, 'accounts/registration_pending.html',
                      {'message': (
                          'A confirmation email has been sent to your email'
                          '. Please confirm to finish registration.')}
                      )
    return render(request, 'accounts/signup.html', {
        'form': form,
    })


class ConfirmRegistrationView(TemplateView):

    def get(self, request, user_id, token):
        user_id = force_text(urlsafe_base64_decode(user_id))

        user = User.objects.get(pk=user_id)

        context = {
            'message': 'Registration confirmation error. Please click the reset password to generate a new confirmation email.'
        }

        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            context['message'] = 'Registration complete. Please login'

        return render(request, 'accounts/registration_complete.html', context)


class CreateStaff(FormView):
    template_name = 'accounts/create_staff.html'
    form_class = CreateStaffForm

    def get(self, request, *args, **kwargs):

        staffs = User.objects.filter(
            is_staff=True, created_by=self.request.user).order_by('-pk')[:10]

        context = {
            'form': self.form_class,
            'staffs': staffs
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)

        if form.is_valid():

            staff_obj = form.save(commit=False)
            staff_obj.is_staff = True
            staff_obj.is_manager = False
            staff_obj.created_by = self.request.user

            # Set default password to phone_number
            # todo: #23 generate random characters
            staff_obj.set_password(
                raw_password=form.cleaned_data['phone']
            )

            staff_obj.save()

            messages.success(request, 'Success, staff created',
                             extra_tags='alert alert-success')

            return redirect(to='accounts:home')

        staffs = User.objects.filter(
            is_staff=True, created_by=self.request.user).order_by('-pk')[:10]

        context = {
            'form': form,
            'staffs': staffs
        }

        messages.error(request, 'Errors occurred',
                       extra_tags='alert alert-danger')

        return render(request, self.template_name, context=context)


class UpdateStaff(FormView):
    template_name = 'accounts/edit_staff.html'
    form_class = UpdateStaffForm
    password_form = PasswordChangeForm

    def post(self, request, *args, **kwargs):

        person = get_object_or_404(User, pk=self.kwargs['pk'])

        form = self.form_class(instance=person, data=request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request, 'Success, staff details updated', extra_tags='alert alert-success')

            return redirect(to='accounts:update-staff', pk=self.kwargs['pk'])
        else:

            context = {
                'form': self.form_class(data=request.POST, instance=person),
                'person': person,
                'password_form': self.password_form
            }

            messages.error(request, 'Failed, errors occurred.',
                           extra_tags='alert alert-danger')

            return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        person = get_object_or_404(User, pk=self.kwargs['pk'])

        password_form = self.password_form(user=person)

        password_form.fields['old_password'].widget.attrs.pop(
            "autofocus", None)

        context = {
            'form': self.form_class(instance=person),
            'person': person,
            'password_form': password_form
        }

        return render(request, self.template_name, context=context)


class DeleteStaff(DeleteView):

    model = User

    def get_success_url(self):

        messages.success(self.request, 'Success, staff deleted',
                         extra_tags='alert alert-info')

        return reverse_lazy('accounts:home')


class UpdatePassword(FormView):
    form_class = PasswordChangeForm

    def post(self, request, *args, **kwargs):

        staff = get_object_or_404(User, pk=self.kwargs['pk'])

        form = self.form_class(user=staff, data=request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, password updated',
                             extra_tags='alert alert-success')
        else:
            messages.error(request, 'Failed, password NOT updated',
                           extra_tags='alert alert-danger')

        return redirect(to='accounts:update-staff', pk=self.kwargs['pk'])


class Logout(FormView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):

        logout(request)

        return redirect(to='accounts:login')
