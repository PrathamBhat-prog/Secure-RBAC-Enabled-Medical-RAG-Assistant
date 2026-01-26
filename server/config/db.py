import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()
MONGO_URI=os.getenv("MONGO_URI")
DB_NAME=os.getenv("DB_NAME")


import certifi

# Using standard connection with certifi for SSL
client=MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db=client[DB_NAME]
users_collection=db["users"]