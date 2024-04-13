# Homework 2

### How to test
1. Launch Botify: ```docker-compose up -d --build --force-recreate --scale recommender=1```
2. Run simulations: ```python -m sim.run --episodes 1000 --config config/env.yml single --recommender remote --seed 31337```
3. Clean ```cache``` folder
4. Save results: ```python ./script/dataclient.py --recommender 1 log2local ./cache/```
5. Stop Botify: ```docker-compose stop```
6. Run the whole [Week 1 Seminar](../../jupyter/Week1Seminar.ipynb). T7 will represent the implemented algorithm. Baseline is T4 (DSSM).
