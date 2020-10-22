from django.contrib import admin
from .models import Business, BusinessTeamMember, Plan, Payment, Subscription


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    pass


@admin.register(BusinessTeamMember)
class BusinessTeamMemberAdmin(admin.ModelAdmin):
    pass


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
