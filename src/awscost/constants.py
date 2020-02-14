import os

AVAILABLE_DIMENSIONS = [
    "AZ",
    "INSTANCE_TYPE",
    "LINKED_ACCOUNT",
    "OPERATION",
    "PURCHASE_TYPE",
    "SERVICE",
    "USAGE_TYPE",
    "PLATFORM",
    "TENANCY",
    "RECORD_TYPE",
    "LEGAL_ENTITY_NAME",
    "DEPLOYMENT_OPTION",
    "DATABASE_ENGINE",
    "CACHE_ENGINE",
    "INSTANCE_TYPE_FAMILY",
    "REGION",
    "BILLING_ENTITY",
    "RESERVATION_ID",
    "SAVINGS_PLANS_TYPE",
    "SAVINGS_PLAN_ARN",
    "OPERATING_SYSTEM",
]

AVAILABLE_METRICS = [
    "BlendedCost",
    "UnblendedCost",
    "AmortizedCost",
    "NetAmortizedCost",
    "NetUnblendedCost",
    "UsageQuantity",
    "NormalizedUsageAmount",
]

# default value
DEFAULT_CONFIG = f"{os.getenv('HOME')}/.awscost"
DEFAULT_PROFILE = "default"

DEFAULT_METRICS = "UnblendedCost"
DEFAULT_POINT = 7
DEFAULT_GRANULARITY = "MONTHLY"
DEFAULT_TOTAL = True
DEFAULT_DEBUG = False
DEFAULT_DIMENSIONS = ["SERVICE"]
