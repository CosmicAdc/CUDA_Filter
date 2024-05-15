import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
from .utils import cargarImagen
from pydantic import BaseModel
import time


class FiltroMedianaParams(BaseModel):
    mascara: int
    bloques_x: int
    bloques_y: int
    path_file: str



def creaciónMODCUDA(TAM_MASCARA):
    FILTER_SIZE = int(TAM_MASCARA)
    modGaussian = SourceModule("""
    #define FILTER_SIZE {TAM_MASCARA}
    __constant__ int d_M[FILTER_SIZE][FILTER_SIZE];

    __global__ void medianFilter(const unsigned char* input, unsigned char* output, int width, int height)
    {{
        int x = blockIdx.x * blockDim.x + threadIdx.x;
        int y = blockIdx.y * blockDim.y + threadIdx.y;

        if (x < width && y < height) {{
            int half_window = FILTER_SIZE / 2;
            if (x < half_window || x >= width - half_window || y < half_window || y >= height - half_window) {{
                output[y * width + x] = input[y * width + x];
            }} else {{
                int window[FILTER_SIZE * FILTER_SIZE];
                int index = 0;
                for (int i = -half_window; i <= half_window; i++) {{
                    for (int j = -half_window; j <= half_window; j++) {{
                        int pixelX = x + j;
                        int pixelY = y + i;
                        window[index++] = input[pixelY * width + pixelX];
                    }}
                }}

                // Ordenar la ventana para encontrar la mediana (Algoritmo de ordenamiento de burbuja)
                for (int i = 0; i < FILTER_SIZE * FILTER_SIZE - 1; i++) {{
                    for (int j = 0; j < FILTER_SIZE * FILTER_SIZE - i - 1; j++) {{
                        if (window[j] > window[j + 1]) {{
                            int temp = window[j];
                            window[j] = window[j + 1];
                            window[j + 1] = temp;
                        }}
                    }}
                }}

                output[y * width + x] = window[FILTER_SIZE * FILTER_SIZE / 2];
            }}
        }}
    }}
    """.format(TAM_MASCARA=TAM_MASCARA))


    return modGaussian




def filtroMediana(path,BloqueX,BloqueY,mascara):

    mod= creaciónMODCUDA(mascara)
    imagen= cargarImagen(path)
    alto, ancho = imagen.shape
    blocks = (BloqueX, BloqueY,1)
    num_grids = ((ancho + blocks[0] + 1) // blocks[0],
              (alto + blocks[1] + 1) // blocks[1],1)
    # Crear espacio de memoria en GPU para la imagen de entrada y salida
    d_input = cuda.mem_alloc(ancho * alto * np.dtype(np.uint8).itemsize)
    d_output = cuda.mem_alloc(ancho * alto * np.dtype(np.uint8).itemsize)

    # Copiar la imagen de entrada a la GPU
    cuda.memcpy_htod(d_input, imagen)

    func = mod.get_function("medianFilter")
    startGPU = time.time()
    func(d_input, d_output, np.int32(ancho), np.int32(alto), block=blocks, grid=num_grids)
    cuda.Context.synchronize()
    endGPU = time.time()

    tiempo=(endGPU - startGPU)

    outputImageGPU = np.empty((alto, ancho), dtype=np.uint8)
    cuda.memcpy_dtoh(outputImageGPU, d_output)

    bloques=int(BloqueX)*int(BloqueY)
    grids=((ancho + blocks[0])+1 // blocks[0]) * ((alto + blocks[1])+1 // blocks[1])
    grids_verdaderos=((ancho + blocks[0])+1 + (blocks[0]) * (alto + blocks[1])+1)
    
    return outputImageGPU, tiempo ,bloques , grids , ancho , alto,grids_verdaderos


    