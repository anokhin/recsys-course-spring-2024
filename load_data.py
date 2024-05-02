import os
import subprocess


if __name__ == '__main__':
    folder = 'results'
    s = 1
    n = 4
    for i in range(s, s + n):
        os.makedirs(f'./{folder}/log-{i}', exist_ok=False)
        subprocess.run([
            'docker', 'cp', f'botify-recommender-{i-s+1}:/app/log/data.json', f'./{folder}/log-{i}/data.json',
        ])
