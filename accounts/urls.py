from django.urls import path

from .import views

app_name = 'accounts'


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('confirm-email/<str:user_id>/<str:token>/',
         views.ConfirmRegistrationView.as_view(), name='confirm-email'),
    path('create-staff/', views.CreateStaff.as_view(), name='create-staff'),
    path('update-staff/<int:pk>/', views.UpdateStaff.as_view(), name='update-staff'),
    path('update-password/<int:pk>/', views.UpdatePassword.as_view(), name='update-password'),
    path('delete-staff/<int:pk>/', views.DeleteStaff.as_view(), name='delete-staff'),
    
]