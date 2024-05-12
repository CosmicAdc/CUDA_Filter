import pycuda
import numpy as np
import cv2
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
from .utils import cargarImagen
from pydantic import BaseModel
import time


class FiltroSobelParams(BaseModel):
    mascara: int
    bloques_x: int
    bloques_y: int
    path_file: str



def creaciónMODCUDA(TAM_MASCARA):
    FILTER_SIZE = int(TAM_MASCARA)
    modSOBEL = SourceModule("""
    #define FILTER_SIZE {TAM_MASCARA}
    __constant__ int d_M[FILTER_SIZE][FILTER_SIZE];
    __global__ void sobelFilter(const unsigned char* input, unsigned char* output, int width, int height)
    {{
        int x = blockIdx.x * blockDim.x + threadIdx.x;
        int y = blockIdx.y * blockDim.y + threadIdx.y;
        if (x < width && y < height) {{
            int sum = 0;
            int radius = FILTER_SIZE / 2;
            for (int i = -radius; i <= radius; i++) {{
                for (int j = -radius; j <= radius; j++) {{
                    int pixelX = x + j;
                    int pixelY = y + i;

                    int index = pixelY * width + pixelX;
                    sum += input[index] * d_M[i + radius][j + radius];
                }}
            }}
            output[y * width + x] = abs(sum);
        }}
    }}
    """.format(TAM_MASCARA=FILTER_SIZE))

    return modSOBEL


def crear_mascaras_sobel(tamano):
    mitad = tamano // 2
    mascaraX = np.zeros((tamano, tamano), dtype=np.int32)
    for y in range(tamano):
        for x in range(tamano):
            mascaraX[y][x] = x - mitad
    return mascaraX



def filtroSobel(path,BloqueX,BloqueY,mascara):

    mod= creaciónMODCUDA(mascara)
    matriz_mascara = crear_mascaras_sobel(mascara)
    mascara_flat = matriz_mascara.flatten().tolist()
    imagen= cargarImagen(path)
    alto, ancho = imagen.shape

    blocks = (BloqueX, BloqueY,1)

    num_grids = ((ancho + blocks[0] - 1) // blocks[0],
              (alto + blocks[1] - 1) // blocks[1],1)


    d_M = mod.get_global('d_M')[0]

    cuda.memcpy_htod(d_M, np.array(mascara_flat, dtype=np.int32))
    d_input = cuda.mem_alloc(ancho * alto * np.dtype(np.uint8).itemsize)
    d_output = cuda.mem_alloc(ancho * alto * np.dtype(np.uint8).itemsize)

    cuda.memcpy_htod(d_input, imagen)

    func = mod.get_function("sobelFilter")
    startGPU = time.time()
    func(d_input, d_output, np.int32(ancho), np.int32(alto), block=blocks, grid=num_grids)
    cuda.Context.synchronize()
    endGPU = time.time()

    tiempo=(endGPU - startGPU)

    outputImageGPU = np.empty((alto, ancho), dtype=np.uint8)
    cuda.memcpy_dtoh(outputImageGPU, d_output)

    return outputImageGPU, tiempo


    