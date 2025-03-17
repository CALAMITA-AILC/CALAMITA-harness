# Python Scripts for Processing lm_eval_harness Results
This folder contains useful Python scripts designed to manage the raw results coming from lm_eval_harness framework for Calamita's purposes.
- - -

## parse_for_website.py
### Functionality
This script by default looks for each file having "result*" in the name starting from the current folder and walking in every subdirectory.
This is useful because results coming from lm_eval_harness are usually organized in several different subfolders.
### Output Structure
The script generates an output file, "parsed.json" consisting as a json file organized in this way:

```json
{
  "tasks": [
    {
      "task_name": "",
      "task_pretty_name": "",
      "task_localURL": "",
      "hasPublicData": 0,
      "isTranslated": 0
    }
  ],
  "subtasks": [
    {
      "subtask_name": "",
      "belongTo": "",  // Empty if the subtask is independent
      "evaluations": [
        {
          "model_name": "",
          "metrics": {
            "name1": 0,
            "name2": 0
          }
        },
        {
          "model_name": "",
          "metrics": {
            "name1": 0,
            "name2": 0
          }
        }
      ]
    }
  ],
  "models": [
    {
      "model_name": "",
      "model_pretty_name": "",
      "model_URL": ""
    }
  ]
}
```

### Integration with Calamita's website
Calamita's website is coded for automatically load a json file into this format to generate the total results table as well as adding the results for each task in the website. Be aware that not always this JSON is immediately usable into the website: some tasks until now have some naming problems, so additional post-processing using different simple scripts could be necessary to align every subtask with its parent task.
In this repo a sample "parsed.json" file is included. 

## Download datasets

Some datasets are gated. Be sure to login on Hugging Face or specify the HF_TOKEN environment variable before.

```bash
HF_HOME=/leonardo_work/IscrC_CALAMITA/calamita/huggingface python calamita/scripts/download_datasets.py
```

## List of tasks

```bash
MAGNET_IT_en_it_private
MAGNET_IT_it_en_private
MAGNET_UK_en_it_private
MAGNET_UK_it_en_private
MAGNET_US_en_it_private
MAGNET_US_it_en_private
MAGNET_en_it_public
MAGNET_it_en_public
ami_2020_aggressiveness
ami_2020_misogyny
arc_challenge_ita
arc_easy_ita
beep
belebele_ita
blm_agr1_0shots
blm_agr1_1shots
blm_agr2_0shots
blm_agr2_1shots
blm_caus1_0shots
blm_caus1_1shots
blm_caus2_0shots
blm_caus2_1shots
blm_od1_0shots
blm_od1_1shots
blm_od2_0shots
blm_od2_1shots
conflict_detect
eureka_hints
eureka_original
geese_dummy
geese_human
geese_llama3
geese_noexp
gente_rephrasing
gfg_task_1_1
gfg_task_1_2
gfg_task_2_1
gfg_task_2_2
gfg_task_2_3
gfg_task_3_1
gfg_task_3_2
haspeede2_hs
haspeede2_stereo
hatecheck_ita
hellaswag_ita
honest_ita
ironita_irony
ironita_sarcasm
itacola
multi-it-a
multi-it-c
news_sum_fanpage
news_sum_ilpost
perse_task_0
perse_task_1
perse_task_2
perse_task_3
physical_state
sentipolc
squad_it
story_class
traceIT
truthfulqa_gen_ita
truthfulqa_mc1_ita
truthfulqa_mc2_ita
veryfIT_enriched
veryfIT_full
veryfIT_small
```
