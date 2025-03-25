
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import csv
import json


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
collection.delete_many({})

new_data = {}

with open("backend/F25SearchResults/combinedResults.json", "r") as results, open("backend/catalog.csv") as file:
    old_data = csv.DictReader(file)
    db_data = {}
    for row in old_data:
        db_data[row["prefix"] + row["code"]] = row
        
    
    data = json.load(results)
    for i in data["data"]:
        if i["subject"] not in new_data:
            new_data[i["subject"]] = {}
        if i["courseNumber"] not in new_data[i["subject"]]:
            if i["subject"] + i["courseNumber"] not in db_data:
                new_data[i["subject"]][i["courseNumber"]] = {
                    "subject": i["subject"],
                    "courseNumber": i["courseNumber"],
                    "courseTitle": i["courseTitle"],
                    "courseDescription": "Unknown",
                    "creditHours": i["creditHours"],
                    "prerequisites": "Unknown",
                    "corequisites": "Unknown",
                    "classes": []
                }
            else:
                new_data[i["subject"]][i["courseNumber"]] = {
                    "subject": i["subject"],
                    "courseNumber": i["courseNumber"],
                    "courseTitle": db_data[i["subject"] + i["courseNumber"]]["course name"],
                    "courseDescription": db_data[i["subject"] + i["courseNumber"]]["description"],
                    "creditHours": db_data[i["subject"] + i["courseNumber"]]["credit hours"],
                    "prerequisites": db_data[i["subject"] + i["courseNumber"]]["prereqs"],
                    "corequisites": db_data[i["subject"] + i["courseNumber"]]["coreqs"],
                    "classes": []
                }
        
        new_data[i["subject"]][i["courseNumber"]]["classes"].append(i)
    
data_array = [course for subject in new_data.values() for course in subject.values()]

collection.insert_many(data_array)
    
client.close()





      



