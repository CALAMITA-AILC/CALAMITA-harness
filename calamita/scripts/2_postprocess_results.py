#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script reads the results from the main directory (files 'results_*') and
for each pair <task, model> based on entries in task_info.yaml and model_info.yaml
it extracts the numerical results and stores them in a dictionary.

TODO: as of now, we don't have a mapping task_name<->main metric,
so we use arbitrarily the second key for each result dict as the numerical result.
"""


import pandas as pd
import yaml
import logging
import glob
import os
import json
from collections import defaultdict
from itertools import product

task_config_file = 'task_info.yaml'
model_config_file = 'model_info.yaml'
results_folder = '/leonardo_work/IscrC_CALAMITA/results_calamita_2024'
pull_results_from_years = ["2024", "2025"]

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger()

results_dir = "/leonardo_work/IscrC_CALAMITA/results_calamita_2024"


# Read task config file yaml
with open(task_config_file, 'r') as stream:
    task_config = yaml.safe_load(stream)

logger.info("Task config")
logger.info(f"Number of tasks: {len(task_config)}")
logger.info(task_config)
# conversion_dict = {v: k for k, v in task_config.items()}

# Read model config file yaml
with open(model_config_file, 'r') as stream:
    model_config = yaml.safe_load(stream)


def process_results_file(f):
    task_stats = dict()
    with open(f) as fp:
        curr_res = json.load(fp)
    for task_name, v in curr_res["results"].items():
        task_results = list(v.keys())
        # each result has at least one key (alias) so, to have a numerical result, we need at least two keys
        if len(task_results) > 1:
            # since we don't have a mapping task_name<->metric, we use arbitrarily the second key for each result dict
            if isinstance(v[task_results[1]], (int, float)):
                task_stats[task_name] = {task_results[1]: v[task_results[1]]}

    return task_stats
    
    

model_results = defaultdict(dict)
for model in model_config.keys():
    for f in glob.glob(os.path.join(results_dir, model, "results*")):
        model_results[model].update(process_results_file(f))
        
# flatten the list of list of task names from values of each entry in task_config
all_task_names = [task for subtask_list in task_config.values() for task in subtask_list]

full_stats = defaultdict(dict)
numerical_matrix = defaultdict(dict)
for task, model in product(all_task_names, model_config.keys()):
    metric_result = model_results[model].get(task, None)
    if metric_result is not None:
        metric_name = list(metric_result.keys())[0]
        numerical_matrix[task][model] = metric_result[metric_name]
    else:
        numerical_matrix[task][model] = None
    
    full_stats[task][model] = metric_result  # save it as a dict of one key: value

with open("task_model_performance.json", "w") as fp:
    json.dump(full_stats, fp, indent=4)

# Create a pandas DataFrame from the boolean matrix
boolean_matrix_df = pd.DataFrame.from_dict(numerical_matrix, orient='index')

# Save the DataFrame to a CSV file
boolean_matrix_df.to_csv("model_2_task_results_found.csv", index_label="Task")

