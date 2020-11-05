from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('create/', views.CreateTeam.as_view(), name='create-team'),
    path('update/<int:pk>/', views.UpdateTeam.as_view(), name='update-team'),
    path('delete-team/<int:pk>/', views.DeleteTeam.as_view(), name='delete-team'),
]