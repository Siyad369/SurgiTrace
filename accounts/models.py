from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Role(models.TextChoices):
    DOCTOR = "doctor", "Doctor"
    HOSPITAL_ADMIN = "hospital_admin", "Hospital Admin"
    DEPARTMENT_HEAD = "department_head", "Department Head"
    STUDENT = "student", "Student"
    EXTERNAL_ENTITY = "external_entity", "External Entity"
    SYSTEM_ADMIN = "system_admin", "System Admin"


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.SYSTEM_ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.DOCTOR,
        db_index = True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def clean(self):
        if self.role in [Role.DOCTOR, Role.DEPARTMENT_HEAD] and not self.department:
            raise ValidationError("Department required for this role")

        if self.role in [Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN] and self.department:
            raise ValidationError("Admins should not have department")

    def __str__(self):
        return self.email

    class Meta:
        indexes = [models.Index(fields=["role", "department"])]
