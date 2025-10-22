from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        # Include phone & KYC_status, exclude sensitive fields from read
        fields = ['first_name','last_name','email','role','phone','KYC_status','password','confirm_password',]
        read_only_fields = ['id','KYC_status']  # Prevent users from setting these manually during signup

    def validate(self, attrs):
        # Validate password match and strength
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Password strength check
        validate_password(attrs.get("password"))
        return attrs

    def create(self, validated_data):
        #  Remove confirm_password since it's not in the model
        validated_data.pop("confirm_password", None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        # Exclude password fields from the serialized output
        rep = super().to_representation(instance)
        rep.pop('password', None)
        rep.pop('confirm_password', None)
        return rep

class KYCVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['KYC_status']

    def update(self, instance, validated_data):
        instance.KYC_status = True
        instance.save()
        return instance