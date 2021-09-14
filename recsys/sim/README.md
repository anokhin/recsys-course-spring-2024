# Sim

Simulate music recommender users

```
export PYTHONPATH=${PYTHONPATH}:.
```

```
python sim/run.py --episodes 1 --recommender console --config config/env.yml --seed 31337
```

```
python sim/run.py --episodes 1000 --recommender remote --config config/env.yml --seed 31337
```