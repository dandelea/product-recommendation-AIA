sudo apt-get update
sudo apt-get install python3.4-dev -y
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo rm get-pip.py
pip install -r requirements.txt
sudo wget https://www.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.8.16.tar.gz
tar xzvf hdf5-1.8.16.tar.gz
cd hdf5-1.8.16
./configure
sudo make install
export HDF5_DIR=~/hdf5
sudo apt-get build-dep python-tables -y
sudo pip install tables
sudo wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.3.tar.gz
tar xzf mysql-connector-python-2.1.3.tar.gz
cd mysql-connector-python-2.1.3.tar.gz
sudo python3 setup.py install