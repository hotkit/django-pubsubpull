"""
    Custom fields
"""
import json

from django.db import models


class JSONB(models.Field):
    """Simplest possible JSONB wrapper.
    """
    description = "Postgres 9.4 JSONB field type"
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection=None):
        return "JSONB"

    def to_python(self, value):
        if not value:
            return None
        elif type(value) != dict:
            return json.loads(value)
        else:
            return value


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

try:
    # If slumber is installed we need to tell it about our custom field
    from slumber.server.json import DATA_MAPPING
    DATA_MAPPING['pubsubpull.fields.JSONB'] = lambda m, i, fm, v: v
except ImportError: # pragma: no cover
    # Slumber isn't installed, don't worry about it
    pass

