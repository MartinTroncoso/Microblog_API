# Makefile para GitBash
up:
	docker-compose build
	docker-compose up

makemigrations:
	docker-compose exec web python manage.py makemigrations

migrate:
	docker-compose exec web python manage.py migrate

startapp:
	@read -p "Nombre de la nueva app: " app_name; \
	docker-compose exec web python manage.py startapp $$app_name

superuser:
	winpty docker-compose exec -it web python manage.py createsuperuser

shell:
	winpty docker-compose exec web python manage.py Shell

show_urls:
	docker-compose exec web python manage.py show_urls

inspect_db:
	winpty docker exec -it web-market-tracer-db-1 psql -U postgres -d postgres
