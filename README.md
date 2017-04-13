
Ein Open Source Spiel auf Basis von OpenStreetMap.

# Install & Run
```
docker-compose build
docker-compose down
docker-compose up -d
```
copy config.py.example to config.py and wait unitl http://localhost is availible
```
docker-compose exec web python3 manage.py bcryptbenchmark
```
and change BCRYPT_LOG_ROUNDS in the config.py
```
docker-compose exec web python3 manage.py db init
docker-compose exec web python3 manage.py db migrate
docker-compose exec web python3 manage.py db upgrade
```
have a look at manage,py and adjust the importPlaces function to your location
```
docker-compose exec web python3 manage.py imoprtInitData
```
