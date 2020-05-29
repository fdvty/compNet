# SmartClinic

A project for 2020 PKU Computer Network. We build a new way to manage patients and clinical records. A neural 
network prediction model is added to help you quickly identify COVID-19 carriers. 

This project is based on Flask + Pytorch + Nginx + Gunicorn + Docker.

We have deployed this project [here](https://39.97.247.225/).

## File Structure

Here we explain the core documents in our project. 

* **app** : The Flask APP

app              
├── __init__.py     // initialize Flask app
├── email.py        // send the reset password email
├── errors.py       // handle 404 and 505 errors
├── evaluator       // the neural network prediction model
├── forms.py        // define the forms
├── models.py       // define the classes used in database
├── routes.py       // routers, implement functions for different URLs
├── static          // static resources used by HTML templates
├── templates       // html templates and mail templates
└── utils.py        // assisting functions for routers

* **config.py** : The parameters used in this project
* **requirements.txt** : The package requirements in this project


## Deployment

We first show how to deploy our project using Docker.
 
We also provide a version without Docker.

### Setup(Docker Version)

#### Installation

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

   Refer [Docker's official website](https://docs.docker.com/get-docker/) for more details.

2. Download image from  [Docker Hub](https://hub.docker.com/).

   ~~~shell
   docker pull primavera/compnet
   ~~~

####Usage

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

### Setup(without Docker Version)

#### Requirement

See file `requirements.txt`

#### Installation

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

## Demos

Here shows some of the operations. 



## Authors

* Zirui Liu, Wentao Wang, Xinyu Di


