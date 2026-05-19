"""
Orders API Routes - E-commerce Backend
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import structlog

from backend.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter()


class OrderItem(BaseModel):
    """Order item model"""
    product_id: int
    quantity: int
    price: float


class Order(BaseModel):
    """Order model"""
    id: int
    user_id: int
    items: List[OrderItem]
    total: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Order creation model"""
    user_id: int
    items: List[OrderItem]


@router.get("/", response_model=List[Order])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    List all orders with optional filtering.
    
    - **skip**: Number of orders to skip (pagination)
    - **limit**: Maximum number of orders to return
    - **user_id**: Filter by user ID (optional)
    """
    logger.info("list_orders", skip=skip, limit=limit, user_id=user_id)
    
    # Mock data (replace with actual DB query)
    orders = [
        {
            "id": 1,
            "user_id": 1,
            "items": [
                {"product_id": 1, "quantity": 1, "price": 999.99}
            ],
            "total": 999.99,
            "status": "completed",
            "created_at": datetime.utcnow(),
        }
    ]
    
    if user_id:
        orders = [o for o in orders if o["user_id"] == user_id]
    
    return orders[skip : skip + limit]


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get a specific order by ID.
    
    - **order_id**: Order ID
    """
    logger.info("get_order", order_id=order_id)
    
    # Mock data (replace with actual DB query)
    if order_id == 1:
        return {
            "id": 1,
            "user_id": 1,
            "items": [
                {"product_id": 1, "quantity": 1, "price": 999.99}
            ],
            "total": 999.99,
            "status": "completed",
            "created_at": datetime.utcnow(),
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Order {order_id} not found",
    )


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    
    - **order**: Order data
    """
    logger.info("create_order", order=order.dict())
    
    # Calculate total
    total = sum(item.price * item.quantity for item in order.items)
    
    # Mock response (replace with actual DB insert)
    return {
        "id": 999,
        "user_id": order.user_id,
        "items": [item.dict() for item in order.items],
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow(),
    }


@router.put("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    """
    Update order status.
    
    - **order_id**: Order ID
    - **status**: New status (pending, processing, completed, cancelled)
    """
    logger.info("update_order_status", order_id=order_id, status=status)
    
    # Mock response (replace with actual DB update)
    return {
        "id": order_id,
        "user_id": 1,
        "items": [
            {"product_id": 1, "quantity": 1, "price": 999.99}
        ],
        "total": 999.99,
        "status": status,
        "created_at": datetime.utcnow(),
    }

# Made with Bob
