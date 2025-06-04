from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://edwardnguyen:sonbn123456789@edwardcluster.xwrohj5.mongodb.net/?retryWrites=true&w=majority&appName=EdwardCluster"

client = MongoClient(uri, server_api=ServerApi('1'))


db = client.book_db
collection = db["book_data"]
users_collection = db["users"]   