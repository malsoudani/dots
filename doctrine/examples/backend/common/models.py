from django.db import models

from common.ids import new_id


class BaseModel(models.Model):
    """Every table gets an opaque string id and audit timestamps (BE-DB-2)."""

    id = models.CharField(primary_key=True, max_length=32, default=new_id, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
