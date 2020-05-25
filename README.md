# SmartClinic

A project for 2020 PKU Computer Network.

This project is based on Flask + Nginx + Gunicorn + Docker.  

We also provide a version without Docker.

## Setup(Docker Version)

### Installation

1. Install Docker.

   ~~~shell
   #Uninstall old versions
   sudo apt-get remove docker docker-engine docker.io containerd runc
   #Setup the repository
   sudo apt-get update
   
   sudo apt-get install \
       apt-transport-https \
       ca-certificates \
       curl \
       gnupg-agent \
       software-properties-common
   #Add Docker's official GPG key
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   #Install Docker Engine
   sudo apt update
   sudo apt install docker-ce docker-ce-cli containerd.io
   ~~~

   Refer this document for more details.

2. Download image from  [Docker Hub](https://hub.docker.com/).

   ~~~shell
   docker pull primavera/compnet
   ~~~

### Usage

1. Create a container from the image.

~~~shell
docker run -it -p 80:80 --name new_compnet primavera/compnet
~~~

2. Enter the directory.

~~~shell
cd /deploy/compNet/
~~~

3. Start Nginx.

~~~shell
service nginx start
~~~

4. Start Gunicorn.

~~~shell
gunicorn -w 4 -b 127.0.0.1:8000 app:app
~~~

----

## Setup(without Docker Version)

### Requirement

See file `requirements.txt`

### Installation

1. Install virtualenv.

~~~shell
pip3 install virtualenv
~~~

2. Install dependence.

~~~shell
pip3 install -r requirements.txt
~~~

3. Install Pytorch.

Select a proper version of Pytorch on [this website](https://pytorch.org/get-started/locally/).

3. Setup Nginx.

Replace `default.conf` in `/etc/nginx/sites-enabled/` by `compNet.conf`.

~~~shell
mv ./compNet.conf /etc/nginx/sites-enabled/
~~~

5. Activate virtual environment.

~~~shell
source ./venv/bin/activate
~~~

6. Start Gunicorn.

~~~shell
gunicorn -w 4 -b 127.0.0.1:8000 app:app
~~~



