## Как сделать свой рекоммендер

#### в ноутбуке обучаем модельку

выгружаем нужные данные в `botify/data/recommendations_example.json`
в `botify/config.json` уквзываем путь до этого файла, прописываем хоаста, порт и DBs

```python
"REDIS_RECOMMENDATIONS_<name>_HOST": "redis",
"REDIS_RECOMMENDATIONS_<name>_PORT": 6379,
"REDIS_RECOMMENDATIONS_<name>_DB": <num>,
...
"RECOMMENDATIONS_<name>_FILE_PATH": "./data/recommendations_example.json",
```

подгружаем их в `botify/server.py`

```python
recommendations_example = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_EXAMPLE")
catalog.upload_recommendations(recommendations_example.connection, "RECOMMENDATIONS_EXAMPLE_FILE_PATH")
```

#### пишем код нового рекоммендера

`в botify/recommenders/<rec_name>.py`

#### настраиваем A/B эксперимент

в ` botify/experiment.py`, class Experiment

    создаем новый эксперимент, включаем его в`__init__`

в `botify/server.py`, class NextTrack(Resource)

    `treatment = Experiments.<exp_name>.assign(user)`

    в зависимости от treatment назначаем рекоммендер

#### запускаем рекоммендер

```bash
cd botify
docker-compose stop
docker-compose up -d --build --force-recreate --scale recommender=4
# проверяем, что сервис жив
curl http://localhost:5001/
```

#### запускаем симулятор

```bash
cd ../sim
conda activate recsys-2024
# однопоточный
python -m sim.run --episodes 100 --config config/env.yml single --recommender remote --seed 31337
# или многопоточный
python -m sim.run --episodes 8000 --config config/env.yml multi --processes 4
```

#### скачиваем данные с рекоммендера

```bash
cd ../script
python dataclient.py --recommender 2 log2local /Users/nadys/recsys_data/experiments/<exp_name>
```

#### запускаем ноутбук Week1Seminar (или ab_test.ipynb)

и анализируем результаты A/B эсперимента
