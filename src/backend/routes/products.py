"""
Products API Routes - E-commerce Backend
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import structlog

from backend.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter()


class Product(BaseModel):
    """Product model"""
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    
    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    """Product creation model"""
    name: str
    description: str
    price: float
    stock: int
    category: str


@router.get("/", response_model=List[Product])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all products with optional filtering.
    
    - **skip**: Number of products to skip (pagination)
    - **limit**: Maximum number of products to return
    - **category**: Filter by category (optional)
    """
    logger.info("list_products", skip=skip, limit=limit, category=category)
    
    # Mock data for now (replace with actual DB query)
    products = [
        {
            "id": 1,
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 999.99,
            "stock": 50,
            "category": "electronics",
        },
        {
            "id": 2,
            "name": "Mouse",
            "description": "Wireless mouse",
            "price": 29.99,
            "stock": 200,
            "category": "electronics",
        },
    ]
    
    if category:
        products = [p for p in products if p["category"] == category]
    
    return products[skip : skip + limit]


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    
    - **product_id**: Product ID
    """
    logger.info("get_product", product_id=product_id)
    
    # Mock data (replace with actual DB query)
    if product_id == 1:
        return {
            "id": 1,
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 999.99,
            "stock": 50,
            "category": "electronics",
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product {product_id} not found",
    )


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    
    - **product**: Product data
    """
    logger.info("create_product", product=product.dict())
    
    # Mock response (replace with actual DB insert)
    return {
        "id": 999,
        **product.dict(),
    }


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    """
    Update an existing product.
    
    - **product_id**: Product ID
    - **product**: Updated product data
    """
    logger.info("update_product", product_id=product_id, product=product.dict())
    
    # Mock response (replace with actual DB update)
    return {
        "id": product_id,
        **product.dict(),
    }


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Delete a product.
    
    - **product_id**: Product ID
    """
    logger.info("delete_product", product_id=product_id)
    
    # Mock deletion (replace with actual DB delete)
    return None

# Made with Bob
