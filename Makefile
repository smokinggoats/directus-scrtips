build:
	docker build -t directus-scripts .

dev:
	uv run gunicorn --bind 0.0.0.0:5000 'main:app'

run:
	docker run --name directus-scripts -p 5000:5000 --env-file=./.env --rm directus-scripts:latest

prod:
	docker run -d --restart always --name directus-scripts -p 5000:5000 --env-file=./.env directus-scripts:latest