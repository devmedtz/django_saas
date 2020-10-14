from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractBaseUser


from .managers import CustomUserManager


class CustomUser(AbstractBaseUser):
    name = models.CharField(verbose_name='Full Name', max_length=100)
    email = models.EmailField(verbose_name='Email Address', unique=True, max_length=100)
    phone = models.CharField(max_length=50, unique=True, verbose_name='Phone Number')
    
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    is_manager = models.BooleanField(default=False)
    is_team = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']


    def has_perm(self, perm, obj=None):

        return True

        # if self.is_superuser or self.is_admin or self.is_manager:
        #     return True

    def has_module_perms(self, app_label):

        return True

        # if self.is_superuser or self.is_admin or self.is_manager:
        #     return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser

    def __str__(self):
        return self.email


# Profile Picture
def profile_pic_filename(instance, filename):
    ext = filename.split('.')[1]
    new_filename = f'{uuid4()}.{ext}'
    return f'profile_pics/{new_filename}'


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    profile_pic = models.ImageField(verbose_name='Profile Picture', default='profile_pics/user.svg', upload_to=profile_pic_filename)

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.user_id})

    def get_profile_update_url(self):
        return reverse('accounts:profile-update', kwargs={'pk': self.user_id})

    def __str__(self):
        return f'{self.user.name} Profile'