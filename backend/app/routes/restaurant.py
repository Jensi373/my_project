
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.db_config import restaurants_collection, db
from app.models.restaurant import RestaurantRegister, RestaurantLogin

from passlib.context import CryptContext
from jose import jwt
from bson import ObjectId

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


router = APIRouter(
    prefix="/api/restaurants",
    tags=["Restaurants"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"

foods_collection = db["foods"]
orders_collection = db["orders"]
tables_collection = db["tables"]


# ==========================================================
# MODELS
# ==========================================================

class RestaurantUpdate(BaseModel):
    restaurantName: str
    ownerName: str
    email: EmailStr
    phone: str
    address: str
    logo: str = ""
    theme: dict = Field(default_factory=dict)


class OrderStatusUpdate(BaseModel):
    status: str


class TableCreate(BaseModel):
    table_number: str
    capacity: int = Field(gt=0, le=50)
    notes: str = ""


class TableUpdate(BaseModel):
    table_number: str
    capacity: int = Field(gt=0, le=50)
    notes: str = ""


class TableStatusUpdate(BaseModel):
    status: str


# ==========================================================
# ORDER STATUS FLOW
# ==========================================================

ORDER_STATUS_FLOW = {
    "Placed": ["Accepted", "Rejected"],
    "Accepted": ["Preparing"],
    "Preparing": ["Ready"],
    "Ready": ["Completed"],
    "Completed": [],
    "Rejected": []
}


# ==========================================================
# TABLE STATUS SETTINGS
# ==========================================================

ALLOWED_TABLE_STATUSES = [
    "Available",
    "Reserved",
    "Cleaning"
]

TERMINAL_ORDER_STATUSES = [
    "completed",
    "delivered",
    "rejected",
    "cancelled"
]


# ==========================================================
# HELPER: CHECK RESTAURANT
# ==========================================================

def check_restaurant_exists(restaurant_id: str):

    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid restaurant ID"
        )

    restaurant = restaurants_collection.find_one({
        "_id": ObjectId(restaurant_id)
    })

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return restaurant


# ==========================================================
# HELPER: GET ORDERS FOR ONE RESTAURANT
# ==========================================================

def get_restaurant_orders(restaurant_id: str):

    restaurant_object_id = ObjectId(restaurant_id)

    restaurant_foods = list(
        foods_collection.find(
            {"restaurant_id": restaurant_id},
            {"_id": 1, "food_name": 1}
        )
    )

    food_ids = [
        str(food["_id"])
        for food in restaurant_foods
    ]

    food_names = {
        str(food["_id"]): food.get("food_name", "")
        for food in restaurant_foods
    }

    if not food_ids:
        return []

    possible_orders = orders_collection.find({
        "$or": [
            {
                "restaurant_id": {
                    "$in": [restaurant_id, restaurant_object_id]
                }
            },
            {
                "restaurantId": {
                    "$in": [restaurant_id, restaurant_object_id]
                }
            },
            {
                "items.food_id": {
                    "$in": food_ids
                }
            }
        ]
    }).sort("created_at", -1)

    restaurant_orders = []

    for order in possible_orders:

        restaurant_items = []

        for item in order.get("items", []):

            food_id = str(item.get("food_id", ""))

            if food_id not in food_ids:
                continue

            quantity = int(item.get("quantity", 1) or 1)
            price = float(item.get("price", 0) or 0)

            subtotal = float(
                item.get("subtotal", price * quantity) or 0
            )

            restaurant_items.append({
                "food_id": food_id,
                "name": item.get(
                    "name",
                    food_names.get(food_id, "Food")
                ),
                "category": item.get("category", ""),
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal
            })

        if not restaurant_items:
            continue

        restaurant_total = sum(
            item["subtotal"]
            for item in restaurant_items
        )

        total_items = sum(
            item["quantity"]
            for item in restaurant_items
        )

        created_at = order.get("created_at")

        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        restaurant_statuses = order.get(
            "restaurant_statuses", {}
        )

        restaurant_status = restaurant_statuses.get(
            restaurant_id,
            order.get("order_status", "Placed")
        )

        # Support older orders which use Pending
        if str(restaurant_status).strip().lower() == "pending":
            restaurant_status = "Placed"

        restaurant_order = {
            "_id": str(order["_id"]),
            "order_number": order.get("order_number", ""),
            "customer_id": str(order.get("customer_id", "")),
            "customer_name": order.get("customer_name", "Customer"),
            "customer_email": order.get("customer_email", ""),
            "phone": order.get("phone", ""),
            "alternate_phone": order.get("alternate_phone", ""),
            "delivery_type": order.get("delivery_type", ""),
            "delivery_address": order.get("delivery_address", {}),
            "table_number": order.get("table_number", ""),
            "items": restaurant_items,
            "total_items": total_items,
            "total_price": restaurant_total,
            "restaurant_total": restaurant_total,
            "payment_method": order.get("payment_method", ""),
            "payment_status": order.get("payment_status", "Pending"),
            "order_status": restaurant_status,
            "restaurant_status": restaurant_status,
            "created_at": created_at
        }

        restaurant_orders.append(restaurant_order)

    return restaurant_orders


# ==========================================================
# HELPER: CHECK TODAY'S DATE IN INDIA
# ==========================================================

def is_today_order(order):

    created_at = order.get("created_at")

    if not created_at:
        return False

    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )
        except ValueError:
            return False

    if not isinstance(created_at, datetime):
        return False

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    india_timezone = ZoneInfo("Asia/Kolkata")

    order_date = created_at.astimezone(
        india_timezone
    ).date()

    today = datetime.now(india_timezone).date()

    return order_date == today


