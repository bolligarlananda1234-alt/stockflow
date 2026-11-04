
from fastapi import APIRouter, Depends
from app.database import get_connection
from app.routers.products import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def get_dashboard(user=Depends(get_current_user)):
    user_id, organization_id = user

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                COUNT(p.product_id) AS total_products,
                COALESCE(SUM(p.quantity), 0) AS total_quantity,
                COALESCE(SUM(
                    CASE
                        WHEN p.quantity <= COALESCE(
                            p.low_stock_threshold,
                            s.default_low_stock_threshold,
                            5
                        )
                        THEN 1
                        ELSE 0
                    END
                ), 0) AS low_stock_products
            FROM Products p
            LEFT JOIN Settings s
                ON p.organization_id = s.organization_id
            WHERE p.organization_id = ?
        """, (organization_id,))

        result = cursor.fetchone()

        return {
            "total_products": result["total_products"],
            "total_quantity": result["total_quantity"],
            "low_stock_products": result["low_stock_products"]
        }

    finally:
        cursor.close()
        connection.close()
