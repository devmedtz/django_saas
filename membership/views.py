from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from .models import Plan, Subscription
from .forms import PaymentForm


def get_user_plan(request):
    user_plan_qs = Subscription.objects.filter(business=request.user.business)
    print('user_plan_qs:', user_plan_qs)
    if user_plan_qs.exists():
        return user_plan_qs.first()
    return None


def get_selected_plan(request):
    plan_type = request.session['selected_plan_type']
    print('plan_type:', plan_type)
    selected_plan_qs = Plan.objects.filter(
            name=plan_type)
    if selected_plan_qs.exists():
        return selected_plan_qs.first()
    return None


class PricingPage(ListView):
    template_name = 'membership/pricing_page.html'
    model = Plan

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_plan = get_user_plan(self.request)
        context['current_plan'] = str(current_plan.plan)
        return context

    def post(self, request, *args, **kwargs):
        selected_plan_type = request.POST.get('plan_id')
        
        user_subscription = get_user_plan(request)

        selected_plan_qs = Plan.objects.filter(
            id=selected_plan_type)

        if selected_plan_qs.exists():
            selected_plan = selected_plan_qs.first()

        #VALIDATION
        if user_subscription.plan == selected_plan:
            if user_subscription != None:
                messages.info(request, "Your have already this plan")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        #ASIGN TO SESSION
        request.session['selected_plan_type'] = selected_plan.name

        return HttpResponseRedirect(reverse('membership:payment'))  


def paymentView(request):

    selected_plan = get_selected_plan(request)

    plans = Plan.objects.get(name=selected_plan)



    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()

            return HttpResponse('Payment successfully')

    else:
        form = PaymentForm()
        context = {'form':form, 'plans':plans}

    return render(request, 'membership/payment.html', context)



    