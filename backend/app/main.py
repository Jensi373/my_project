
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



from app.routes import restaurant, food, ai, feedback
app = FastAPI(
    title="AI Food Management API",
    description="Restaurant Management and Local AI Analytics",
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Existing modules
app.include_router(restaurant.router)
app.include_router(food.router)

# AI module
app.include_router(ai.router)
app.include_router(feedback.router)

@app.get("/")
async def root():

    return {
        "success": True,
        "message": "AI Food Management API is running"
    }


@app.get("/api/test")
async def test_api():

    return {
        "success": True,
        "message": "Backend API working"
    }
