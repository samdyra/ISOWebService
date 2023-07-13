## Running the server


Install the required dependencies:

```
python -m pip install -r requirements.txt
```

Start the server:
```
python -m uvicorn main:app --reload
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

## Run EC2 Instance (https://www.youtube.com/watch?v=SgSnz7kW-Ko)
```
chmod 400 hydroapi_key.pem
```

Run on terminal

```
ssh -i "hydroapi_key.pem" ubuntu@ec2-3-106-125-16.ap-southeast-2.compute.amazonaws.com
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