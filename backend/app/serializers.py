from .models import User
from rest_framework import serializers

# read only:
# Read-only fields are included in the API output, but should not be included in the input during create or update operations. 
# Any 'read_only' fields that are incorrectly included in the serializer input will be ignored.

# write only:
#  Set this to True to ensure that the field may be used when updating or creating an instance, 
# but is not included when serializing the representation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'phone', 'password', 'user_type', 'is_active']
        read_only_field = ['is_active'] 
        write_only_field = ['password']