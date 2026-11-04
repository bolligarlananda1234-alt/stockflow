
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from app.database import get_connection
from jose import jwt, JWTError
from dotenv import load_dotenv
from typing import Optional
import os
import sqlite3

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter(prefix="/products", tags=["Products"])
security = HTTPBearer()


class ProductCreate(BaseModel):
    product_name: str = Field(min_length=2, max_length=150)
    sku: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    quantity: int = Field(ge=0)
    cost_price: float = Field(ge=0)
    selling_price: float = Field(ge=0)
    low_stock_threshold: Optional[int] = Field(default=None, ge=0)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload["sub"])
        organization_id = int(payload["organization_id"])

        return user_id, organization_id

    except (JWTError, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ADD PRODUCT
@router.post("/")
def add_product(
    data: ProductCreate,
    current_user: tuple = Depends(get_current_user)
):
    user_id, organization_id = current_user

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO Products (
                organization_id, product_name, sku,
                description, quantity, cost_price,
                selling_price, low_stock_threshold
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                organization_id,
                data.product_name,
                data.sku,
                data.description,
                data.quantity,
                data.cost_price,
                data.selling_price,
                data.low_stock_threshold
            )
        )

        product_id = cursor.lastrowid
        connection.commit()

        return {
            "message": "Product added successfully",
            "product_id": product_id,
            "organization_id": organization_id
        }

    except sqlite3.IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="SKU already exists in your organization"
        )

    except Exception as error:
        connection.rollback()
        print("Add product error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to add product"
        )

    finally:
        cursor.close()
        connection.close()


# GET ALL PRODUCTS
@router.get("/")
def get_products(
    current_user: tuple = Depends(get_current_user)
):
    user_id, organization_id = current_user

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                product_id,
                product_name,
                sku,
                description,
                quantity,
                cost_price,
                selling_price,
                low_stock_threshold
            FROM Products
            WHERE organization_id = ?
            ORDER BY product_id DESC
            """,
            (organization_id,)
        )

        rows = cursor.fetchall()

        products = []

        for row in rows:
            products.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "sku": row["sku"],
                "description": row["description"],
                "quantity": row["quantity"],
                "cost_price": float(row["cost_price"]),
                "selling_price": float(row["selling_price"]),
                "low_stock_threshold": row["low_stock_threshold"]
            })

        return {
            "total_products": len(products),
            "products": products
        }

    finally:
        cursor.close()
        connection.close()


# UPDATE PRODUCT
@router.put("/{product_id}")
def update_product(
    product_id: int,
    data: ProductCreate,
    current_user: tuple = Depends(get_current_user)
):
    user_id, organization_id = current_user

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT product_id
            FROM Products
            WHERE product_id = ? AND organization_id = ?
            """,
            (product_id, organization_id)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        cursor.execute(
            """
            UPDATE Products
            SET
                product_name = ?,
                sku = ?,
                description = ?,
                quantity = ?,
                cost_price = ?,
                selling_price = ?,
                low_stock_threshold = ?
            WHERE product_id = ? AND organization_id = ?
            """,
            (
                data.product_name,
                data.sku,
                data.description,
                data.quantity,
                data.cost_price,
                data.selling_price,
                data.low_stock_threshold,
                product_id,
                organization_id
            )
        )

        connection.commit()

        return {
            "message": "Product updated successfully",
            "product_id": product_id
        }

    except HTTPException:
        connection.rollback()
        raise

    except sqlite3.IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="SKU already exists in your organization"
        )

    except Exception as error:
        connection.rollback()
        print("Update product error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to update product"
        )

    finally:
        cursor.close()
        connection.close()
