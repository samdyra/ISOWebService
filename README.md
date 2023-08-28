## Running the server locally


Install the required dependencies:

```
python -m pip install -r requirements.txt
```

Start the server:
```
source env/bin/activate
python -m uvicorn main:app --reload
```

from docker
```
docker build -t isoappservice .   
docker run -p 8000:8000 isoappservice 
```

When the application starts, navigate to `http://localhost:8000/docs` and try out the `book` endpoints.

## Running the tests

Install `pytest`:

```
python -m pip install pytest
```

Execute the tests:

```
python -m pytest
```

## create virtual environtment

```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
uvicorn main:app --reload
```

## Run EC2 Instance (https://www.youtube.com/watch?v=SgSnz7kW-Ko)
## Contact Code Owner (Sam) for server configs

```
chmod 400 hydroservice.pem
```

Run on terminal

```
ssh -i "hydroservice.pem" ubuntu@ec2-54-153-240-138.ap-southeast-2.compute.amazonaws.com

```

install dependency "Already done"

```
sudo apt-get update
```

Install python and nginx

```
sudo apt install -y python3-pip nginx
```

configure nginx on server

```
sudo cat /etc/nginx/sites-enabled/fastapi_nginx
```

restart nginx

```
sudo service nginx restart
```

install requirements.txt

```
pip3 install -r requirements.txt
```

run app on ec2 instance

```
cd ISOWebService
./start.sh
```

public ip4 address

```
http://ec2-54-153-240-138.ap-southeast-2.compute.amazonaws.com:8000/docs
```
## configure supervisor (https://www.youtube.com/watch?v=E5IhKYT7ecU&t=213s)

configure
```
cd /etc/supervisor/conf.d/
sudo vi hydrowebservice.conf
```

check health supervisor

```
sudo service supervisor status
```

refresh supervisor
```
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
```

check health workers
```
sudo supervisorctl
cat -n /var/log/supervisor/hydroapi_error.log
```

stop all worker

```
sudo supervisorctl stop all 
```