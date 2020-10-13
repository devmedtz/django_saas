from django.shortcuts import render
from django.views.generic import TemplateView


class Dashboard(TemplateView):
    template_name = 'index.html'