# ==========================================================
# HELPER: CONVERT DATETIME
# ==========================================================

def parse_table_datetime(value):

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    if not isinstance(value, datetime):
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value


# ==========================================================
# HELPER: GET ORDERS FOR A SHARED TABLE
# ==========================================================

def get_table_order_details(
    table_number: str,
    last_cleared_at=None
):

    baseline = parse_table_datetime(last_cleared_at)

    dine_in_orders = orders_collection.find({
        "delivery_type": {
            "$regex": "^dine_in$",
            "$options": "i"
        },
        "table_number": table_number
    }).sort("created_at", -1)

    table_orders = []

    for order in dine_in_orders:

        restaurant_statuses = order.get(
            "restaurant_statuses", {}
        )

        order_restaurant_ids = set()
        order_items = []

        for item in order.get("items", []):

            food_id = str(item.get("food_id", ""))

            try:
                food = foods_collection.find_one({
                    "_id": ObjectId(food_id)
                })

                if food:
                    restaurant_id = str(
                        food.get("restaurant_id", "")
                    )

                    if restaurant_id:
                        order_restaurant_ids.add(restaurant_id)

            except Exception:
                pass

            order_items.append({
                "name": item.get("name", "Food"),
                "quantity": int(item.get("quantity", 1) or 1)
            })

        # Get status of every restaurant involved
        statuses = []

        if order_restaurant_ids:

            for rid in order_restaurant_ids:

                status = restaurant_statuses.get(
                    rid,
                    order.get("order_status", "Placed")
                )

                statuses.append(
                    str(status).strip().lower()
                )

        else:

            statuses.append(
                str(order.get("order_status", "Placed"))
                .strip()
                .lower()
            )

        # Ignore orders that were entirely rejected or cancelled
        if all(
            status in ["rejected", "cancelled"]
            for status in statuses
        ):
            continue

        created_at = parse_table_datetime(
            order.get("created_at")
        )

        is_after_last_clear = (
            baseline is None
            or created_at is None
            or created_at > baseline
        )

        has_unfinished_order = any(
            status not in TERMINAL_ORDER_STATUSES
            for status in statuses
        )

        # Ignore old completed orders from previous table sessions
        if not is_after_last_clear and not has_unfinished_order:
            continue

        # A table can be cleared only when all restaurants finish
        can_clear = all(
            status in TERMINAL_ORDER_STATUSES
            for status in statuses
        )

        created_at_value = order.get("created_at")

        if isinstance(created_at_value, datetime):
            created_at_value = created_at_value.isoformat()

        display_status = ", ".join(
            status.title()
            for status in sorted(set(statuses))
        )

        table_orders.append({
            "order_id": str(order["_id"]),
            "order_number": order.get("order_number", ""),
            "customer_name": order.get(
                "customer_name", "Customer"
            ),
            "phone": order.get("phone", ""),
            "order_status": display_status,
            "items": order_items,
            "created_at": created_at_value,
            "can_clear": can_clear
        })

    return table_orders


# ==========================================================
# REGISTER RESTAURANT
# ==========================================================

