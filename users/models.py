import uuid
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .managers import UserManager

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    weight = models.IntegerField()

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_regular_user_role():
        return Role.objects.get(name='user')
    
    @staticmethod
    def get_banned_user_role():
        return Role.objects.get(name='banned')

    @staticmethod 
    def get_deactivated_user_role():
        return Role.objects.get(name='deactivated')

    @staticmethod 
    def get_chat_moderator_role():
        return Role.objects.get(name='chat_moderator')
    
    @staticmethod
    def get_site_moderator_role():
        return Role.objects.get(name='site_moderator')
    
    @staticmethod
    def get_admin_role():
        return Role.objects.get(name='admin')


class User(AbstractBaseUser):
    role = models.ForeignKey(
        Role, 
        on_delete=models.PROTECT,
    )
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    experience = models.IntegerField(default=0)
    is_profile_visible = models.BooleanField(
        default=True,
        verbose_name='Profile visibility'
    ) 
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff status'
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name='Superuser status'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Registration date'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last update'
    )


    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_staff

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['role', 'email']

    objects = UserManager()

class UserLike(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='liked_user'
    )

    def __str__(self):
        return f'{self.id}'
    
    class Meta:
        unique_together = ['user', 'liked_user']

