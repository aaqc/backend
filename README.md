# AAQC Backend

Server backend for the drones.

## Building & Running

Build the container with: `$ docker-compose build`<br>
Start the container with: `$ docker-compose up`<br>

## Forward the database from remote host using SSH:

`ssh -NL 0.0.0.0:3306:0.0.0.0:3306 $SERVER_HOST`

## How to install and use with VSCode

<a href="how-to-use.gif" target="_blank"><img src="how-to-use.gif" alt="GIF Tutorial on how to do it" width="400px"></a>

## Start devserver in container in debug mode:

`/start-reload.sh`
