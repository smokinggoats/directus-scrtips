build:
	docker build -t directus-scripts .

run:
	docker run --name directus-scripts -p 5000:5000 --env-file=./.env --rm directus-scripts:latest