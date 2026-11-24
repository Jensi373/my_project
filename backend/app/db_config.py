# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os

# load_dotenv()

# MONGODB_URL = os.getenv("MONGODB_URL")
# DATABASE_NAME = os.getenv("DATABASE_NAME")

# if not MONGODB_URL:
#     raise ValueError("MONGODB_URL is not found in .env")

# if not DATABASE_NAME:
#     raise ValueError("DATABASE_NAME is not found in .env")


# # Create client
# client = MongoClient(
#     MONGODB_URL,
#     serverSelectionTimeoutMS=5000
# )

# # Database object
# db = client[DATABASE_NAME]


# # Function to test connection
# def check_database_connection():
#     try:
#         client.admin.command("ping")
#         return True, "MongoDB Atlas Connected Successfully!"

#     except Exception as e:
#         return False, str(e)


# # Test connection when backend starts
# connected, message = check_database_connection()

# if connected:
#     print("✅", message)
#     print(f"📁 Database: {DATABASE_NAME}")
# else:
#     print("❌ MongoDB Connection Failed!")
#     print("Error:", message)



from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL is not found in .env")

if not DATABASE_NAME:
    raise ValueError("DATABASE_NAME is not found in .env")


# ==========================================================
# CREATE MONGODB CLIENT
# ==========================================================

client = MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=20000,
    socketTimeoutMS=20000,
    tls=True
)


# ==========================================================
# DATABASE
# ==========================================================

db = client[DATABASE_NAME]


# ==========================================================
# COLLECTIONS
# ==========================================================

restaurants_collection = db["restaurants"]


# ==========================================================
# TEST DATABASE CONNECTION
# ==========================================================

def check_database_connection():

    try:
        client.admin.command("ping")

        return True, "MongoDB Atlas Connected Successfully!"

    except Exception as e:

        return False, str(e)


# ==========================================================
# TEST CONNECTION WHEN BACKEND STARTS
# ==========================================================

connected, message = check_database_connection()

if connected:

    print("✅", message)
    print(f"📁 Database: {DATABASE_NAME}")
    print("📂 Collection: restaurants")

else:

    print("❌ MongoDB Connection Failed!")
    print("Error:", message)

