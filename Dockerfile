FROM nvidia/cuda:12.2.2-devel-ubi8


# Instalamos las dependencias necesarias para compilar Python
RUN yum install -y make gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget

# Descargamos el código fuente de Python 3.10
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz && \
    tar xvf Python-3.10.0.tgz && \
    cd Python-3.10.0 && \
    ./configure --enable-optimizations && \
    make altinstall

# Limpiamos los archivos temporales
RUN rm -rf Python-3.10.0*

# Actualizamos pip
RUN python3.10 -m pip install --upgrade pip

# Instalamos npm y otras dependencias
# Agrega el repositorio que contiene la versión específica de npm
RUN curl -sL https://rpm.nodesource.com/setup_20.x | bash -

# Instala npm desde el repositorio
RUN yum install -y nodejs
RUN yum install -y libglvnd-glx
RUN npm install -g @angular/cli

COPY . /app
WORKDIR /app
RUN python3.10 -m pip install poetry==1.6.1


RUN npm install /app/front_cuda

WORKDIR /app               # Regresamos al directorio principal

# Exponemos el puerto 4200 para acceder a la aplicación Angular
EXPOSE 4200
EXPOSE 8000
WORKDIR /app/app
RUN poetry install
WORKDIR /app
# Ejecutamos ng serve para iniciar el servidor de desarrollo de Angular
CMD ["/bin/bash", "/app/start.sh"]
