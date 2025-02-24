
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import csv


uri = "mongodb+srv://root:root@cluster0.cnbie.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    exit()
    
db = client.classes


collection_name = "course"
collection = db[collection_name]

with open("catalog.csv", 'r') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    
    for row in csvreader:
        prefix, code, course_name, description, credit_hours, pre_req, core_req = row
        doc = {
            "prefix": prefix,
            "code": code,
            "course_name": course_name,
            "description": description,
            "credit_hours": credit_hours,
            "pre_req": pre_req,
            "core_req": core_req
        }
        collection.insert_one(doc)

client.close()





      



