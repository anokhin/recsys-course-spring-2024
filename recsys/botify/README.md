# Botify

Сервис рекомендаций реализован как приложение на [Flask](https://flask-restful.readthedocs.io/en/latest/).
Это приложение умеет обрабатывать запросы по REST API.
В качестве in-memory кэша используется [Redis](https://redis.io/).
Приложение пишет лог событий в json в папку `/app/log/`

## Инструкция

1. [Устанавливаем docker](https://www.docker.com/products/docker-desktop)
2. Собираем образы и запускаем контейнеры
   ```
   docker-compose up -d --build 
   ```   
3. Останавливаем контейнеры
   ```
   docker-compose stop
   ```
4. Модифицируем код в этом модуле
5. Повторяем шаги 2-4, пока не достигнем поставленной цели 

## Полезные команды
Проверяем, что сервис жив
```
curl http://localhost:5000/
```
Запрашиваем информацию по треку
```
curl http://localhost:5000/track/42
```
Запрашиваем следующий трек
```
curl -H "Content-Type: application/json" -X POST -d '{"track":10,"time":0.3}'  http://localhost:5000/next/1
```
Завершаем пользовательскую сессию
```
curl -H "Content-Type: application/json" -X POST -d '{"track":10,"time":0.3}'  http://localhost:5000/last/1
```
Закидываем логи контейнера в hdfs (папка scripts должна быть в $PYTHONPATH)
```
python dataclient.py --user anokhin log2hdfs --cleanup tmp
```