"""
SQL Server-compatible query templates for each intent.
"""

from src.app.domain.intents_enum import IntentEnum
from src.app.domain.errors import SQLValidationError

SQL_TEMPLATES: dict[IntentEnum, str] = {
    IntentEnum.COUNT_ASSETS: (
        "SELECT COUNT(*) AS AssetCount FROM Assets WHERE Status <> 'Disposed';"
    ),
    IntentEnum.ASSETS_BY_SITE: (
        "SELECT s.SiteName, COUNT(*) AS AssetCount "
        "FROM Assets a JOIN Sites s ON s.SiteId = a.SiteId "
        "WHERE a.Status <> 'Disposed' "
        "GROUP BY s.SiteName ORDER BY AssetCount DESC;"
    ),
    IntentEnum.ASSET_VALUE_BY_SITE: (
        "SELECT s.SiteName, SUM(a.Cost) AS TotalValue "
        "FROM Assets a JOIN Sites s ON s.SiteId = a.SiteId "
        "WHERE a.Status <> 'Disposed' "
        "GROUP BY s.SiteName ORDER BY TotalValue DESC;"
    ),
    IntentEnum.ASSETS_PURCHASED_THIS_YEAR: (
        "SELECT COUNT(*) AS Count FROM Assets "
        "WHERE YEAR(PurchaseDate) = YEAR(GETDATE());"
    ),
    IntentEnum.TOP_VENDOR_BY_ASSETS: (
        "SELECT TOP 1 v.VendorName, COUNT(*) AS AssetCount "
        "FROM Assets a JOIN Vendors v ON v.VendorId = a.VendorId "
        "GROUP BY v.VendorName ORDER BY AssetCount DESC;"
    ),
    IntentEnum.TOTAL_BILLED_LAST_QUARTER: (
        "SELECT SUM(TotalAmount) AS TotalBilled FROM Bills "
        "WHERE BillDate >= DATEADD(q, -1, DATEADD(q, DATEDIFF(q, 0, GETDATE()), 0)) "
        "AND BillDate < DATEADD(q, DATEDIFF(q, 0, GETDATE()), 0);"
    ),
    IntentEnum.OPEN_PURCHASE_ORDERS: (
        "SELECT COUNT(*) AS OpenPOs FROM PurchaseOrders WHERE Status = 'Open';"
    ),
    IntentEnum.ASSETS_BY_CATEGORY: (
        "SELECT Category, COUNT(*) AS AssetCount FROM Assets "
        "WHERE Status <> 'Disposed' "
        "GROUP BY Category ORDER BY AssetCount DESC;"
    ),
    IntentEnum.SALES_ORDERS_BY_CUSTOMER: (
        "SELECT c.CustomerName, COUNT(*) AS OrderCount "
        "FROM SalesOrders so JOIN Customers c ON c.CustomerId = so.CustomerId "
        "WHERE so.SODate >= DATEADD(month, -1, GETDATE()) "
        "GROUP BY c.CustomerName ORDER BY OrderCount DESC;"
    ),
    IntentEnum.UNKNOWN: "",
}


def get_sql(intent: IntentEnum) -> str:
    """
    Return the SQL template for a given intent.

    Raises SQLValidationError if the template is empty and intent is not UNKNOWN.
    """
    template = SQL_TEMPLATES.get(intent, "")
    if not template and intent is not IntentEnum.UNKNOWN:
        raise SQLValidationError(intent.value)
    return template
