from fastapi import FastAPI, UploadFile, File
from typing import List
import cv2
import uuid
import numpy as np


app = FastAPI()

SAVE_PATH_OR = "app/static/originales/"

##Subir imagen al servidor
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Leer la imagen en color
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convertir a blanco y negro
        
        image_id = str(uuid.uuid4())

        cv2.imwrite(f"{SAVE_PATH_OR}ORIGINAL_{image_id}.jpg", gray_img)

        print(f"File '{file.filename}' guardado con id: {image_id}")
    return {"message": "Subida exitosamente"}



@app.get("/")
def read_root():
    return {"message": "¡Hola, FastAPI!"}