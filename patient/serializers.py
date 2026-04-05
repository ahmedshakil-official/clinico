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


class PatientSerializer(BaseUserSerializer):

    def create(self, validated_data):
        validated_data["user_type"] = UserTypeChoices.PATIENT

        user = User(**validated_data)
        user.set_unusable_password()
        user.save()

        return user


