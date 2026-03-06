from django.db import models
from django.utils import timezone
from .managers import ActiveManager

class SoftDeleteModel(models.Model):

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_delete = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

