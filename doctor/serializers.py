from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.enums import NameTitleChoices, UserTypeChoices
from doctor.models import Doctor

User = get_user_model()


class DoctorListCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(source="user.password", write_only=True, min_length=6)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    phone = serializers.CharField(
        source="user.phone",
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    title = serializers.ChoiceField(
        source="user.title",
        choices=NameTitleChoices.choices,
        required=False,
        default=NameTitleChoices.DR,
    )
    suburb = serializers.CharField(
        source="user.suburb",
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    postal_code = serializers.CharField(
        source="user.postal_code",
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    address = serializers.CharField(
        source="user.address",
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    profile_image = serializers.ImageField(
        source="user.profile_image",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Doctor
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
            "degree",
            "specialization",
            "joined_date",
            "consultation_fee",
            "chamber_room",
            "experience_years",
            "bio",
            "gender",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "alias", "slug", "created_at", "updated_at"]

    def validate(self, attrs):
        user_data = attrs.get("user", {})
        email = user_data.get("email")

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "A user with this email already exists."
            })

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop("user", {})

        email = user_data.get("email")
        password = user_data.get("password")
        first_name = user_data.get("first_name")
        last_name = user_data.get("last_name")
        phone = user_data.get("phone", None)
        title = user_data.get("title", NameTitleChoices.DR)
        suburb = user_data.get("suburb", None)
        postal_code = user_data.get("postal_code", None)
        address = user_data.get("address", None)
        profile_image = user_data.get("profile_image", None)

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
            user_type=UserTypeChoices.DOCTOR,
            is_active=True,
        )

        doctor = Doctor.objects.create(
            user=user,
            created_by=request.user,
            updated_by=request.user,
            **validated_data,
        )
        return doctor


class DoctorRetrieveUpdateSerializer(serializers.ModelSerializer):
    # user_alias = serializers.UUIDField(source="user.alias", read_only=True)
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
        model = Doctor
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
            "degree",
            "specialization",
            "joined_date",
            "consultation_fee",
            "chamber_room",
            "experience_years",
            "bio",
            "gender",
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