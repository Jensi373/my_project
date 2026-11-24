
from pydantic import BaseModel, EmailStr, Field


# ==========================================================
# RESTAURANT REGISTER MODEL
# ==========================================================

class RestaurantRegister(BaseModel):
    restaurantName: str
    ownerName: str
    email: EmailStr
    phone: str
    password: str
    confirmPassword: str
    address: str

    # Restaurant logo (Base64 image)
    logo: str = ""

    # Restaurant theme customization
    theme: dict = Field(
        default_factory=lambda: {
            "themeName": "terracotta",
            "primaryColor": "#c65d3a",
            "secondaryColor": "#e7a66a",
            "backgroundColor": "#faf7f2",
            "cardColor": "#ffffff",
            "textColor": "#292524",
        }
    )


# ==========================================================
# RESTAURANT LOGIN MODEL
# ==========================================================

class RestaurantLogin(BaseModel):
    email: EmailStr
    password: str
