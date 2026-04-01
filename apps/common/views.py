from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import IsOrganizationMember


class BaseTenantModelViewSet(ModelViewSet):
    """
    Base ViewSet that enforces tenant isolation.
    All tenant models must inherit this.
    """

    permission_classes = [IsAuthenticated, IsOrganizationMember]

    tenant_field = None  # must be set by child classes

    def get_queryset(self):
        if not self.tenant_field:
            raise AssertionError(
                "tenant_field must be set in the viewset"
            )

        filter_kwargs = {
            self.tenant_field: self.request.organization
        }

        return self.queryset.filter(**filter_kwargs)

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        if hasattr(instance, "soft_delete"):
            instance.soft_delete()
            return

        instance.delete()
