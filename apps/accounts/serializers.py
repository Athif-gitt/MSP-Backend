from django.contrib.auth import get_user_model, authenticate
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .services import send_verification_email

from apps.organizations.models import Organization
from apps.organizations.models import Membership

from django.db import transaction

from django.utils import timezone

from apps.organizations.models import OrganizationInvitation


User = get_user_model()


# REGISTER SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(write_only=True, required=False)
    invite_token = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password", "organization_name", "invite_token")

    def create(self, validated_data):
        try:
            with transaction.atomic():

                invitation = validated_data.pop("invitation", None)
                organization_name = validated_data.pop("organization_name", None)

                user = User.objects.create_user(
                    email=validated_data["email"],
                    first_name=validated_data.get("first_name", ""),
                    last_name=validated_data.get("last_name", ""),
                    password=validated_data["password"],
                    is_active=True if invitation else False,  # 🔥 KEY CHANGE
                )

                # ✅ INVITE FLOW (MEMBER)
                if invitation:
                    return user

                # ✅ OWNER FLOW (UNCHANGED)
                organization = Organization.objects.create(
                    name=organization_name,
                    owner=user
                )

                Membership.objects.create(
                    user=user,
                    organization=organization,
                    role="owner"
                )

            # Send email ONLY for owner flow
            if not invitation:
                try:
                    send_verification_email(user)
                except Exception:
                    pass

            return user

        except Exception:
            raise serializers.ValidationError({
                "detail": "Registration failed. Please try again."
            })
        
    def validate(self, data):
        invite_token = data.get("invite_token")

        if invite_token:
            try:
                invitation = OrganizationInvitation.objects.get(token=invite_token)
            except OrganizationInvitation.DoesNotExist:
                raise serializers.ValidationError("Invalid invitation")

            if invitation.status != "PENDING":
                raise serializers.ValidationError("Invitation not valid")

            if invitation.expires_at < timezone.now():
                raise serializers.ValidationError("Invitation expired")

            if invitation.email != data["email"]:
                raise serializers.ValidationError("Email must match invitation")

            data["invitation"] = invitation

        else:
            # OWNER FLOW
            if not data.get("organization_name"):
                raise serializers.ValidationError({
                    "organization_name": "This field is required for owner signup"
                })

        return data


# LOGIN SERIALIZER
class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("Email not verified")
        
        membership = user.memberships.first()
        organization = membership.organization if membership else None

        refresh = RefreshToken.for_user(user)

        return {
            "user_id": str(user.id),
            "email": user.email,
            "organization_id": str(organization.id) if organization else None,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    role = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            'role'
        ]

    def get_role(self, obj):

        request = self.context.get("request")

        membership = Membership.objects.filter(
            user=obj,
            organization=request.organization
        ).first()

        if membership:
            return membership.role
        return None
    

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "bio",
            "timezone",
            "email_verified",
            "created_at",
        ]
        read_only_fields = ["email", "email_verified", "created_at"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
class UserProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "avatar",
            "bio",
            "timezone",
        ]
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(min_length=8)

class MeSerializer(serializers.ModelSerializer):
    organizations = serializers.SerializerMethodField()
    current_organization = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "organizations",
            "current_organization",
        ]

    def get_organizations(self, obj):
        memberships = obj.memberships.select_related("organization")

        return [
            {
                "id": m.organization.id,
                "name": m.organization.name,
                "role": m.role,
            }
            for m in memberships
        ]

    def get_current_organization(self, obj):
        request = self.context.get("request")

        org_id = request.headers.get("X-Organization-ID")

        if org_id:
            membership = obj.memberships.filter(
                organization_id=org_id
            ).first()
        else:
            membership = obj.memberships.first()

        if not membership:
            return None

        return {
            "id": membership.organization.id,
            "name": membership.organization.name,
            "role": membership.role,
        }