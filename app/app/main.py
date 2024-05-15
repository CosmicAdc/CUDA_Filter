import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException,Request
import cv2
import numpy as np
import uuid
from .sobel import filtroSobel, FiltroSobelParams
from .gauss import filtroGauss, FiltroGaussParams
from .mediana import filtroMediana, FiltroMedianaParams
from typing import List
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(static_directory="app/static")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

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

        cv2.imwrite(f"{SAVE_PATH_ORIGINAL}{filename}.jpg", gray_img)

        print(f"File '{file.filename}' guardado")
    return {"message": "Subida exitosamente"}


@app.post("/filtroSobel/")
async def filtro_sobel(params: FiltroSobelParams):
    mascara = params.mascara
    bloques_x = params.bloques_x
    bloques_y = params.bloques_y
    path_file = params.path_file


    path=SAVE_PATH_ORIGINAL+str(path_file)
    imagenFinal, tiempo , bloques, grids ,ancho , alto  ,grids_verdaderos = filtroSobel(path,bloques_x,bloques_y,mascara)

    path_final=SAVE_PATH_SOBEL+'Sobel-'+str(mascara)+'-'+str(path_file)
    cv2.imwrite(path_final, imagenFinal)

    return {"ruta_imagen": path_final, "tiempo": tiempo, "filtro":"Sobel X","bloques": bloques, "grids": grids,"ancho": ancho, "alto": alto,"grids_verdaderos": grids_verdaderos }

@app.post("/Gauss/")
async def filtro_gauss(params: FiltroGaussParams):
    mascara = params.mascara
    bloques_x = params.bloques_x
    bloques_y = params.bloques_y
    path_file = params.path_file


    path=SAVE_PATH_ORIGINAL+str(path_file)
    imagenFinal, tiempo , bloques, grids ,ancho , alto, grids_verdaderos = filtroGauss(path,bloques_x,bloques_y,mascara)

    path_final=SAVE_PATH_GAUSS+'Gauss-'+str(mascara)+'-'+str(path_file)
    cv2.imwrite(path_final, imagenFinal)

    return {"ruta_imagen": path_final, "tiempo": tiempo, "filtro":"Gauss","bloques": bloques, "grids": grids,"ancho": ancho, "alto": alto,"grids_verdaderos": grids_verdaderos}

@app.post("/Mediana/")
async def filtro_gauss(params: FiltroMedianaParams):
    mascara = params.mascara
    bloques_x = params.bloques_x
    bloques_y = params.bloques_y
    path_file = params.path_file


    path=SAVE_PATH_ORIGINAL+str(path_file)
    imagenFinal, tiempo , bloques, grids ,ancho , alto ,grids_verdaderos = filtroMediana(path,bloques_x,bloques_y,mascara)

    path_final=SAVE_PATH_MEDIANA+'mediana-'+str(mascara)+'-'+str(path_file)
    cv2.imwrite(path_final, imagenFinal)

    return {"ruta_imagen": path_final, "tiempo": tiempo, "filtro":"Mediana","bloques": bloques, "grids": grids,"ancho": ancho, "alto": alto,"grids_verdaderos": grids_verdaderos}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)