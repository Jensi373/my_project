
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from bson import ObjectId

from app.db_config import db
from app.models.feedback import FoodFeedbackCreate

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

orders_collection = db["orders"]
foods_collection = db["foods"]
feedback_collection = db["feedback"]
restaurants_collection = db["restaurants"]


# =====================================================
# HELPER: CONVERT ID TO STRING
# =====================================================

def normalize_id(value):
    if isinstance(value, ObjectId):
        return str(value)
    return str(value) if value is not None else ""


# =====================================================
# HELPER: GET RESTAURANT FEEDBACK
# SUPPORTS OLD AND NEW FEEDBACK
# =====================================================

def get_feedback_for_restaurant(restaurant_id):

    result = []

    # 1. GET NEW FEEDBACK
    new_feedbacks = list(
        feedback_collection.find({
            "restaurant_id": {
                "$in": [restaurant_id, ObjectId(restaurant_id)]
            }
        })
    )

    for feedback in new_feedbacks:
        feedback["_id"] = str(feedback["_id"])
        feedback["review_type"] = "Food review"

        if feedback.get("food_id"):
            feedback["food_id"] = normalize_id(
                feedback["food_id"]
            )

        result.append(feedback)

    # 2. GET OLD FEEDBACK WITHOUT RESTAURANT ID
    old_feedbacks = feedback_collection.find({
        "$or": [
            {"restaurant_id": {"$exists": False}},
            {"restaurant_id": None},
            {"restaurant_id": ""}
        ]
    })

    for feedback in old_feedbacks:

        order_id = feedback.get("order_id")

        if not order_id:
            continue

        if not ObjectId.is_valid(str(order_id)):
            continue

        order = orders_collection.find_one({
            "_id": ObjectId(str(order_id))
        })

        if not order:
            continue

        items = order.get("items", [])

        # Get unique food IDs from the order
        food_ids = list(set(
            normalize_id(item.get("food_id"))
            for item in items
            if item.get("food_id")
        ))

        # Only safely assign an old order-level review
        # when the order contains exactly one distinct food.
        if len(food_ids) != 1:
            continue

        food_id = food_ids[0]

        if not ObjectId.is_valid(food_id):
            continue

        food = foods_collection.find_one({
            "_id": ObjectId(food_id)
        })

        if not food:
            continue

        food_restaurant_id = normalize_id(
            food.get("restaurant_id")
        )

        # Match the food's restaurant with requested restaurant
        if food_restaurant_id != restaurant_id:
            continue

        ordered_item = next(
            (
                item for item in items
                if normalize_id(item.get("food_id")) == food_id
            ),
            {}
        )

        feedback["_id"] = str(feedback["_id"])
        feedback["restaurant_id"] = restaurant_id
        feedback["food_id"] = food_id

        feedback["food_name"] = ordered_item.get(
            "name",
            food.get("food_name", "Food")
        )

        feedback["category"] = ordered_item.get(
            "category",
            food.get("category", "")
        )

        feedback["review_type"] = "Order-level review"

        result.append(feedback)

    # Sort newest reviews first
    result.sort(
        key=lambda item: (
            item.get("created_at")
            if isinstance(item.get("created_at"), datetime)
            else datetime.min.replace(tzinfo=timezone.utc)
        ),
        reverse=True
    )

    return result


# =====================================================
# CUSTOMER: SUBMIT FOOD FEEDBACK
# =====================================================

@router.post("/submit")
async def submit_feedback(data: FoodFeedbackCreate):

    if not ObjectId.is_valid(data.order_id):
        raise HTTPException(400, "Invalid order ID")

    if not ObjectId.is_valid(data.food_id):
        raise HTTPException(400, "Invalid food ID")

    order = orders_collection.find_one({
        "_id": ObjectId(data.order_id)
    })

    if not order:
        raise HTTPException(404, "Order not found")

    if order.get("order_status") != "Completed":
        raise HTTPException(
            400,
            "Feedback can only be submitted for completed orders"
        )

    customer_id = order.get("customer_id")

    ordered_item = next(
        (
            item for item in order.get("items", [])
            if normalize_id(item.get("food_id")) == data.food_id
        ),
        None
    )

    if not ordered_item:
        raise HTTPException(
            400,
            "This food item does not belong to the selected order"
        )

    food = foods_collection.find_one({
        "_id": ObjectId(data.food_id)
    })

    if not food:
        raise HTTPException(404, "Food not found")

    restaurant_id = normalize_id(food.get("restaurant_id"))

    if not restaurant_id:
        raise HTTPException(
            400,
            "Restaurant information not found for this food"
        )

    existing = feedback_collection.find_one({
        "order_id": data.order_id,
        "food_id": data.food_id,
        "customer_id": customer_id
    })

    if existing:
        raise HTTPException(
            400,
            "You have already submitted feedback for this food item"
        )

    feedback = {
        "order_id": data.order_id,
        "order_number": order.get("order_number", ""),
        "customer_id": customer_id,
        "customer_name": order.get("customer_name", "Customer"),
        "customer_email": order.get("customer_email", ""),
        "restaurant_id": restaurant_id,
        "food_id": data.food_id,
        "food_name": ordered_item.get(
            "name",
            food.get("food_name", "Food")
        ),
        "category": ordered_item.get(
            "category",
            food.get("category", "")
        ),
        "rating": data.rating,
        "comment": data.comment or "",
        "created_at": datetime.now(timezone.utc)
    }

    result = feedback_collection.insert_one(feedback)

    return {
        "success": True,
        "message": "Food feedback submitted successfully",
        "feedback_id": str(result.inserted_id)
    }


# =====================================================
# RESTAURANT: GET OWN FOOD FEEDBACK
# =====================================================

@router.get("/restaurant/{restaurant_id}")
async def get_restaurant_feedback(restaurant_id: str):

    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(400, "Invalid restaurant ID")

    feedbacks = get_feedback_for_restaurant(restaurant_id)

    total_reviews = len(feedbacks)

    average_rating = (
        round(
            sum(int(item.get("rating", 0)) for item in feedbacks)
            / total_reviews,
            2
        )
        if total_reviews else 0
    )

    return {
        "success": True,
        "restaurant_id": restaurant_id,
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "feedbacks": feedbacks
    }


# =====================================================
# RESTAURANT: FOOD-WISE FEEDBACK SUMMARY
# =====================================================

@router.get("/restaurant/{restaurant_id}/food-summary")
async def get_food_feedback_summary(restaurant_id: str):

    if not ObjectId.is_valid(restaurant_id):
        raise HTTPException(400, "Invalid restaurant ID")

    feedbacks = get_feedback_for_restaurant(restaurant_id)

    summary = {}

    for feedback in feedbacks:

        food_id = feedback.get("food_id")

        if not food_id:
            continue

        if food_id not in summary:
            summary[food_id] = {
                "food_id": food_id,
                "food_name": feedback.get("food_name", "Food"),
                "total_reviews": 0,
                "total_rating": 0
            }

        summary[food_id]["total_reviews"] += 1
        summary[food_id]["total_rating"] += int(
            feedback.get("rating", 0)
        )

    result = []

    for item in summary.values():

        total = item["total_reviews"]

        result.append({
            "food_id": item["food_id"],
            "food_name": item["food_name"],
            "total_reviews": total,
            "average_rating": round(
                item["total_rating"] / total,
                2
            )
        })

    result.sort(
        key=lambda item: item["average_rating"],
        reverse=True
    )

    return {
        "success": True,
        "food_summary": result
    }
