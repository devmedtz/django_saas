from django.urls import path

from .import views

app_name = 'membership'

urlpatterns = [
    path('', views.paymentView, name='payment'),
    path('update/<int:pk>/business/', views.BusinessUpdateView.as_view(), name='update-business')
]
