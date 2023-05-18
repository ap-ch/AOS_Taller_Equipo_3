from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pymongo.mongo_client import MongoClient

api_recambios = FastAPI()
mongo_client = MongoClient("mongodb://root:root@recambios_db:27017/")
taller = mongo_client["taller"]


@api_recambios.get("/api/v1/recambios")
async def lista_recambios(page: int = 0):
    recambios_cur = taller["recambios"].find({}, {"_id": 0}).skip(page).limit(10)
    recambios = {
        "recambios": [recambio for recambio in recambios_cur],
        "links": {
            "nextPage": { "href": "http://127.0.0.1:4000/api/v1/recambios?page=1", "rel": "nextPage" }
        } if page == 0 else \
        {
            "prevPage": { "href": f"http://127.0.0.1:4000/api/v1/recambios?page={page-1}", "rel": "prevPage" },
            "nextPage": { "href": f"http://127.0.0.1:4000/api/v1/recambios?page={page+1}", "rel": "nextPage" }
        }
    }
    return recambios