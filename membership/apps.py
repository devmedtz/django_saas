from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _  #added


class MembershipConfig(AppConfig):
    name = 'membership'

    def ready(self):
        import membership.signals #added
