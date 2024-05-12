import cv2


def cargarImagen(ruta):
    try:
        img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError("No se pudo cargar la imagen. Verifica la ruta."+ruta)
        return img
    except Exception as e:
        raise e