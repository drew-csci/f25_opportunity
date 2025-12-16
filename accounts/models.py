from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        STUDENT = 'student', 'Student'
        ORGANIZATION = 'organization', 'Organization'
        ADMINISTRATOR = 'administrator', 'Administrator'

    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.STUDENT)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # keep username for admin compatibility

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.email


class FeedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.display_name} - {self.content[:50]}...'
