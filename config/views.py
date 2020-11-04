import datetime
from datetime import datetime
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.shortcuts import render
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

    
class Dashboard(SubscriptionView, TemplateView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        sub = Subscription.objects.get(business=self.request.user.business)
        remain_days = sub.ends_time.day - timezone.now().day
        context['subscription'] = sub
        context['remain_days'] = remain_days
        return context

    template_name = 'dashboard.html'