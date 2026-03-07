import json
from enum import Enum

class EnumEncoder(json.JSONEncoder):
    """JSON encoder that handles Enum objects by converting them to their values."""
    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        return super().default(o)

def safe_json_dump(data, file, **kwargs):
    """JSON dump with enum support."""
    return json.dump(data, file, cls=EnumEncoder, **kwargs)

def safe_json_dumps(data, **kwargs):
    """JSON dumps with enum support."""
    return json.dumps(data, cls=EnumEncoder, **kwargs)
