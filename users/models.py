from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from django.utils.translation import gettext_lazy as _
from django_utz.decorators import model, usermodel
from timezone_field import TimeZoneField
from djmoney.models.fields import CurrencyField
from django.core.mail import EmailMessage, get_connection as get_smtp_connection
from django.urls import reverse

from .managers import UserAccountManager


@model
@usermodel
class UserAccount(PermissionsMixin, AbstractBaseUser):
    """Custom user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(_("email address"), unique=True)
    timezone = TimeZoneField(_("timezone"), default="Africa/Lagos", help_text=_("Choose your timezone."))
    preferred_currency = CurrencyField(_("preferred currency"), default="NGN")
    is_active = models.BooleanField(_("active") ,default=True)
    is_admin = models.BooleanField(_("admin") ,default=False)
    is_staff = models.BooleanField(_("staff") ,default=False)
    is_superuser = models.BooleanField(_("superuser") ,default=False)
    is_verified = models.BooleanField(_("verified") ,default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ("firstname", "lastname")

    objects = UserAccountManager()

    class Meta:
        verbose_name = _("useraccount")
        verbose_name_plural = _("useraccounts")
    
    class UTZMeta:
        timezone_field = "timezone"
        datetime_fields = ["registered_at", "updated_at"]
    

    def __str__(self) -> str:
        return self.email
    
    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
    
    @property
    def initials(self):
        return f"{self.firstname[0]}{self.lastname[0]}"


    def send_verification_email(self):
        """Send verification email to user."""
        if self.is_verified:
            return
        connection = get_smtp_connection()
        email = EmailMessage(
            subject="Graphi - Verify your email address",
            body=construct_verification_email_body(self),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.email],
            connection=connection
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

           
           

def construct_verification_email_body(user: UserAccount) -> str:
    """Construct the verification email body."""
    return f"""
    <div style="font-family: Roboto;">
        <h3>Verify your email address</h3>
        <br>
        <p>Hi {user.firstname},</p>
        <p>Thanks for signing up on Graphi. Please click the link below to verify your email address.</p>
        <p>
            <a href="{settings.BASE_URL}/{reverse("users:account_verification", kwargs={"token": user.id.hex})}">Verify email address</a>
        </p>
    </div>
    """
