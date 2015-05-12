"""
    Custom fields
"""
from django.db import models


class JSONB(models.Field):
    """Simplest possible JSONB wrapper.
    """
    description = "Postgres 9.4 JSONB field type"

    def db_type(self, connection=None):
        return "JSONB"


try:
    # If South in installed then we need to tell it about our custom field
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
            (
                (JSONB,),
                [],
                {}
            )
        ], [r"^pubsubpull\.fields\.JSONB"])
except ImportError: # pragma: no cover
    # South isn't installed so don't worry about it
    pass
