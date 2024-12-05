# Write results to file.
# Since we have a ton of storage compared to memory (typically), we'll store the full results
# in addition to the compressed data

import os
import csv

# Logs data from an experiment
def log(dir: str, file: str, results: list | dict) -> None:
    
    # Ensures the logdir exists
    if not os.path.exists(f'Results/{dir}'):
        os.makedirs(f'Results/{dir}')

    # Writes uncompressed results
    if isinstance(results, list):
        with open(f'Results/{dir}/{file}.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(([result] for result in results))
    elif isinstance(results, dict):
        with open(f'Results/{dir}/{file}.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(([f'{k}:{v}'] for k, v in results.items()))
    else:
        assert False, f'unknow results type "{type(results)}"'

    def unlog(path):
        pass