@router.post("/register")
async def register_restaurant(data: RestaurantRegister):

    if data.password != data.confirmPassword:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    if len(data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters"
        )

    existing_restaurant = restaurants_collection.find_one({
        "email": str(data.email)
    })

    if existing_restaurant:
        raise HTTPException(
            status_code=400,
            detail="Restaurant with this email already exists"
        )

    if len(data.logo or "") > 3 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Restaurant logo is too large"
        )

    hashed_password = pwd_context.hash(data.password)

    restaurant = {
        "restaurantName": data.restaurantName,
        "ownerName": data.ownerName,
        "email": str(data.email),
        "phone": data.phone,
        "password": hashed_password,
        "address": data.address,
        "logo": data.logo or "",
        "theme": data.theme,
        "status": "Active"
    }

    result = restaurants_collection.insert_one(restaurant)

    return {
        "message": "Restaurant registered successfully",
        "restaurant_id": str(result.inserted_id),
        "restaurantName": data.restaurantName
    }


# ==========================================================
# LOGIN RESTAURANT
# ==========================================================

@router.post("/login")
async def login_restaurant(data: RestaurantLogin):

    restaurant = restaurants_collection.find_one({
        "email": str(data.email)
    })

    if not restaurant:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = pwd_context.verify(
        data.password,
        restaurant["password"]
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    restaurant_id = str(restaurant["_id"])

    token_data = {
        "restaurant_id": restaurant_id,
        "email": restaurant["email"]
    }

    token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "restaurant_id": restaurant_id,
        "restaurantName": restaurant["restaurantName"]
    }


# ==========================================================
# RESTAURANT DASHBOARD
# ==========================================================

@router.get("/{restaurant_id}/dashboard")
async def get_restaurant_dashboard(restaurant_id: str):

    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid restaurant ID"
        )

    restaurant = restaurants_collection.find_one({
        "_id": ObjectId(restaurant_id)
    })

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    all_orders = get_restaurant_orders(restaurant_id)

    today_orders = [
        order for order in all_orders
        if is_today_order(order)
    ]

    completed_statuses = ["completed", "delivered"]
    cancelled_statuses = ["cancelled", "rejected"]

    completed_orders = [
        order for order in all_orders
        if order["order_status"].lower() in completed_statuses
    ]

    pending_orders = [
        order for order in all_orders
        if order["order_status"].lower()
        not in completed_statuses + cancelled_statuses
    ]

    today_revenue = sum(
        order["restaurant_total"]
        for order in today_orders
        if order["order_status"].lower() not in cancelled_statuses
    )

    recent_orders = all_orders[:10]

    return {
        "restaurant_id": restaurant_id,
        "restaurantName": restaurant["restaurantName"],
        "ownerName": restaurant.get("ownerName", ""),
        "email": restaurant.get("email", ""),
        "phone": restaurant.get("phone", ""),
        "todayOrders": len(today_orders),
        "pendingOrders": len(pending_orders),
        "completedOrders": len(completed_orders),
        "todayRevenue": today_revenue,
        "recentOrders": recent_orders,
        "popularFood": []
    }


# ==========================================================
# GET ALL ORDERS FOR THIS RESTAURANT
# ==========================================================

@router.get("/{restaurant_id}/orders")
async def get_restaurant_order_list(restaurant_id: str):

    check_restaurant_exists(restaurant_id)

    orders = get_restaurant_orders(restaurant_id)

    return {
        "restaurant_id": restaurant_id,
        "total_orders": len(orders),
        "orders": orders
    }


# ==========================================================
# UPDATE ORDER STATUS FOR THIS RESTAURANT ONLY
# ==========================================================

