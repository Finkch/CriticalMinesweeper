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
            case 'expReveals.csv':
                with open(f'{path}/{file}') as f:
                    reader = csv.reader(f)
                    results['expReveals'] = [int(line[0]) for line in reader]

            case 'expAlphas.csv':
                with open(f'{path}/{file}') as f:
                    reader = csv.reader(f)

                    # Regular alpha value
                    try:
                        results['expAlphas'] = [float(line[0]) for line in reader]

                    # Lists of successive frontier sizes
                    except:
                        results['expAlphas'] = []
                        for line in reader:
                            splits = line[0].replace('[', '').replace(']', '').split(', ')
                            results['expAlphas'].append([int(frontier) for frontier in splits])

            case 'expDists.csv':
                pass    # For now, ignore this one

            case 'expMeta.csv':
                results['expMeta'] = {}
                with open(f'{path}/{file}') as f:
                    for line in f:
                        kv = line.split(':')
                        results['expMeta'][kv[0]] = kv[1].strip()
            


            # CD Finder results
            case 'cdReveals.csv':
                results['cdReveals'] = []
                with open(f'{path}/{file}') as f:
                    for line in f:
                        splits = line.split(',')
                        results['cdReveals'].append([int(split.strip()) for split in splits])
            
            case 'cdAlphas.csv':
                results['cdAlphas'] = []
                with open(f'{path}/{file}') as f:
                    for line in f:
                        splits = line.split(',')
                        results['cdAlphas'].append([float(split.strip()) for split in splits])


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