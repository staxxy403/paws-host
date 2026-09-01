from enum import Enum


class VPSStatus(Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    CREATING = 'creating'
    DELETED = 'deleted'
    ERROR = 'error'

class TransactionType(Enum):
    # Topups
    DEPOSIT = 'deposit'
    REFUND = 'refund'
    REFERRAL_REWARD = 'referral_reward'
    PROMO_CODE = 'promo_code'
    ADMIN_GRANT = 'admin_grant'

    # Spends
    VPS_PURCHASE = 'vps_purchase'
    VPS_RENEWAL = 'vps_renewal'
    TARIFF_UPGRADE = 'tariff_upgrade'
    ADMIN_CHARGE = 'admin_charge'

class TransactionStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