@router.put("/{restaurant_id}/orders/{order_id}/status")
async def update_restaurant_order_status(
    restaurant_id: str,
    order_id: str,
    data: OrderStatusUpdate
):

    # 1. Validate IDs
    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid restaurant ID"
        )

    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid order ID"
        )

    restaurant_object_id = ObjectId(restaurant_id)
    order_object_id = ObjectId(order_id)

    # 2. Check restaurant
    restaurant = restaurants_collection.find_one({
        "_id": restaurant_object_id
    })

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    # 3. Get order
    order = orders_collection.find_one({
        "_id": order_object_id
    })

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 4. Verify that this order contains food belonging to this restaurant
    restaurant_owns_order = False

    for item in order.get("items", []):

        food_id = str(item.get("food_id", ""))

        if not ObjectId.is_valid(food_id):
            continue

        food = foods_collection.find_one({
            "_id": ObjectId(food_id)
        })

        if food and str(food.get("restaurant_id", "")) == restaurant_id:
            restaurant_owns_order = True
            break

    if not restaurant_owns_order:
        raise HTTPException(
            status_code=403,
            detail="This order does not belong to your restaurant"
        )

    # 5. Get this restaurant's current status
    restaurant_statuses = order.get(
        "restaurant_statuses", {}
    )

    current_status = restaurant_statuses.get(
        restaurant_id,
        order.get("order_status", "Placed")
    )

    current_status = str(current_status).strip().title()

    new_status = data.status.strip().title()

    # Support old orders using Pending
    if current_status == "Pending":
        current_status = "Placed"

    # 6. Validate new status
    if new_status not in ORDER_STATUS_FLOW:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    allowed_statuses = ORDER_STATUS_FLOW.get(
        current_status, []
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change status from "
                f"{current_status} to {new_status}"
            )
        )

        # 7. Find all restaurants involved in this order
    order_restaurant_ids = set()

    for item in order.get("items", []):
        food_id = str(item.get("food_id", ""))

        if not ObjectId.is_valid(food_id):
            continue

        food = foods_collection.find_one({
            "_id": ObjectId(food_id)
        })

        if food:
            order_restaurant_ids.add(
                str(food.get("restaurant_id", ""))
            )

    # 8. Update restaurant-specific status
    update_fields = {
        f"restaurant_statuses.{restaurant_id}": new_status
    }

    # If only one restaurant is involved, also update overall status
    if len(order_restaurant_ids) == 1:
        update_fields["order_status"] = new_status

    result = orders_collection.update_one(
        {"_id": order_object_id},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 9. Verify saved status
    updated_order = orders_collection.find_one({
        "_id": order_object_id
    })

    saved_status = updated_order.get(
        "restaurant_statuses", {}
    ).get(restaurant_id)

    if saved_status != new_status:
        raise HTTPException(
            status_code=500,
            detail="Order status could not be saved"
        )

    return {
        "success": True,
        "message": "Order status saved successfully",
        "order_id": order_id,
        "restaurant_id": restaurant_id,
        "previous_status": current_status,
        "new_status": saved_status,
        "overall_status": updated_order.get("order_status")
    }

# ==========================================================
# GET RESTAURANT DETAILS
# ==========================================================

@router.get("/{restaurant_id}")
async def get_restaurant(restaurant_id: str):

    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid restaurant ID"
        )

    restaurant_object_id = ObjectId(restaurant_id)

    restaurant = restaurants_collection.find_one({
        "_id": restaurant_object_id
    })

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return {
        "restaurant_id": str(restaurant["_id"]),
        "restaurantName": restaurant["restaurantName"],
        "ownerName": restaurant["ownerName"],
        "email": restaurant["email"],
        "phone": restaurant["phone"],
        "address": restaurant.get("address", ""),
        "logo": restaurant.get("logo", ""),
        "theme": restaurant.get("theme", {})
    }


# ==========================================================
# UPDATE RESTAURANT PROFILE
# ==========================================================

@router.put("/{restaurant_id}")
async def update_restaurant(
    restaurant_id: str,
    data: RestaurantUpdate
):

    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid restaurant ID"
        )

    restaurant_object_id = ObjectId(restaurant_id)

    restaurant = restaurants_collection.find_one({
        "_id": restaurant_object_id
    })

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    existing_email = restaurants_collection.find_one({
        "email": str(data.email),
        "_id": {"$ne": restaurant_object_id}
    })

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="This email is already used by another restaurant"
        )

    if len(data.logo or "") > 3 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Restaurant logo is too large"
        )

    updated_data = {
        "restaurantName": data.restaurantName.strip(),
        "ownerName": data.ownerName.strip(),
        "email": str(data.email),
        "phone": data.phone.strip(),
        "address": data.address.strip(),
        "logo": data.logo or "",
        "theme": data.theme
    }

    restaurants_collection.update_one(
        {"_id": restaurant_object_id},
        {"$set": updated_data}
    )

    return {
        "message": "Restaurant profile updated successfully",
        "restaurant_id": restaurant_id,
        "restaurantName": updated_data["restaurantName"]
    }


# ==========================================================
# DELETE RESTAURANT ACCOUNT
# ==========================================================

