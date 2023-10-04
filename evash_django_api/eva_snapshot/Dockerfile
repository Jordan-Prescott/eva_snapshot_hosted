FROM python:3.10

WORKDIR /app

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install graphviz

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]