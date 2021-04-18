FROM python:3.8
# use just for local development
WORKDIR /project
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./ .