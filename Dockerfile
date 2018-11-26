FROM python:3.6-slim
LABEL maintainer="Nick Janetakis <nick.janetakis@gmail.com>"

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

WORKDIR /seneschal

COPY . .
RUN pipenv install

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "seneschal:create_app()"