@router.delete("/{restaurant_id}")
async def delete_restaurant(restaurant_id: str):

    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid restaurant ID"
        )

    restaurant_object_id = ObjectId(restaurant_id)

    restaurant = restaurants_collection.find_one({
        "_id": restaurant_object_id
    })

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    related_collections = [
        "foods",
        "food",
        "menus",
        "orders",
        "order_items",
        "orderItems",
        "kitchen",
        "feedback",
        "reviews",
        "reservations"
    ]

    existing_collections = set(db.list_collection_names())

    deleted_records = {}

    restaurant_values = [
        restaurant_id,
        restaurant_object_id
    ]

    ownership_filter = {
        "$or": [
            {"restaurant_id": {"$in": restaurant_values}},
            {"restaurantId": {"$in": restaurant_values}},
            {"restaurantID": {"$in": restaurant_values}}
        ]
    }

    for collection_name in related_collections:

        if collection_name not in existing_collections:
            continue

        collection = db[collection_name]

        result = collection.delete_many(ownership_filter)

        deleted_records[collection_name] = result.deleted_count

    result = restaurants_collection.delete_one({
        "_id": restaurant_object_id
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete restaurant account"
        )

    return {
        "message": "Restaurant account and associated records deleted successfully",
        "restaurant_id": restaurant_id,
        "deleted_records": deleted_records
    }


# ==========================================================
# SHARED TABLE MANAGEMENT
# ==========================================================

# ADD SHARED TABLE

@router.post("/{restaurant_id}/tables")
async def add_shared_table(
    restaurant_id: str,
    data: TableCreate
):

    check_restaurant_exists(restaurant_id)

    table_number = data.table_number.strip()

    if not table_number:
        raise HTTPException(
            status_code=400,
            detail="Table number is required"
        )

    table_number_key = table_number.casefold()

    existing_table = tables_collection.find_one({
        "table_number_key": table_number_key
    })

    if existing_table:
        raise HTTPException(
            status_code=400,
            detail="This table number already exists in the food court"
        )

    created_at = datetime.now(timezone.utc)

    table = {
        "table_number": table_number,
        "table_number_key": table_number_key,
        "capacity": data.capacity,
        "notes": data.notes.strip(),
        "manual_status": "Available",
        "created_at": created_at,
        "last_cleared_at": created_at
    }

    result = tables_collection.insert_one(table)

    return {
        "message": "Shared table added successfully",
        "table_id": str(result.inserted_id),
        "table_number": table_number
    }


# GET ALL SHARED TABLES

@router.get("/{restaurant_id}/tables")
async def get_shared_tables(restaurant_id: str):

    check_restaurant_exists(restaurant_id)

    all_tables = tables_collection.find().sort(
        "table_number_key", 1
    )

    result = []

    for table in all_tables:

        table_number = table.get("table_number", "")

        active_orders = get_table_order_details(
            table_number,
            table.get(
                "last_cleared_at",
                table.get("created_at")
            )
        )

        if active_orders:
            current_status = "Occupied"
        else:
            current_status = table.get(
                "manual_status", "Available"
            )

        can_clear = (
            len(active_orders) > 0
            and all(
                order["can_clear"]
                for order in active_orders
            )
        )

        result.append({
            "_id": str(table["_id"]),
            "table_number": table_number,
            "capacity": table.get("capacity", 2),
            "notes": table.get("notes", ""),
            "status": current_status,
            "active_orders": active_orders,
            "can_clear": can_clear
        })

    return {
        "total_tables": len(result),
        "tables": result
    }


# UPDATE SHARED TABLE DETAILS

@router.put("/{restaurant_id}/tables/{table_id}")
async def update_shared_table(
    restaurant_id: str,
    table_id: str,
    data: TableUpdate
):

    check_restaurant_exists(restaurant_id)

    if not ObjectId.is_valid(table_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid table ID"
        )

    table_object_id = ObjectId(table_id)

    existing_table = tables_collection.find_one({
        "_id": table_object_id
    })

    if not existing_table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )

    table_number = data.table_number.strip()

    if not table_number:
        raise HTTPException(
            status_code=400,
            detail="Table number is required"
        )

    table_number_key = table_number.casefold()

    duplicate_table = tables_collection.find_one({
        "table_number_key": table_number_key,
        "_id": {"$ne": table_object_id}
    })

    if duplicate_table:
        raise HTTPException(
            status_code=400,
            detail="This table number already exists"
        )

    if table_number != existing_table.get("table_number"):

        active_orders = get_table_order_details(
            existing_table.get("table_number", ""),
            existing_table.get(
                "last_cleared_at",
                existing_table.get("created_at")
            )
        )

        if active_orders:
            raise HTTPException(
                status_code=400,
                detail="Cannot change table number while it is occupied"
            )

    tables_collection.update_one(
        {"_id": table_object_id},
        {
            "$set": {
                "table_number": table_number,
                "table_number_key": table_number_key,
                "capacity": data.capacity,
                "notes": data.notes.strip()
            }
        }
    )

    return {
        "message": "Table updated successfully",
        "table_id": table_id
    }


