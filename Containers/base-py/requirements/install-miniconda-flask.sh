export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PATH=/opt/conda/bin:$PATH
mkdir /var/uwsgi

apt-get update --fix-missing
apt-get install -y curl supervisor bzip2

apt-get -qq update && apt-get -qq -y install curl 
curl -sSL https://repo.continuum.io/miniconda/Miniconda3-4.5.4-Linux-x86_64.sh -o /tmp/miniconda.sh 
bash /tmp/miniconda.sh -bfp /usr/local 
rm -rf /tmp/miniconda.sh 
conda install -y python=3 
conda update conda 
apt-get -qq -y remove curl bzip2 
apt-get -qq -y autoremove 
apt-get autoclean 
rm -rf /var/lib/apt/lists/* /var/log/dpkg.log 
conda clean --all --yes

conda create -n ai4e_py_api python=3.6.6 
echo "source activate ai4e_py_api" >> ~/.bashrc 
conda install -c conda-forge -n ai4e_py_api uwsgi flask flask-restful