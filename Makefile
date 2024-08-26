run:
	@command poetry run fastapi run rentavid/main.py --port 8000

build:
	DOCKER_BUILDKIT=1 docker build -t rentavid-api .

docker_run:
	@command docker run --name api -d -p 8000:8000 -e DB_URL="postgresql://postgres:1236456@pagila/postgres" rentavid-api 