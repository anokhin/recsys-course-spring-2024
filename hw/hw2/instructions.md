# Как запускать

Для запуска сервиса или симулятора новых инструкций нет, но лучше запускать в одном контейнере:

`recsys-course-spring-2024\botify>docker-compose up -d --build --force-recreate --scale recommender=1`

`recsys-course-spring-2024\sim>python -m sim.run --episodes 2000 --config config/env.yml single --recommender remote`

`\recsys-course-spring-2024\script>python dataclient.py --recommender 1 log2local ../hw/hw2/logs`

Дальше смотрим на результаты в `AB_test.ipynb`.

Для ноутбуков с обучением модели тоже не требуятся библиотеки кроме тех, что уже использовались по ходу курса.

При загрузке данных используйте те, что есть. По необходимости ставьте `data_prepared = False`

Можно загрузить в `data` `contextual_data.csv` с одного из семинаров.