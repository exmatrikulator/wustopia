
Ein Open Source Spiel auf Basis von OpenStreetMap.

# Install & Run
```
docker-compose build
docker-compose down
docker-compose up -d
docker-compose exec web python3 manage.py db init
docker-compose exec web python3 manage.py db migrate
docker-compose exec web python3 manage.py db upgrade
docker-compose exec web python3 manage.py imoprtInitData
```
