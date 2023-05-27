from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
import yaml


api_recambios = FastAPI()
mongo_client = MongoClient("mongodb://root:root@recambios_db:27017/")
taller = mongo_client["taller"]

origins = [
    "127.0.0.1:4000"
]

api_recambios.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS", "PUT", "DELETE"],
		allow_headers=["*"],
    max_age=3600,
)

@api_recambios.options("/api/v1/recambios")
async def get_supported_methods_without_param():
    # Cargar el documento openapi.yaml
    with open("openapi.yaml", "r") as file:
        openapi_data = yaml.safe_load(file)

    # Obtener la lista de métodos HTTP soportados del documento
    methods_data = openapi_data["paths"]["/recambios"]

    # Devolver la lista de métodos HTTP soportados
    return {
        "methods_without_param": methods_data
    }

@api_recambios.options("/api/v1/recambios/{numero_serie}")
async def get_supported_methods():
    # Cargar el documento openapi.yaml
    with open("openapi.yaml", "r") as file:
        openapi_data = yaml.safe_load(file)

    # Obtener la lista de métodos HTTP soportados del documento
    methods_data = openapi_data["paths"]["/recambios/{Numero_Serie}"]

    # Devolver la lista de métodos HTTP soportados
    return {
        "methods_with_param": methods_data,
    }

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

@api_recambios.get('/api/v1/recambios/{numero_serie}')
async def obtener_recambio(numero_serie: str):
    recambios_cur = taller["recambios"].find({"numero_serie": numero_serie}, {"_id": 0})
    recambios = {
        "recambios": [recambio for recambio in recambios_cur],
    }
    if not recambios:
        raise HTTPException(status_code=404, detail="No se encuentra el recambio")
    recambioOut = {"recambios": recambios}
    return recambioOut

@api_recambios.delete('/api/v1/recambios/{numero_serie}')
async def delete_recambio(numero_serie: str):
    # Buscar el objeto con el número de serie en la colección
    recambios_cur = taller["recambios"].find({"numero_serie": numero_serie}, {"_id": 0})

    if recambios_cur:
        # Eliminar el objeto de la colección
        taller["recambios"].delete_one({"numero_serie": numero_serie})
        return {"message": "Recambio eliminado correctamente"}
    else:
        # No se encontró ningún objeto con el número de serie proporcionado
        raise HTTPException(status_code=404, detail="Recambio no encontrado")

@api_recambios.post('/api/v1/recambios')
async def add_recambio(recambio: dict):
    # Comprobar si falta el atributo obligatorio "numero_serie"
    if "numero_serie" not in recambio:
        raise HTTPException(status_code=422, detail="Falta el atributo obligatorio 'numero_serie'")

    numero_serie = recambio["numero_serie"]

    # Comprobar si el número de serie ya existe en la colección
    recambios_cur = taller["recambios"].find({"numero_serie": numero_serie}, {"_id": 0})
    if recambios_cur:
        raise HTTPException(status_code=400, detail="El número de serie especificado ya existe")

    # Insertar el nuevo objeto en la colección
    taller["recambios"].insert_one(recambio)
    return {"message": "Recambio añadido correctamente"}

@api_recambios.put('/api/v1/recambios/{numero_serie}')
async def update_recambio(numero_serie: str, recambio_data: dict):
    # Comprobar si falta el atributo obligatorio "numero_serie" en el body
    if "numero_serie" not in recambio_data:
        raise HTTPException(status_code=422, detail="Falta el atributo obligatorio 'numero_serie'")

    # Verificar si el número de serie existe en la colección
    recambios_cur = taller["recambios"].find({"numero_serie": numero_serie}, {"_id": 0})
    if not recambios_cur:
        raise HTTPException(status_code=404, detail="Recambio no encontrado")

    # Actualizar el objeto en la colección
    taller["recambios"].update_one({"numero_serie": numero_serie}, {"$set": recambio_data})

    return {"message": "Recambio actualizado correctamente"}