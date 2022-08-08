# Questions-service (qserv)

<p align="right">
  <a href="https://docs.python.org/3.9/">
    <img src="https://img.shields.io/badge/Python-3.9-FFE873.svg?labelColor=4B8BBE"
        alt="Python requirement">
  </a>
</p>

## About

A simple web service application:
* takes POST requests in form `{"questions_num": integer}`;
* sends a request to a public [API](https://jservice.io/api/random?count=1) to get specified early
number of questions (`integer`);
* saves part information of received questions to own DB (in case the question is found in the DB,
the application sends new requests to the public API to get unique questions);
* responds to the client request by returning previously saved question or, if there is none, an 
  empty 
  object (in my case empty dictionary`{}`).

Tech stack: \
[Flask](https://flask.palletsprojects.com/en/2.1.x/),
[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/),
[Docker](https://www.docker.com/)

## Docker instructions

Clone this git repository. \
Before starting, [install Docker Compose](https://docs.docker.com/compose/install/) if you do not have 
it. Below it is assumed that
[Docker's repositories](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
are set up. By default, the Docker daemon always runs as the `root` user. If you do not want to 
preface the docker command with `sudo` see
[this](https://docs.docker.com/engine/install/linux-postinstall/). Start Docker daemon with command:

```shell
$ sudo service docker start
```

### Build image

`Dockerfile` describes modifications of [Python 3.9 parent image](https://hub.docker.com/r/library/python/tags/3.9)
needed to build 'qserv-app' image. \
To build Docker's 'qserv-app' image, run the following from the project 
root directory: 

```shell
$ sudo docker build --tag qserv-app .
```

### Run containers


`docker-compose.yml` describes two services: 'db' ans 'web'. 'db' is 
service with PostgreSQL DBMS. 
The 'postgres' image is used to start 'db'. 'db' uses volumes at path `./data/db` for 
containing DB data.  See the 
[reference](https://docs.docker.com/compose/compose-file/) for more 
information about structure `docker-compose.yml`.
'web' is service that runs 'qserv-app' image and also has dependency on 'db'. Make sure you create 
the 'qserv-app' image before starting the services.

To create and run only Docker container with PostgreSQL, run from the project root directory:

```shell
$ sudo docker compose up db
```

or use flag `-d` to start the service in the background

```shell
$ sudo docker compose up db -d
```

To create and run Docker container with 'qserv-app' application, run from the project root directory:

```shell
$ sudo docker compose up
```

To shut down running services and clean up containers, use either of these methods:
* stop the application by typing `Ctrl-C` in the same shell (if the service is running in the 
  foreground) 
  in where you started it, then use `sudo docker rm <CONTAINER ID | NAME>` to remove containers 
  (to see containers list `sudo docker ps -a`)
* or switch to a different shell and run from the project root directory

```shell
$ sudo docker compose down
```

## Application

To connect to running 'db' service with PostgreSQL, run:

```shell
$ psql -U postgres -W -h 127.0.0.1 -p 5432 postgres
```

Input password: 'postgres'. It is assumed you have psql - PostgreSQL interactive terminal.

To send POST request to the running 'qserv-app', use:

```shell
$ curl -X POST http://127.0.0.1:8000/ \
        -H 'Content-Type: application/json' \
        -d '{"questions_num":<your integer number>}'
```

for example:

```
$ curl -X POST http://127.0.0.1:8000/ \
        -H 'Content-Type: application/json' \
        -d '{"questions_num":1}'
```

or run from the project root directory:

```shell
$ ./request.sh <not negative integer number>
```
