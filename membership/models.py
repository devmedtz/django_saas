from django.db import models
from django.db.transaction import TransactionManagementError
from django.contrib.auth import get_user_model

User = get_user_model()


class Business(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.email


class Plan(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    duration_days = models.IntegerField(default=14)
    price = models.FloatField(default=0)
    max_staff = models.IntegerField(default=3)
    max_branch = models.IntegerField(default=3)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if kwargs.get("force", False):
            kwargs.pop("force")
            super(Plan, self).delete(*args, **kwargs)
        else:
            raise TransactionManagementError("Cant't delete Plan objects. On production, set active=False. If you're on development and really want to delete, use object.delete(force=True).")


class Subscription(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    business = models.OneToOneField(Business, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    ends_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    paid_status = models.BooleanField(default=False)  # payment gateway

    def __str__(self):
        return self.business.name


class BusinessTeamMember(models.Model):
    business = models.ForeignKey(Business, on_delete=models.PROTECT)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name


class Payment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True)
    phone = models.CharField(
        max_length=12, verbose_name='Enter your M-PESA mobile number', help_text='example. 255700000000')
    transactionID = models.CharField(max_length=100, blank=True, null=True)
    conversationID = models.CharField(max_length=100, blank=True, null=True)
    reference_no = models.CharField(
        max_length=150, blank=True, null=True)  # payment gateway

    def __str__(self):
        return self.user.business.name
