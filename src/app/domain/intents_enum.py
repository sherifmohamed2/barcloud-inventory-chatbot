"""
Intent enum — all supported query intents.
"""

from enum import Enum


class IntentEnum(str, Enum):
    COUNT_ASSETS = "count_assets"
    ASSETS_BY_SITE = "assets_by_site"
    ASSET_VALUE_BY_SITE = "asset_value_by_site"
    ASSETS_PURCHASED_THIS_YEAR = "assets_purchased_this_year"
    TOP_VENDOR_BY_ASSETS = "top_vendor_by_assets"
    TOTAL_BILLED_LAST_QUARTER = "total_billed_last_quarter"
    OPEN_PURCHASE_ORDERS = "open_purchase_orders"
    ASSETS_BY_CATEGORY = "assets_by_category"
    SALES_ORDERS_BY_CUSTOMER = "sales_orders_by_customer"
    UNKNOWN = "unknown"
