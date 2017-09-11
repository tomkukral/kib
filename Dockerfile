FROM python:3.6

# prepare directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


# copy app
COPY . .
