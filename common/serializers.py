from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
)
from djoser.serializers import UserCreateSerializer

# from case.models import Case
from common.utils import get_random_string
from common.enums import UserTypeChoices
from common.models import User



class ListSerializer(ModelSerializer):

    class Meta:
        ref_name = ""
        fields = (
            "id",
            "slug",
        )
        read_only_fields = ("id", "slug")


# class OrganizationUserListSerializer(ModelSerializer):
#     class Meta:
#         model = OrganizationUser
#         ref_name = "OrganizationUserList"
#         fields = [
#             "id",
#             "alias",
#         ]
#         read_only_fields = [
#             "id",
#             "alias",
#         ]


class CommonUserSerializer(UserCreateSerializer):
    phone = serializers.CharField(max_length=24, required=False)
    profile_image = serializers.ImageField(required=False)
    user_type = serializers.ChoiceField(
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.SELECT_USER_TYPE,
        required=False,
    )

    class Meta(UserCreateSerializer.Meta):
        fields = [
            "alias",
            "email",
            "phone",
            "title",
            "first_name",
            "last_name",
            "profile_image",
            "user_type",
        ]


class CommonUserWithIdSerializer(UserCreateSerializer):
    phone = serializers.CharField(max_length=24, required=False)
    profile_image = serializers.ImageField(required=False)
    user_type = serializers.ChoiceField(
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.SELECT_USER_TYPE,
        required=False,
    )

    class Meta(UserCreateSerializer.Meta):
        fields = [
            "id",
            "alias",
            "email",
            "phone",
            "title",
            "first_name",
            "last_name",
            "profile_image",
            "user_type",
        ]


class CommonUserWithPasswordSerializer(UserCreateSerializer):
    phone = serializers.CharField(max_length=24, required=False)
    profile_image = serializers.ImageField(required=False)
    user_type = serializers.ChoiceField(
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.SELECT_USER_TYPE,
        required=False,
    )

    class Meta(UserCreateSerializer.Meta):
        fields = [
            "id",
            "email",
            "phone",
            "title",
            "first_name",
            "last_name",
            "profile_image",
            "user_type",
        ]

    def validate(self, attrs):
        if not attrs.get("password"):
            attrs["password"] = get_random_string(8)
        return super().validate(attrs)

    def create(self, validated_data):
        user = super().create(validated_data)

        return user



from patient.models import Patient
from doctor.models import Doctor


class PatientNestedSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "alias",
            "slug",
            "full_name",
            "gender",
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class DoctorNestedSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "alias",
            "slug",
            "full_name",
            "specialization",
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"