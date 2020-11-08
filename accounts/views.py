from datetime import datetime
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView
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


class Login(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        elif self.request.user.is_admin:
            return reverse('dashboard')
        elif self.request.user.is_manager:
            if self.request.user.business.location == '':
                return reverse('membership:update-business', kwargs={'pk': self.request.user.business.id})
            else:
                return reverse('dashboard')
        elif self.request.user.is_team:
            return reverse('dashboard')
        else:
            return f'/admin/'


def random_name():
    return get_random_string(length=6)


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
        # random business created since field is mandatory
        business = Business(user=user, name=random_name())
        business.save()

        # create BusinessTeamMember
        business_team = BusinessTeamMember.objects.get_or_create(
            business=business, user=user)

        # create free subscription
        plan = Plan.objects.first()

        day = plan.duration_days

        ends_time = timezone.now() + timedelta(days=day)

        subscription = Subscription.objects.get_or_create(
            plan=plan,
            business=business,
            start_time=timezone.now(),
            ends_time=ends_time,
            is_active=True,
        )

        # send confirmation email
        form.send_confirmation_email(user)

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
            if user.is_team:
                # send login credentials
                message = get_template(
                    'teams/login_credentials_email.html').render({
                        'email': f'{user.email}',
                        'password': f'{user.teampassword.password}',
                    })
                mail = EmailMessage(
                    'Login credentials',
                    message,
                    to=[user.email],
                    from_email=settings.EMAIL_HOST_USER)
                mail.content_subtype = 'html'
                mail.send()

        return render(request, 'accounts/registration_complete.html', context)
