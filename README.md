# AcmeSupermarketRecommenderAIA
Aplicación de recomendación para la tarea 03 de AIA (Aplicaciones de Inteligencia Artificial) del Máster de Ingeniería Informática de la Universidad de Sevilla.

Contiene un ejercicio de filtrado colaborativo basado en items o en usuarios (/filter) y un ejercicio de extracción de reglas de compras (/rules).

## Prerequisitos

Instalar con
```
./install.sh
```

...o bien...

* Actualizar las bases de datos de repositorios
 * `sudo apt-get update`
* Instalar Python 3.4:
 * `sudo apt-get install python3.4-dev`
* Instalar pip:
 * `cd ~`
 * `wget https://bootstrap.pypa.io/get-pip.py`
 * `sudo python3 get-pip.py`
* Instalar numpy, scipy y pymongo
 * `pip install numpy`
 * `pip install scipy`
 * `pip install pymongo`
* Instalar pytables y hdf5
 * `cd ~`
 * `sudo wget https://www.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.8.16.tar.gz`
 * `tar xzvf hdf5-1.8.16.tar.gz`
 * `cd hdf5-1.8.16`
 * `./configure`
 * `sudo make install`
 * `export HDF5_DIR=~/hdf5`
 * `sudo apt-get build-dep python-tables`
 * `sudo pip install tables`
* Instalar MySQL Connector
 * `sudo wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.3.tar.gz`
 * `tar xzf mysql-connector-python-2.1.3.tar.gz`
 * `cd mysql-connector-python-2.1.3.tar.gz`
 * `sudo python3 setup.py install`

## Desarrollado por
* Daniel de los Reyes Leal
* Alejandro Sánchez Medina