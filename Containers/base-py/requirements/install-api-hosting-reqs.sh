export LANG=C.UTF-8
export LC_ALL=C.UTF-8

mkdir /var/uwsgi

apt-get update --fix-missing
apt-get install -y apt-utils
apt-get install -y supervisor

apt-get install -y curl bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 git mercurial subversion
apt-get clean

echo 'export PATH=/usr/local/miniconda/bin:$PATH' > /etc/profile.d/conda.sh 
curl -sSL https://repo.continuum.io/miniconda/Miniconda3-4.5.4-Linux-x86_64.sh -o /tmp/miniconda.sh 
bash /tmp/miniconda.sh -bfp /usr/local
rm -rf /tmp/miniconda.sh 

export PATH=/usr/local/miniconda/bin:$PATH
export CONDA_AUTO_UPDATE_CONDA=false
export CONDA_DEFAULT_ENV=ai4e_py_api
export CONDA_PREFIX=/usr/local/miniconda/envs/$CONDA_DEFAULT_ENV
export PATH=$CONDA_PREFIX/bin:$PATH

# Create a Python 3.6 environment
conda install conda-build 
conda create -y --name ai4e_py_api python=3.6.6 
conda clean -ya




#/opt/conda/bin/conda clean -tipsy
#ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh 
#echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc 
#echo "conda activate base" >> ~/.bashrc 
#find /opt/conda/ -follow -type f -name '*.a' -delete 
#find /opt/conda/ -follow -type f -name '*.js.map' -delete 
#/opt/conda/bin/conda clean -afy


#conda install -y python=3 

#conda create -n ai4e_py_api python=3.6.6
#mkdir -p /usr/local/envs/ai4e_py_api/bin
#ln /opt/conda/envs/ai4e_py_api/bin/pip /usr/local/envs/ai4e_py_api/bin/pip
echo "source activate ai4e_py_api" >> ~/.bashrc 
conda install -c conda-forge -n ai4e_py_api uwsgi flask flask-restful