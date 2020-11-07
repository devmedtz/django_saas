from datetime import datetime
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from .models import Plan, Subscription, Business
from .forms import PaymentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

# Vodacom mpesa intergrations
from django.conf import settings
from portalsdk import APIContext, APIMethodType, APIRequest
from time import sleep

from datetime import datetime, timedelta, date


def get_user_plan(request):
    user_plan_qs = Subscription.objects.filter(business=request.user.business)
    if user_plan_qs.exists():
        return user_plan_qs.first()
    return None


def get_selected_plan(request):

    plan_type = request.session.get('selected_plan_type')
    host = request.get_host()

    selected_plan_qs = Plan.objects.filter(
        name=plan_type)
    if selected_plan_qs.exists():
        return selected_plan_qs.first()

    return HttpResponse('Session expire')

def has_expire(request):
    sub = Subscription.objects.get(business=request.user.business)

    return sub.ends_time < timezone.now()


class PricingPage(ListView):
    template_name = 'membership/pricing_page.html'
    model = Plan

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            current_plan = get_user_plan(self.request)
            context['current_plan'] = str(current_plan.plan)
        return context

    def post(self, request, *args, **kwargs):
        selected_plan_type = request.POST.get('plan_id')

        user_subscription = get_user_plan(request)

        has_expired = has_expire(request)
        print('has_expire:', has_expired)

        selected_plan_qs = Plan.objects.filter(
            id=selected_plan_type)

        if selected_plan_qs.exists():
            selected_plan = selected_plan_qs.first()

        # VALIDATION
        if user_subscription.plan == selected_plan:
            if user_subscription != None:
                messages.info(request, "Your have already this plan")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # ASIGN TO SESSION
        request.session['selected_plan_type'] = selected_plan.name

        return HttpResponseRedirect(reverse('membership:payment'))


@login_required
def paymentView(request):

    selected_plan = get_selected_plan(request)
    plans = Plan.objects.get(name=selected_plan)

    business = Business.objects.get(user=request.user)

    current_subscription = get_user_plan(request)

    reference_no = str(request.user.id) + str(current_subscription.id) + \
        datetime.now().strftime('%Y%m%d%H%M%S')


    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():

            # Begin payment processing
            public_key = settings.PUBLIC_KEY

            # Create Context with API to request a Session ID
            api_context = APIContext()

            # Api key
            api_context.api_key = settings.API_KEY

            # Public key
            api_context.public_key = public_key

            # Use ssl/https
            api_context.ssl = True

            # Method type (can be GET/POST/PUT)
            api_context.method_type = APIMethodType.GET

            # API address
            api_context.address = 'openapi.m-pesa.com'

            # API Port
            api_context.port = 443

            # API Path
            api_context.path = '/sandbox/ipg/v2/vodacomTZN/getSession/'

            # Add/update headers
            api_context.add_header('Origin', '*')

            # Parameters can be added to the call as well that on POST will be in JSON format and on GET will be URL parameters
            # api_context.add_parameter('key', 'value')

            # Do the API call and put result in a response packet
            api_request = APIRequest(api_context)

            # Do the API call and put result in a response packet
            result = None
            try:
                result = api_request.execute()
            except Exception as e:
                print('Call Failed: ' + e)

            if result is None:
                raise Exception(
                    'SessionKey call failed to get result. Please check.')

            # The above call issued a sessionID
            api_context = APIContext()
            api_context.api_key = result.body['output_SessionID']
            api_context.public_key = public_key
            api_context.ssl = True
            api_context.method_type = APIMethodType.POST
            api_context.address = 'openapi.m-pesa.com'
            api_context.port = 443
            api_context.path = '/sandbox/ipg/v2/vodacomTZN/c2bPayment/singleStage/'
            api_context.add_header('Origin', '*')

            # Input Variables
            has_expired = has_expire(request)
            selected_price = plans.price
            current_price = current_subscription.plan.price
            
            if plans.id != 1 and has_expired == False and selected_price > current_price:
                amount = selected_price - current_price
            else:
                amount = selected_price

            phone = request.POST.get('phone')
            desc = plans.name

            api_context.add_parameter('input_Amount', amount)
            api_context.add_parameter('input_Country', 'TZN')
            api_context.add_parameter('input_Currency', 'TZS')
            # phone number from customer
            api_context.add_parameter('input_CustomerMSISDN', '000000000001')
            api_context.add_parameter('input_ServiceProviderCode', '000000')
            api_context.add_parameter(
                'input_ThirdPartyConversationID', 'asv02e5958774f7ba228d83d0d689761')
            api_context.add_parameter(
                'input_TransactionReference', reference_no)
            api_context.add_parameter('input_PurchasedItemsDesc', desc)

            api_request = APIRequest(api_context)

            sleep(30)

            result = None

            try:
                result = api_request.execute()
            except Exception as e:
                print('Call Failed: ' + e)

            if result is None:
                raise Exception('API call failed to get result. Please check.')

            if result.body['output_ResponseCode'] == 'INS-0':

                #Update/downgrade subscriptions - New Plan/Existing plan.
                ends_times = timezone.now() + timedelta(days=plans.duration_days)

                if plans.id != 1 and has_expired == False and selected_price > current_price:
                    start_times = current_subscription.start_time
                    ends_time = current_subscription.ends_time

                else:
                    start_times = timezone.now()
                    ends_time = ends_times

                print('start_times:', start_times)
                print('ends_time:', ends_time)

                Subscription.objects.filter(business=request.user.business).update(
                    plan=plans.id,
                    start_time=start_times,
                    ends_time=ends_time,
                    paid_status=True,
                )


                # save transactionID,transactionID
                payment = form.save(commit=False)
                payment.user_id = request.user.id
                payment.transactionID = result.body['output_TransactionID']
                payment.conversationID = result.body['output_ConversationID']
                payment.reference_no = reference_no
                payment.save()

                return HttpResponse('Your Payment was Successfully sent!')

            elif result.body['output_ResponseCode'] == 'INS-1':
                messages.add_message(request, messages.ERROR, 'Internal Error')

            elif result.body['output_ResponseCode'] == 'INS-6':
                messages.add_message(
                    request, messages.ERROR, 'Transaction Failed')

            elif result.body['output_ResponseCode'] == 'INS-9':
                messages.add_message(
                    request, messages.ERROR, 'Request timeout')

            elif result.body['output_ResponseCode'] == 'INS-10':
                messages.add_message(
                    request, messages.ERROR, 'Duplicate Transaction')

            elif result.body['output_ResponseCode'] == 'INS-2006':
                messages.add_message(
                    request, messages.ERROR, 'Insufficient balance')

            else:
                messages.add_message(
                    request, messages.ERROR,
                    'Configuration Error, contact with support team')

    else:
        form = PaymentForm()
    context = {'form': form, 'plans': plans, 'reference_no': reference_no}

    return render(request, 'membership/payment.html', context)
