from django.contrib import admin
from django.urls import path, include
from .import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('membership/', include('membership.urls', namespace='membership'),)
]
