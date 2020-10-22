from django.urls import path

from .import views

app_name = 'membership'

urlpatterns = [
    path('', views.paymentView, name='payment')
]
