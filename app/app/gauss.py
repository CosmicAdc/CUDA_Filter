import pycuda
import numpy as np
import cv2
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
from .utils import cargarImagen
from pydantic import BaseModel
import time


class FiltroGaussParams(BaseModel):
    mascara: int
    bloques_x: int
    bloques_y: int
    path_file: str



def creaciónMODCUDA(TAM_MASCARA):
    FILTER_SIZE = int(TAM_MASCARA)
    # Kernel CUDA
    modGaussian = SourceModule("""
    #define FILTER_SIZE {TAM_MASCARA}
    #define FILTER_RADIUS (FILTER_SIZE/2)
    __constant__ float d_K[FILTER_SIZE][FILTER_SIZE];

    __global__ void gaussianFilter(const unsigned char* input, unsigned char* output, int width, int height)
    {{
        int x = blockIdx.x * blockDim.x + threadIdx.x;
        int y = blockIdx.y * blockDim.y + threadIdx.y;

        if (x < width && y < height) {{
            float sum = 0.0;
            float value = 0.0;

            for (int i = -FILTER_RADIUS; i <= FILTER_RADIUS; ++i) {{
                for (int j = -FILTER_RADIUS; j <= FILTER_RADIUS; ++j) {{
                    int offsetX = x + j;
                    int offsetY = y + i;

                    if (offsetX >= 0 && offsetX < width && offsetY >= 0 && offsetY < height) {{
                        float weight = d_K[i + FILTER_RADIUS][j + FILTER_RADIUS];
                        value += weight * input[offsetY * width + offsetX];
                        sum += weight;
                    }}
                }}
            }}

            output[y * width + x] = static_cast<unsigned char>(value / sum);
        }}
    }}
    """.format(TAM_MASCARA=TAM_MASCARA))


    return modGaussian


def create_gaussian_blur_kernel(size, sigma):
    kernel = np.zeros((size, size), dtype=np.float32)
    sum = 0.0
    half = size // 2

    for i in range(-half, half + 1):
        for j in range(-half, half + 1):
            value = np.exp(-(i * i + j * j) / (2 * sigma * sigma))
            kernel[i + half][j + half] = value
            sum += value

    # Normalizar el kernel
    kernel /= sum

    return kernel



def filtroGauss(path,BloqueX,BloqueY,mascara):

    mod= creaciónMODCUDA(mascara)
    matriz_mascara = create_gaussian_blur_kernel(mascara,100)


    mascara_flat = matriz_mascara.flatten().tolist()
    imagen= cargarImagen(path)
    alto, ancho = imagen.shape

    blocks = (BloqueX, BloqueY,1)

    num_grids = ((ancho + blocks[0] + 1) // blocks[0],
              (alto + blocks[1] + 1) // blocks[1],1)


   # Copiar el kernel a la memoria de la GPU
    gaussian_kernel_flat = matriz_mascara.flatten().tolist()
    d_K = mod.get_global('d_K')[0]
    cuda.memcpy_htod(d_K, np.array(gaussian_kernel_flat, dtype=np.float32))

    # Reservar memoria en la GPU para la imagen de entrada y salida
    d_input = cuda.mem_alloc(imagen.nbytes)
    d_output = cuda.mem_alloc(imagen.nbytes)

    # Copiar la imagen de entrada a la memoria de la GPU
    cuda.memcpy_htod(d_input, imagen)


    func = mod.get_function("gaussianFilter")
    startGPU = time.time()
    func(d_input, d_output, np.int32(ancho), np.int32(alto), block=blocks, grid=num_grids)
    cuda.Context.synchronize()
    endGPU = time.time()

    tiempo=(endGPU - startGPU)

    outputImageGPU = np.empty((alto, ancho), dtype=np.uint8)
    cuda.memcpy_dtoh(outputImageGPU, d_output)

    bloques=int(BloqueX)*int(BloqueY)
    grids=((ancho + blocks[0] - 1)+1 // blocks[0]) * ((alto + blocks[1] - 1)+1 // blocks[1])
    grids_verdaderos=((ancho + blocks[0] - 1)+1 + (blocks[0]) * (alto + blocks[1] - 1)+1)
    
    return outputImageGPU, tiempo ,bloques , grids , ancho , alto,grids_verdaderos


    