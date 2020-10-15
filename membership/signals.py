from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Business


@receiver(post_save, sender=Business)
def business_reference_no(sender, instance, created, **kwargs):
    if created:
        reference_no = str(instance.id) + str(instance.created_at.hour) + str(instance.created_at.minute) + str(instance.created_at.year)[-2:]
    
        Business.objects.filter(pk=instance.pk).update(reference_no=reference_no)
        print("reference_no:", reference_no)