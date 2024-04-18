# Homework 2

## Идея

* Берем любой отсортированный список рекомендаций (в нашем случае DSSM).  
* Если первый трек не присутвует в рекомендациях, то рекомендуем случайный из них.

* Далее, определим два множества треков, первое: треки в окно (на расстояние `window_size`) и второе: вне окна.

* Будем хранить всю историю прослушенных треков - уже прослушенные убираем из множеств.  

* если `track_time` большое, значит 'похожие' треки понравятся - рекомендуем случайный в окне. Иначе похожие уже надоели/не нравятся - то рекомендуем случайные не похожие, вне окна. 

> Лучший результат получается, для `window_size=4`, `track_time > 0.6`

## Код

Добавлен новый эксперимент `DSSM_VS_ALL` и рекомендор `Window` в `window.py`

## Запуск

> Находимся в корни репозитория : `recsys-course-spring-2024/`



Настройка окружения (на mac m1 просто поставить все либы, не вышло)
* Создаем конду `CONDA_SUBDIR=osx-64 conda create -n recsys-2024 python=3.8.18`
* `conda activate recsys-2024`

* Убрать из `requirements` библиотеку `gym`
* `pip install -r ./sim/requirements.txt`
* `pip install pip==21`
* `pip install wheel==0.38.0`
* `pip install setuptools==65.5.0`
* `pip install gym==0.20.0`



Перемещаемся в botify
```bash
cd botify
```

Запускаем рекомендоры: 

```bash
docker-compose up -d --build --force-recreate --scale recommender=1
```

Перемещаемся в sim
```bash
cd ../sim

```

Начинаем симуляцию пользователей

```bash
python -m sim.run --episodes 2000 --config config/env.yml multi --processes 1
```

Возвращаемся в корень проекта 
```bash
cd ..
```
Чистим кеш
```
rm -rf local_data/cache
```

Выгружаем, данные из докер-пространства

```
python script/dataclient.py --recommender 1 log2local ./local_data/cache
```

Далее идем запускаем и смотрим резрультат тетрадки `recsys-course-spring-2024/jupyter/metrics_Week1Seminar.ipynb`

Запуск jupyter

```bash
jupyter notebook
```

# Результат 

Наша эвристика построенная на отсортированных рекомендациях позволяет более точно определять желание пользователя и быть более адаптивной, что показывает стат значимый результат. 

![alt text](image.png)

