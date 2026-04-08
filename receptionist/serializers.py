from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.enums import NameTitleChoices, UserTypeChoices
from receptionist.models import Receptionist

User = get_user_model()


class ReceptionistListCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    title = serializers.ChoiceField(
        choices=NameTitleChoices.choices,
        required=False,
        default=NameTitleChoices.MS,
    )
    suburb = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    postal_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Receptionist
        fields = [
            "id",
            "alias",
            "slug",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "title",
            "suburb",
            "postal_code",
            "address",
            "profile_image",
            "employee_id",
            "joining_date",
            "shift",
            "desk_number",
            "experience_years",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "alias", "slug", "created_at", "updated_at"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        phone = validated_data.pop("phone", None)
        title = validated_data.pop("title", NameTitleChoices.MS)
        suburb = validated_data.pop("suburb", None)
        postal_code = validated_data.pop("postal_code", None)
        address = validated_data.pop("address", None)
        profile_image = validated_data.pop("profile_image", None)

        request = self.context.get("request")

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            title=title,
            suburb=suburb,
            postal_code=postal_code,
            address=address,
            profile_image=profile_image,
            user_type=UserTypeChoices.RECEPTIONIST,
            is_active=True,
        )

        receptionist = Receptionist.objects.create(
            user=user,
            created_by=request.user,
            updated_by=request.user,
            **validated_data,
        )
        return receptionist


class ReceptionistRetrieveUpdateSerializer(serializers.ModelSerializer):
    alias = serializers.UUIDField(source="user.alias", read_only=True)
    email = serializers.EmailField(source="user.email", required=False)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    phone = serializers.CharField(source="user.phone", required=False, allow_blank=True, allow_null=True)
    title = serializers.ChoiceField(
        source="user.title",
        choices=NameTitleChoices.choices,
        required=False,
    )
    suburb = serializers.CharField(source="user.suburb", required=False, allow_blank=True, allow_null=True)
    postal_code = serializers.CharField(source="user.postal_code", required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(source="user.address", required=False, allow_blank=True, allow_null=True)
    profile_image = serializers.ImageField(source="user.profile_image", required=False, allow_null=True)

    class Meta:
        model = Receptionist
        fields = [
            "id",
            "alias",
            "slug",
            "email",
            "first_name",
            "last_name",
            "phone",
            "title",
            "suburb",
            "postal_code",
            "address",
            "profile_image",
            "employee_id",
            "joining_date",
            "shift",
            "desk_number",
            "experience_years",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "alias", "slug", "created_at", "updated_at"]

    def validate_email(self, value):
        user = self.instance.user
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            instance.updated_by = request.user

        instance.save()
        return instance


