from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.enums import UserTypeChoices, NameTitleChoices
from patient.models import Patient

User = get_user_model()


class PatientListCreateSerializer(serializers.ModelSerializer):
    # User fields
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    title = serializers.ChoiceField(
        choices=NameTitleChoices.choices,
        write_only=True,
        required=False,
        default=NameTitleChoices.MR,
    )
    suburb = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    postal_code = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    profile_image = serializers.ImageField(write_only=True, required=False, allow_null=True)

    # Read-only user info
    user_alias = serializers.UUIDField(source="user.alias", read_only=True)
    patient_alias = serializers.UUIDField(source="alias", read_only=True)
    patient_slug = serializers.CharField(source="slug", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)
    user_title = serializers.CharField(source="user.title", read_only=True)
    user_suburb = serializers.CharField(source="user.suburb", read_only=True)
    user_postal_code = serializers.CharField(source="user.postal_code", read_only=True)
    user_address = serializers.CharField(source="user.address", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "patient_alias",
            "patient_slug",
            "user_alias",
            "user_email",
            "user_first_name",
            "user_last_name",
            "user_phone",
            "user_title",
            "user_suburb",
            "user_postal_code",
            "user_address",
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
            "date_of_birth",
            "gender",
            "blood_group",
            "emergency_contact_name",
            "emergency_contact_phone",
            "medical_history",
        ]

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
        title = validated_data.pop("title", NameTitleChoices.MR)
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
            user_type=UserTypeChoices.PATIENT,
            is_active=True,
        )

        patient = Patient.objects.create(
            user=user,
            receptionist=request.user,
            created_by=request.user,
            updated_by=request.user,
            **validated_data,
        )
        return patient


class PatientRetrieveUpdateSerializer(serializers.ModelSerializer):
    user_alias = serializers.UUIDField(source="user.alias", read_only=True)
    patient_alias = serializers.UUIDField(source="alias", read_only=True)
    patient_slug = serializers.CharField(source="slug", read_only=True)

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
        model = Patient
        fields = [
            "patient_alias",
            "patient_slug",
            "user_alias",
            "email",
            "first_name",
            "last_name",
            "phone",
            "title",
            "suburb",
            "postal_code",
            "address",
            "profile_image",
            "date_of_birth",
            "gender",
            "blood_group",
            "emergency_contact_name",
            "emergency_contact_phone",
            "medical_history",
        ]

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