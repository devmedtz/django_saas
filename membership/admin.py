from django.contrib import admin
from .models import Business, BusinessTeamMember, Plan, Payment

# Register your models here.
admin.site.register(Business)
admin.site.register(BusinessTeamMember)
admin.site.register(Plan)
admin.site.register(Payment)
