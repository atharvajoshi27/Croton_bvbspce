from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.db import connection, models
from django.conf import settings
import os


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, user_type, password=None, phone=None, is_admin=False):
        if not name:
            raise ValueError("Please provide name")
        if not email:
            raise ValueError("Please provide email")
        if not password:
            raise ValueError("Please provide password")
        if not phone:
            raise ValueError("Please provide phone")
        if not user_type in ["0", "1"]:
            raise ValueError("Please provide correct user type")

        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.user_type = user_type
        user.is_admin = is_admin
        user.set_password(password)
        user.phone = phone
        user.save(using=self._db)

        return user

    def create_superuser(self, name, email, password, phone, user_type="0"):
        return self.create_user(name=name, email=email, password=password, phone=phone, user_type=user_type, is_admin=True)


class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=17, blank=True)
    password = 	models.CharField(max_length=255)
    user_type = models.CharField(max_length=1, default="0") # doctor or patient or admin
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    
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
        return self.is_admin and self.is_active

# class User(AbstractUser):
#     name = models.CharField(max_length=20)


class Doctor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.CharField(max_length=256, blank=True, null=True)
    degree = models.CharField(max_length=256, blank=True, null=True)
    verified = models.BooleanField(default=False)

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encryption_key = models.CharField(max_length=512)
    access_list = models.ManyToManyField(Doctor)    

class Document(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.FileField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        super(Document, self).save(*args, **kwargs)
        # print(f"DEFAULT URL : {self.profile_pic.url}")
        BASE_DIR = settings.BASE_DIR
        UPLOAD_TO = f'Documents/{self.id}'
        path = os.path.join(BASE_DIR, f'media/Documents/{self.id}')
        if not os.path.exists(path):
            os.makedirs(path)
        # print(f"profile_pic.name = {self.profile_pic.name}")
        # print(f"profile pic name = {self.profile_pic.name}")
        filename = self.document.name
        extension = filename.split('.')[-1]

        new_name = f"{self.id}_{filename}"
        location = os.path.join(BASE_DIR, os.path.join('media'))
        print(f"Previous location: {os.path.join(location, filename)}, New location: {os.path.join(location, os.path.join(UPLOAD_TO, new_name))}")
        os.replace(os.path.join(location, filename), os.path.join(location, os.path.join(UPLOAD_TO, new_name)))
        self.document.name = os.path.join(UPLOAD_TO, new_name)
        print(f"name = ", self.document.name)
        super(Document, self).save(*args, **kwargs)



class Report(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    date = models.DateField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    document = models.FileField(null=True)
    def save(self, *args, **kwargs):
        super(Report, self).save(*args, **kwargs)
        
        BASE_DIR = settings.BASE_DIR
        UPLOAD_TO = f'Patient/{self.patient.id}/Reports/'
        path = os.path.join(BASE_DIR, f'media/Patient/{self.patient.id}/Reports/')
        if not os.path.exists(path):
            os.makedirs(path)
        # print(f"profile_pic.name = {self.profile_pic.name}")
        # print(f"profile pic name = {self.profile_pic.name}")
        filename = self.document.name
        extension = filename.split('.')[-1]

        new_name = f"{self.id}_{filename}"
        location = os.path.join(BASE_DIR, os.path.join('media'))
        print(f"Previous location: {os.path.join(location, filename)}, New location: {os.path.join(location, os.path.join(UPLOAD_TO, new_name))}")
        os.replace(os.path.join(location, filename), os.path.join(location, os.path.join(UPLOAD_TO, new_name)))
        self.document.name = os.path.join(UPLOAD_TO, new_name)
        print(f"name = ", self.document.name)
        super(Report, self).save(*args, **kwargs)

class Xray(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    document = models.ImageField()
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    def save(self, *args, **kwargs):
        super(Xray, self).save(*args, **kwargs)
        
        BASE_DIR = settings.BASE_DIR
        UPLOAD_TO = f'Patient/{self.patient.id}/Xrays/'
        path = os.path.join(BASE_DIR, f'media/Patient/{self.patient.id}/Xrays/')
        if not os.path.exists(path):
            os.makedirs(path)
        # print(f"profile_pic.name = {self.profile_pic.name}")
        # print(f"profile pic name = {self.profile_pic.name}")
        filename = self.document.name
        extension = filename.split('.')[-1]

        new_name = f"{self.id}_{filename}"
        location = os.path.join(BASE_DIR, os.path.join('media'))
        print(f"Previous location: {os.path.join(location, filename)}, New location: {os.path.join(location, os.path.join(UPLOAD_TO, new_name))}")
        os.replace(os.path.join(location, filename), os.path.join(location, os.path.join(UPLOAD_TO, new_name)))
        self.document.name = os.path.join(UPLOAD_TO, new_name)
        print(f"name = ", self.document.name)
        super(Xray, self).save(*args, **kwargs)

class Mri(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ImageField()
    title = models.CharField(max_length=256)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    def save(self, *args, **kwargs):
        super(Mri, self).save(*args, **kwargs)
        
        BASE_DIR = settings.BASE_DIR
        UPLOAD_TO = f'Patient/{self.patient.id}/Mris/'
        path = os.path.join(BASE_DIR, f'media/Patient/{self.patient.id}/Mris/')
        if not os.path.exists(path):
            os.makedirs(path)
        # print(f"profile_pic.name = {self.profile_pic.name}")
        # print(f"profile pic name = {self.profile_pic.name}")
        filename = self.document.name
        extension = filename.split('.')[-1]

        new_name = f"{self.id}_{filename}"
        location = os.path.join(BASE_DIR, os.path.join('media'))
        print(f"Previous location: {os.path.join(location, filename)}, New location: {os.path.join(location, os.path.join(UPLOAD_TO, new_name))}")
        os.replace(os.path.join(location, filename), os.path.join(location, os.path.join(UPLOAD_TO, new_name)))
        self.document.name = os.path.join(UPLOAD_TO, new_name)
        print(f"name = ", self.document.name)
        
        super(Mri, self).save(*args, **kwargs)

class Prescription(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    date = models.DateField(null=True)
    document = models.FileField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(Prescription, self).save(*args, **kwargs)
        
        BASE_DIR = settings.BASE_DIR
        UPLOAD_TO = f'Patient/{self.patient.id}/Prescriptions/'
        path = os.path.join(BASE_DIR, f'media/Patient/{self.patient.id}/Prescriptions/')
        if not os.path.exists(path):
            os.makedirs(path)
        # print(f"profile_pic.name = {self.profile_pic.name}")
        # print(f"profile pic name = {self.profile_pic.name}")
        filename = self.document.name
        extension = filename.split('.')[-1]

        new_name = f"{self.id}_{filename}"
        location = os.path.join(BASE_DIR, os.path.join('media'))
        print(f"Previous location: {os.path.join(location, filename)}, New location: {os.path.join(location, os.path.join(UPLOAD_TO, new_name))}")
        os.replace(os.path.join(location, filename), os.path.join(location, os.path.join(UPLOAD_TO, new_name)))
        self.document.name = os.path.join(UPLOAD_TO, new_name)
        print(f"name = ", self.document.name)
        super(Prescription, self).save(*args, **kwargs)
    # optional fields
    # profile_pic = models.ImageField(default='Profiles/default.png')
    # about = models.TextField(null=True, blank=True)
    # twitter = models.URLField(null=True, blank=True)
    # linkedin = models.URLField(null=True, blank=True)