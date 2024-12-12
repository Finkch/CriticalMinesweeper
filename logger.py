# Write results to file.
# Since we have a ton of storage compared to memory (typically), we'll store the full results
# in addition to the compressed data

import os
import csv
import json

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
            case 'expMesa.csv':
                with open(f'{path}/{file}') as f:
                    reader = csv.reader(f)
                    results['expMesa'] = [json.loads(line[0]) for line in reader]

            case 'expMeta.csv':
                results['expMeta'] = {}
                with open(f'{path}/{file}') as f:
                    for line in f:
                        kv = line.split(':')
                        results['expMeta'][kv[0]] = kv[1].strip()
            


            # CD Finder results
            case 'cdMesas.csv':
                results['cdMesas'] = []
                with open(f'{path}/{file}') as f:
                    for line in f:
                        results['cdMesas'].append([])
                        line = line.strip().replace('[', '').replace('"', '').replace(']]', '').replace(' ', '')
                        splits = line.split('],')

                        for split in splits:
                            subsplits = split.split(',')
                            results['cdMesas'][-1].append([int(subsplits[0]), float(subsplits[1])])


            case 'cdMetas.csv':
                results['cdMetas'] = []
                with open(f'{path}/{file}') as f:
                    for line in f:
                        results['cdMetas'].append({})
                        splits = line.split(',')
                        for split in splits:
                            kv = split.split(':')
                            results['cdMetas'][-1][kv[0]] = kv[1].strip()
            
            case 'cdRhos.csv':
                with open(f'{path}/{file}') as f:
                    results['cdRhos'] = [float(line.strip()) for line in f]

            case 'cdTimes.csv':
                with open(f'{path}/{file}') as f:
                    results['cdTimes'] = [float(line.strip()) for line in f]

            case '.DS_Store':
                pass # Stupid, smelly .DS_Store!
            
            case _:
                assert False, f'Unrecognised file "{file}"'

    return results