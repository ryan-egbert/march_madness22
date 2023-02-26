import pymongo

def get_collection(collection_name):
    client = pymongo.MongoClient("mongodb+srv://ryanegbert15:admin@marchmadness.umglste.mongodb.net/?retryWrites=true&w=majority")
    db = client.marchmadness
    return db[collection_name]