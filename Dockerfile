FROM python:3.8

WORKDIR /isoappservice

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y libgdal-dev 

RUN python -m pip install numpy=="1.24.4"   

RUN python -m pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]