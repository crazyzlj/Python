import pymongo
from pymongo import MongoClient
ip = "127.0.0.1"
port = 27017
conn = MongoClient(ip, port)
# print conn.database_names()
db = conn["model_dianbu2_30m_longterm"]
# print db.collection_names()
gfs = db["SPATIAL.files"]

