from rest_framework import serializers
from .models import Organization, OrganizationInvitation, Membership


# ==============================
# ORGANIZATION
# ==============================

class OrganizationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = fields


# ==============================
# INVITATION - CREATE
# ==============================

class InvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["ADMIN", "MEMBER"])


# ==============================
# INVITATION - READ (SAFE)
# ==============================

class InvitationSerializer(serializers.ModelSerializer):
    invited_by = serializers.StringRelatedField()
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    class Meta:
        model = OrganizationInvitation
        fields = [
            "id",
            "email",
            "role",
            "status",              # ✅ correct field
            "organization_name",  # ✅ frontend needs this
            "invited_by",
            "created_at",
            "expires_at",
        ]
        read_only_fields = fields


# ==============================
# INVITATION - ACCEPT
# ==============================

class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

class MemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = Membership
        fields = ["id", "email", "role", "created_at"]