# Botify

A toy music recommender

```
$ docker-compose up -d --build 
```

```
curl -H "Content-Type: application/json" -X POST -d '{"track":10,"time":0.3}'  http://localhost:5000/next/1
```