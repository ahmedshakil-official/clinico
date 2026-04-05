from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import User  # Import User model


def jwt_payload_handler(token, user=None, request=None):
    """
    Custom JWT payload handler to add extra information.
    """
    if user is None:
        # Attempt to get user.  This is important for compatibility.
        user_id = token.payload.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Exception("User not found")

    payload = {
        "user_id": user.id,
        "email": user.email,
        "phone": user.phone,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_type": user.user_type,
    }

    if user.profile_image:
        request = request  # Access the request
        payload["profile_image"] = (
            request.build_absolute_uri(user.profile_image.url)
            if request
            else user.profile_image.url
        )
    else:
        payload["profile_image"] = None

    return payload
