
An Open Source Game based on OpenStreetMap.

# Install & Run
```
docker-compose up -d --build
```
and visit http://localhost/

## Develop & Run
Comment out the app volume in the docker-compose.yml and run
```
docker-compose up -d --build
```
and visit http://localhost/

### Formula for new resources
```
(<steps> - 1) root of(<end>/<start>)
```

e.g. 20 steps from 20 to 86400 seconds (1 day)
https://www.wolframalpha.com/input/?i=19+root+of+(86400%2F20)

for benefit calculate -2 steps on amount and +2 steps on time.
