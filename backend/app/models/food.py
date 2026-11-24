
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class FoodCreate(BaseModel):
    model_config = ConfigDict(extra="allow")

    food_name: str
    food_type: str
    category: str
    description: str = ""

    price: float = Field(gt=0)

    image: str = ""
    images: list[str] = Field(default_factory=list)

    available: bool

    preparation_time: int = 15

    ingredients: list[str] = Field(default_factory=list)

    customization: dict[str, Any] = Field(default_factory=dict)

    is_todays_special: bool = False
    is_bestseller: bool = False
    is_chef_special: bool = False
    is_restaurant_special: bool = False

    discount: dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": False,
            "percentage": 0,
            "start_date": "",
            "end_date": ""
        }
    )
