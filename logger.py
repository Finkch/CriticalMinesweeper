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

# Unlogs an experiment or CD Finder
def unlog(path: str):

    results = {}

    # Obtains all results from given run
    for file in os.listdir(path):

        # Creates data appropriately
        match file:

            # Experiment results
            case 'fulle.csv':
                with open(f'{path}/{file}') as f:
                    results['fulle'] = [int(line) for line in f]


            case 'compressede.csv':
                results['compressede'] = {}
                
                with open(f'{path}/{file}') as f:
                    for line in f:
                        kv = line.split(':')
                        results['compressede'][kv[0]] = kv[1].strip()
            


            # CD Finder results
            case 'fullc.csv':
                results['fullc'] = []
                with open(f'{path}/{file}') as f:
                    for line in f:
                        splits = line.split(',')
                        results['fullc'].append([int(split) for split in splits])

            case 'compressedc.csv':
                results['compressedc'] = []
                with open(f'{path}/{file}') as f:
                    for line in f:
                        results['compressedc'].append({})
                        splits = line.split(',')
                        for split in splits:
                            kv = split.split(':')
                            results['compressedc'][-1][kv[0]] = kv[1].strip()
            
            case 'rhos.csv':
                with open(f'{path}/{file}') as f:
                    results['rhosc'] = [float(line) for line in f]

            case 'timesc.csv':
                with open(f'{path}/{file}') as f:
                    results['timesc'] = [float(line) for line in f]

    return results