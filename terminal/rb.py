#!/usr/bin/env python3

import argparse
import os
import subprocess

DOCKER_COMPOSE_FILE_CONTENT = """
version: '3'

services:
  db:
    image: postgres:latest
    environment:
      - POSTGRES_DB=reviewboard
      - POSTGRES_USER=reviewboard
      - POSTGRES_PASSWORD=reviewboard
    volumes:
      - dbdata:/var/lib/postgresql/data

  cache:
    image: redis:latest

  web:
    image: reviewboard/reviewboard:latest
    ports:
      - "8080:80"
    environment:
      - DATABASE_TYPE=postgresql
      - DATABASE_NAME=reviewboard
      - DATABASE_USER=reviewboard
      - DATABASE_PASSWORD=reviewboard
      - DATABASE_HOST=db
      - REDIS_HOST=cache
      - ENABLE_SEARCH=1
      - LOAD_DEFAULT_DATA=1
    depends_on:
      - db
      - cache

volumes:
  dbdata:
"""

def write_docker_compose(file_location):
    with open(file_location, 'w') as f:
        f.write(DOCKER_COMPOSE_FILE_CONTENT)
    print(f"Docker Compose file written to {file_location}")

def start_reviewboard(file_location):
    subprocess.run(["docker-compose", "-f", file_location, "up", "-d"], check=True)
    print("Review Board started.")

def stop_reviewboard(file_location):
    subprocess.run(["docker-compose", "-f", file_location, "down"], check=True)
    print("Review Board stopped.")

def main():
    parser = argparse.ArgumentParser(description="Review Board Docker Compose Utility")
    parser.add_argument("command", choices=["install", "start", "stop"], help="Command to execute")
    parser.add_argument("file_location", nargs='?', default=os.getcwd(), help="Location of the Docker Compose file (default: current directory)")

    args = parser.parse_args()

    file_location = os.path.join(args.file_location, "docker-compose.yml")

    if args.command == "install":
        write_docker_compose(file_location)
    elif args.command == "start":
        start_reviewboard(file_location)
    elif args.command == "stop":
        stop_reviewboard(file_location)

if __name__ == "__main__":
    main()

