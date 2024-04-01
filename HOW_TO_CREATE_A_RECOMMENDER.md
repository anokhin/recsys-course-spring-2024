## Что делать

#### в ноутбуке обучаем модельку

выгружаем нужные данные в `botify/data/recommendations_example.json`
в `botify/config.json` уквзываем путь до этого файла

    `"RECOMMENDATIONS_DSSM_FILE_PATH": "./data/recommendations_example.json",`

подгружаем их в `botify/server.py`

```python
recommendations_example = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_EXAMPLE")
catalog.upload_recommendations(recommendations_example.connection, "RECOMMENDATIONS_EXAMPLE_FILE_PATH")
```

#### пишем код нового рекоммендера

`в botify/recommenders/<rec_name>.py`

#### настраиваем A/B эксперимент

в ` botify/experiment.py`, class Experiment

    создаем новый эксперимент, включаем его в init

в `botify/server.py`, class NextTrack(Resource)

    `treatment = Experiments.<exp_name>.assign(user)`

    в зависимости от treatment назначаем рекоммендер

#### запускаем рекоммендер

```bash
cd botify
docker-compose up -d --build --force-recreate --scale recommender=2
```

#### запускаем симулятор

```bash
cd ../sim
conda activate recsys-2024
# однопоточный
python -m sim.run --episodes 2000 --config config/env.yml single --recommender remote --seed 31337 
# или многопоточный
python -m sim.run --episodes 1000 --config config/env.yml multi --processes 4
```

#### скачиваем данные с рекоммендера

```bash
cd ../script
python dataclient.py --recommender 2 log2local /Users/nadys/recsys/experiments/<exp_name>
```

#### запускаем ноутбук Week1Seminar

и анализируем результаты A/B эсперимента
