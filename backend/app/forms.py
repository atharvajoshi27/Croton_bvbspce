from django.forms import ModelForm, Textarea
from .models import User

# Using this form we can easily create users
class CreateUser(ModelForm):
	class Meta:
		model = User
		fields = ['name', 'email', 'password', 'phone', 'user_type']