from rest_framework import serializers
from django.contrib.auth import get_user_model
from common.enums import UserTypeChoices

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "alias",
            "title",
            "first_name",
            "last_name",
            "email",
            "phone",
            "user_type",
        ]
        read_only_fields = ["alias", "user_type"]


class DoctorSerializer(BaseUserSerializer):
    def create(self, validated_data):
        validated_data["user_type"] = UserTypeChoices.DOCTOR
        password = validated_data.pop("password", "default123")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user