from django.urls import path
from django.urls.conf import include

from .import views

app_name = 'accounts'


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('confirm-email/<str:user_id>/<str:token>/',
         views.ConfirmRegistrationView.as_view(), name='confirm-email'),
    path('', include('django.contrib.auth.urls')),
]
