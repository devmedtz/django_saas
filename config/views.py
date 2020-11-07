import datetime
from datetime import datetime
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, View
from membership.models import Subscription, BusinessTeamMember


class BusinessView(View):
    """
    This view must by inherited by any view that should be accessed only
    if the user making the request is part of a business that is registered
    """

    def initial(self, request, *args, **kwargs):
	    ret = super(BusinessView, self).initial(request, *args, **kwargs)
	    if not request.user.is_anonymous():
		    try:
			    team_member = BusinessTeamMember.objects.get(user=request.user)
			    request.business = team_member.business
		    except BusinessTeamMember.DoesNotExist:
			    raise MemberDoesNotExist()
	    return ret


class SubscriptionView(BusinessView):
    """
    This view must be inherited by any view that should be accessed only if
    there is an active subscription present for a business to which
    the user that is making the request belongs to
    """

    def initial(self, request, *args, **kwargs):
	    ret = super(SubscriptionView, self).initial(request, *args, **kwargs)
	    try:
		    subscription = Subscription.objects.get(business=request.business, is_active=True)
		    request.subscription = subscription
	    except Subscription.DoesNotExist:
		    raise NoActiveSubscriptionFound()
	    return ret

    
class Dashboard(LoginRequiredMixin, UserPassesTestMixin, SubscriptionView, TemplateView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        sub = Subscription.objects.get(business=self.request.user.businessteammember.business)
        remain_days = sub.ends_time - timezone.now()
        context['subscription'] = sub
        #context['remain_days'] = remain_days.days
        context['remain_days'] = remain_days
        return context

    template_name = 'dashboard.html'

    def test_func(self):
        if self.request.user.business.location != '':
            return True

    def handle_no_permission(self):
        return redirect(reverse('membership:update-business', kwargs={'pk': self.request.user.business.id}))