FROM python:3.8
# use just for local development
RUN apt-get update && apt-get install -y libgl1-mesa-dev
WORKDIR /project
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./ .