import pymongo

client = pymongo.MongoClient("localhost", 27017)

db = client["Doofenshmirtz"]

collectionUser = db["User"]
collectionExam = db["Exam"]
collectionCategory = db["Category"]
