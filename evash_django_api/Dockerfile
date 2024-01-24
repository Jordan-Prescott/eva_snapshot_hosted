# Pull base image
FROM python:3.10-slim

# Create directories and set work dir
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/static
WORKDIR $APP_HOME

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update the OS and install app-specific software
RUN apt update
RUN apt -y upgrade
RUN apt -y install graphviz

# Install the app dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy the project to the working directory
COPY . .