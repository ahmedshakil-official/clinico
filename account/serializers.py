from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from common.enums import UserTypeChoices
# from common.serializers import CommonUserSerializer


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model that includes the desired fields.
    """

    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "title",
            "first_name",
            "last_name",
            "profile_image",
            "user_type",
        )

    def get_profile_image(self, obj):
        """
        Method to serialize the profile image URL.
        """
        if obj.profile_image:
            # Construct the full URL, handling potential issues.
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            else:
                return obj.profile_image.url  # important for other cases
        return None


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Return access/refresh plus a minimal user object.
    """

    @classmethod
    def get_token(cls, user):
        # Optional – put *claims* inside the JWT itself
        token = super().get_token(user)
        token["user_type"] = user.user_type
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get("request")# {'access', 'refresh'}
        # Add whatever you want in the HTTP response:
        data["user"] = {
            "title": self.user.title,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "user_type": self.user.user_type,
            "profile_image": (
                request.build_absolute_uri(self.user.profile_image.url)
                if request and self.user.profile_image else None
            ),
        }
        return data


class CustomUserCreateSerializer(UserCreateSerializer):
    # Fields for the required information during registration
    phone = serializers.CharField(max_length=24, required=False)
    profile_image = serializers.ImageField(required=False)
    user_type = serializers.ChoiceField(
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.SELECT_USER_TYPE,
        required=False,
    )
    # created_by = CommonUserSerializer(read_only=True)
    # updated_by = CommonUserSerializer(read_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = [
            "email",
            "phone",
            "title",
            "first_name",
            "last_name",
            "profile_image",
            "user_type",
            "password",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        # Check if the request context has a user
        request_user = (
            self.context["request"].user if "request" in self.context else None
        )
        print("=" * 20)
        print(request_user)
        print("=" * 20)

        # Extract user data
        password = validated_data.pop("password")

        with transaction.atomic():
            # Create the user
            user = User(**validated_data)
            user.set_password(password)

            # Assign created_by only if the request user is authenticated
            if request_user and request_user.is_authenticated:
                user.created_by = request_user

            user.save()

        return user

    def update(self, instance, validated_data):
        # Check if the request context has a user
        request_user = (
            self.context["request"].user if "request" in self.context else None
        )

        with transaction.atomic():
            # Update user fields
            for attr, value in validated_data.items():
                if attr == "password":
                    instance.set_password(value)
                else:
                    setattr(instance, attr, value)

            # Assign updated_by only if the request user is authenticated
            if request_user and request_user.is_authenticated:
                instance.updated_by = request_user

            instance.save()

        return instance
