

from django.db import models

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, password=None, is_admin=False):
        if not name:
            raise ValueError("Please provide name")
        if not email:
            raise ValueError("Please provide email")
        if not password:
            raise ValueError("Please provide password")

        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.is_admin = is_admin
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, name, email, password):
        return self.create_user(name=name, email=email, password=password, is_admin=True)


class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=17, blank=True)
    password = 	models.CharField(max_length=255)
    user_type = models.SmallIntegerField() # doctor or patient or admin

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # optional fields
    # profile_pic = models.ImageField(default='Profiles/default.png')
    # about = models.TextField(null=True, blank=True)
    # twitter = models.URLField(null=True, blank=True)
    # linkedin = models.URLField(null=True, blank=True)



    REQUIRED_FIELDS = ['name', 'password', 'phone']

    objects = CustomUserManager() # Note this

    # @property
    def is_superuser(self):
        return self.is_admin

    # @property
    def is_staff(self):
        return self.is_admin

    # @property
    def has_perm(self, perm, obj=None):
        return self.is_admin and self.is_active
    # @property
    def has_perms(self, perm_list, obj=None):
        return self.is_admin and self.is_active
    
    # @property
    def has_module_perms(self, package_name=None):
        return self.is_admin and self.is_act