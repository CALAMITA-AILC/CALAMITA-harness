import os
import shutil
import pandas as pd
import yaml
import logging
from collections import defaultdict
import glob
from tqdm import tqdm

# Setup logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger()

# Constants for file and folder names
task_config_file = 'task_info.yaml'
model_config_file = 'model_info.yaml'
results_folder = '/leonardo_work/IscrC_CALAMITA/results_calamita_2024'
pull_results_from_years = ["2024", "2025"]
output_folder = "output_folder"

# Create output directory if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

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

logger.info("Model config")
logger.info(f"Number of models: {len(model_config)}")
logger.info(model_config)
    
model_2_task_found = defaultdict(list)
for task, subtask_list in tqdm(task_config.items(), desc="Task"):
    for subtask in tqdm(subtask_list, desc="Subtask"):
        os.makedirs(os.path.join(output_folder, task, subtask), exist_ok=True)
        for model in model_config.keys():
            matching_files = list()
            for y in pull_results_from_years:
                matching_files.extend(glob.glob(os.path.join(results_folder, model, f"samples_*{subtask}_{y}*.jsonl")))
            if len(matching_files) == 0:
                print(f"No files found for model {model} and subtask {subtask}")
            else:
                if len(matching_files) > 1:
                    logger.warning(f"Multiple files found {model}, {subtask}: {matching_files}. Taking the first one")

                model_2_task_found[model].append(subtask)
                abs_path = matching_files[0]
                basename = os.path.basename(abs_path)
                destination_path = os.path.join(output_folder, task, subtask, f"{model}_{basename}")
                shutil.copyfile(abs_path, destination_path)


# Create a boolean DataFrame with models as columns and subtasks as rows
all_subtasks = set([subtask for subtasks in task_config.values() for subtask in subtasks])
all_models = list(model_config.keys())
df = pd.DataFrame(index=list(all_subtasks), columns=all_models)
for model, tasks in model_2_task_found.items():
    for task in tasks:
        df.loc[task, model] = True
df.to_csv('model_2_task_found.csv')