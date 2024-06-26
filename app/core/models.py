from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True)  # to avoid potential issues

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Add related_name attributes to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set',  # Avoid conflict with auth.User.groups
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_set',  # Avoid conflict with auth.User.user_permissions
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='core_user',
    )



class UserIDList(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
     userid = models.CharField(max_length=200)    
     def __str__(self):
        return self.userid


class Answers(models.Model):
    userid = models.ForeignKey(UserIDList, on_delete=models.CASCADE)
    question_type_id = models.PositiveIntegerField(default=1)
    data = models.JSONField(default=list,null=True,blank=True)
    def __str__(self):
        return self.userid.userid



