from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Plan


class PricingPage(TemplateView):
    template_name = 'membership/pricing_page.html'

    def get(self, request, *args, **kwargs):

        plans = Plan.objects.all()

        context = {
            'plans': plans
        }

        return render(request, self.template_name, context=context)

    