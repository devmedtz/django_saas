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
from django.views.generic import TemplateView, FormView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import authenticate, login, logout
#from .utils import get_all_perms, selected_perms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

# from .tokens import account_activation_token
from .forms import CreateTeamForm, UpdateTeamForm
from membership.models import Business, BusinessTeamMember, Subscription, Plan
from accounts.models import Profile
from teams.models import TeamPassword


User = get_user_model()


class CreateTeam(FormView):
    template_name = 'teams/create_team.html'
    form_class = CreateTeamForm

    team_password = get_random_string(length=8)

    def get(self, request, *args, **kwargs):

        teams = User.objects.filter(
            is_team=True, created_by=self.request.user).order_by('-pk')[:10]

        context = {
            'form': self.form_class(
                initial={'password1': self.team_password,
                         'password2': self.team_password}),
            'teams': teams
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            initial={'password1': self.team_password,
                     'password2': self.team_password},
            data=request.POST)

        if form.is_valid():

            team_obj = form.save(commit=False)
            team_obj.is_team = True
            team_obj.is_manager = False
            team_obj.created_by = self.request.user

            team_obj.save()
            TeamPassword.objects.create(
                user=team_obj, password=self.team_password)

            # create profile
            profile = Profile(user=team_obj)
            profile.save()

            # Add to BusinessTeamMember
            business_team = BusinessTeamMember.objects.get_or_create(
                business=request.user.business, user=team_obj)

            # send account confirmation to a team member
            form.send_confirmation_email(team_obj)

            messages.success(request, 'Success, Team created',
                             extra_tags='alert alert-success')

            return redirect(to='teams:create-team')

        teams = User.objects.filter(
            is_team=True, created_by=self.request.user).order_by('-pk')[:10]

        context = {
            'form': form,
            'teams': teams
        }

        messages.error(request, 'Errors occurred',
                       extra_tags='alert alert-danger')

        return render(request, self.template_name, context=context)


class UpdateTeam(FormView):
    template_name = 'teams/edit_team.html'
    form_class = UpdateTeamForm

    def post(self, request, *args, **kwargs):

        person = get_object_or_404(User, pk=self.kwargs['pk'])

        form = self.form_class(instance=person, data=request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request, 'Success, team details updated', extra_tags='alert alert-success')

            return redirect(to='teams:update-team', pk=self.kwargs['pk'])
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

        context = {
            'form': self.form_class(instance=person),
            'person': person,
        }

        return render(request, self.template_name, context=context)


class DeleteTeam(DeleteView):
    model = User
    template_name = 'teams/comfirm_delete.html'

    def get_success_url(self):

        messages.success(self.request, 'Success, team deleted',
                         extra_tags='alert alert-info')

        return reverse_lazy('teams:create-team')
