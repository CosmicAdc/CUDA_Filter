import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException,Request
import cv2
import numpy as np
import uuid
from .sobel import filtroSobel, FiltroSobelParams
from typing import List
import os

app = FastAPI()

SAVE_PATH_ORIGINAL = "app/static/originales/"
SAVE_PATH_SOBEL = "app/static/sobel/"
SAVE_PATH_GAUSS = "app/static/gauss/"
SAVE_PATH_MEDIANA = "app/static/mediana/"



##Subir imagen al servidor
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Leer la imagen en color
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convertir a blanco y negro

        filename = os.path.splitext(file.filename)[0]

        cv2.imwrite(f"{SAVE_PATH_ORIGINAL}{filename}-ORIGINAL.jpg", gray_img)

        print(f"File '{file.filename}' guardado")
    return {"message": "Subida exitosamente"}


@app.post("/filtroSobel/")
async def filtro_sobel(params: FiltroSobelParams):
    mascara = params.mascara
    bloques_x = params.bloques_x
    bloques_y = params.bloques_y
    path_file = params.path_file

    path=SAVE_PATH_ORIGINAL+str(path_file)
    imagenFinal, tiempo = filtroSobel(path,bloques_x,bloques_y,mascara)

    path_final=SAVE_PATH_SOBEL+'-Sobel-'+str(mascara)+'.jpg'
    cv2.imwrite(path_final, imagenFinal)

    return {"tiempo de ejecución":  tiempo }



@app.get("/")
def read_root():
    return {"message": "¡Hola, FastAPI!"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)