# UPDATE MANUAL TABLE STATUS

@router.put("/{restaurant_id}/tables/{table_id}/status")
async def update_shared_table_status(
    restaurant_id: str,
    table_id: str,
    data: TableStatusUpdate
):

    check_restaurant_exists(restaurant_id)

    if not ObjectId.is_valid(table_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid table ID"
        )

    table_object_id = ObjectId(table_id)

    table = tables_collection.find_one({
        "_id": table_object_id
    })

    if not table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )

    new_status = data.status.strip().title()

    if new_status not in ALLOWED_TABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Choose Available, Reserved or Cleaning"
        )

    active_orders = get_table_order_details(
        table.get("table_number", ""),
        table.get(
            "last_cleared_at",
            table.get("created_at")
        )
    )

    if active_orders:
        raise HTTPException(
            status_code=400,
            detail=(
                "This table has orders in its current session. "
                "Clear the table before changing its manual status."
            )
        )

    tables_collection.update_one(
        {"_id": table_object_id},
        {
            "$set": {
                "manual_status": new_status
            }
        }
    )

    return {
        "message": "Table status updated successfully",
        "status": new_status
    }


# CLEAR TABLE AFTER CUSTOMER LEAVES

@router.put("/{restaurant_id}/tables/{table_id}/clear")
async def clear_shared_table(
    restaurant_id: str,
    table_id: str
):

    check_restaurant_exists(restaurant_id)

    if not ObjectId.is_valid(table_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid table ID"
        )

    table_object_id = ObjectId(table_id)

    table = tables_collection.find_one({
        "_id": table_object_id
    })

    if not table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )

    active_orders = get_table_order_details(
        table.get("table_number", ""),
        table.get(
            "last_cleared_at",
            table.get("created_at")
        )
    )

    if not active_orders:
        raise HTTPException(
            status_code=400,
            detail="This table has no occupied orders to clear"
        )

    unfinished_orders = [
        order for order in active_orders
        if not order["can_clear"]
    ]

    if unfinished_orders:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot clear this table yet. "
                "All restaurant orders must be completed first."
            )
        )

    cleared_time = datetime.now(timezone.utc)

    tables_collection.update_one(
        {"_id": table_object_id},
        {
            "$set": {
                "manual_status": "Available",
                "last_cleared_at": cleared_time
            }
        }
    )

    return {
        "message": "Table cleared successfully",
        "table_number": table.get("table_number", ""),
        "status": "Available"
    }


# DELETE SHARED TABLE

@router.delete("/{restaurant_id}/tables/{table_id}")
async def delete_shared_table(
    restaurant_id: str,
    table_id: str
):

    check_restaurant_exists(restaurant_id)

    if not ObjectId.is_valid(table_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid table ID"
        )

    table_object_id = ObjectId(table_id)

    table = tables_collection.find_one({
        "_id": table_object_id
    })

    if not table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )

    active_orders = get_table_order_details(
        table.get("table_number", ""),
        table.get(
            "last_cleared_at",
            table.get("created_at")
        )
    )

    if active_orders:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a table with orders in its current session"
        )

    tables_collection.delete_one({
        "_id": table_object_id
    })

    return {
        "message": "Table deleted successfully",
        "table_id": table_id
    }


# ==========================================================
# DELETE FOOD
# ==========================================================

@router.delete("/foods/{food_id}")
async def delete_food(food_id: str):

    if not ObjectId.is_valid(food_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid food ID"
        )

    food_object_id = ObjectId(food_id)

    existing_food = foods_collection.find_one({
        "_id": food_object_id
    })

    if not existing_food:
        raise HTTPException(
            status_code=404,
            detail="Food not found"
        )

    result = foods_collection.delete_one({
        "_id": food_object_id
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete food"
        )

    return {
        "message": "Food deleted successfully",
        "food_id": food_id
    }
   