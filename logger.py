# Write results to file.
# Since we have a ton of storage compared to memory (typically), we'll store the full results
# in addition to the compressed data

import os
import csv

# Logs data from an experiment
def log(dir: str, file: str, results: list) -> None:
    
    # Ensures the logdir exists
    if not os.path.exists(dir):
        os.makedirs(dir)

    
    # Writes uncompressed results
    with open(f'Results/{dir}/{file}.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(([result] for result in results))