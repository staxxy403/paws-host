from enum import Enum

class VPSStatus(Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    CREATING = 'creating'
    DELETED = 'deleted'
