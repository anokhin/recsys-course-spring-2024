###  Отчет

Эксперимент по улучшению DSSM-рекоммендора.
В данный момент использую каскад рекомендаций и также выдаю рекомендации в порядке появления в списке.
Пока что эффект не significant.

### Повторение эксперимента

1. В папке `botify`
    ```shell
   docker compose up -d --build --force-recreate --scale recommender=1
   ```
2. В папке `sim`
    ```shell
   python3 -m sim.run --episodes 3000 --config config/env.yml single --recommender remote --seed 533
   ```
3. В корневой папке
    ```shell
    python ./script/dataclient.py --recommender 1 log2local ./cache/
    ```
