# Идея

Давайте выдавать рекомендации дссм, не рандомно, а осмысленно. Следующий трек в списке рекомендаций поле предыдущего и первый, если предыдущего трека нет в списке рекомендаций.

Пытался еще обучать LightFm, но не взлетело(4 семинар)

# Инструкция 

cd ./botify
docker-compose up -d --build --force-recreate --scale recommender=1
cd ../sim
python -m sim.run --episodes 2000 --config config/env.yml multi --processes 4
cd ../botify
docker cp botify-recommender-1:/app/log/ /tmp/ 
(В последней у меня почему-то `docker cp botify-recommender-5:/app/log/ /tmp/ `)

И запускаем первый семинар 

# Итог

[alt text](AB.png)

