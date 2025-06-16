from datetime import timedelta

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, max_length=255)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        null=True,
        blank=True
    )
    region = models.CharField(max_length=255, null=True, blank=True)
    google_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'Users'


def default_expire_date():
    return timezone.now() + timedelta(minutes=5)


class CodePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    code = models.CharField(max_length=10)
    expire_date = models.DateTimeField(default=default_expire_date)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Password Code"
        verbose_name_plural = "Password Codes"
        db_table = "CodePassword"

    def save(self, *args, **kwargs):
        CodePassword.objects.filter(user=self.user).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Code: {self.code} for {self.user.email} (Expires: {self.expire_date})"


class CodeEmail(models.Model):
    code = models.CharField(max_length=10)
    email = models.EmailField(max_length=200)
    expire_date = models.DateTimeField(default=default_expire_date)

    class Meta:
        verbose_name = "Email Code"
        verbose_name_plural = "Email Codes"
        db_table = "CodeEmail"

    def save(self, *args, **kwargs):
        CodeEmail.objects.filter(email=self.email).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Code: {self.code} for {self.email} (Expires: {self.expire_date})"


class TemporaryUser(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    region = models.CharField(max_length=255)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    re_password = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} - {self.email}"

    class Meta:
        db_table = "TemporaryUser"


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    new_email = models.EmailField()
    code = models.CharField(max_length=10)
    expire_date = models.DateTimeField(default=default_expire_date)

    class Meta:
        db_table = 'email_verifications'

    def save(self, *args, **kwargs):
        EmailVerification.objects.filter(new_email=self.new_email).delete()
        super().save(*args, **kwargs)


class RecentActivity(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]

    MODEL_CHOICES = [
        ('Product', 'Product'),
        ('PlantedProduct', 'Planted Product'),
        ('Region', 'Region'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recent_activities")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)
    object_id = models.PositiveIntegerField()
    object_name = models.CharField(max_length=255)  # Store the string representation
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Recent Activities'
        ordering = ['-timestamp']
        verbose_name = 'Recent Activity'
        verbose_name_plural = 'Recent Activities'

    def __str__(self):
        return f"{self.user.email} {self.get_action_display().lower()} {self.model_name}: {self.object_name}"
