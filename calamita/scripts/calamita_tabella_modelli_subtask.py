import json
import pandas as pd
import requests
import os
import argparse

DICT_RENAMED = {'conflict_detect': 'gita_conflict_detect', 'physical_state':'gita_physical_state', 'story_class':'gita_story_class'}
LISTA_IGNORE = ['agr_tasks', 'od_tasks', 'caus_tasks'] #per la sottotask a due livelli di blm

def main(path_cartella_results):
  # Raw URL of the file on GitHub
  # Premere il tasto 'raw' durante visualizzazione del file su github
  raw_url = 'https://raw.githubusercontent.com/CALAMITA-AILC/CALAMITA-harness/refs/heads/main/calamita/calamita_tasks_v1.txt'

  response = requests.get(raw_url)
  if response.status_code == 200:
    file_content = response.text
    lista_elementi = file_content.split('\n')
    lista_subtasks = [elemento.strip() for elemento in lista_elementi if elemento.strip()]
  else:
    raise Exception(f"Failed to retrieve the calamita_tasks_v1.txt file. Status code: {response.status_code}\nCopia il file con l'elenco delle subtask in altro modo")

  # check path della cartella con i risultati
  try:
    if 'results_calamita_2024' not in os.listdir(path_cartella_results):
      raise Exception("cartella 'results_calamita_2024' non presente nel path")
  except Exception as e:
    raise Exception(e)

  # le directory contengono il nome del modello
  modelli = [dir.split('__')[1] for dir in os.listdir('./results_calamita_2024') if dir not in ['README.md','.git','.gitattributes']]

  # creazione del dictionary da cui verrà creata la tabella finale
  # istanziamo tutti no e poi passiamo a yes man mano
  tabellaFinale = {el:{model:"no" for model in modelli} for el in lista_subtasks}

  # per ogni directory di modello
  modelsDirectories = [dir for dir in os.listdir('./results_calamita_2024') if dir not in ['README.md','.git','.gitattributes']]
  for modelIndex in range(len(modelli)):
    modelDirectory = modelsDirectories[modelIndex]
    modelDirectoryPath = path_cartella_results+'/results_calamita_2024/'+modelDirectory
    # selezionare le sotto directory contenenti results e non samples
    results = [dir for dir in os.listdir(modelDirectoryPath) if dir[0:7] == 'results']
    # iterare tutti i file results
    for resultFile in results:
      resultsFilePath = modelDirectoryPath+'/'+resultFile
      with open(resultsFilePath, 'r', encoding='utf-8') as file:
        data = json.load(file)
      # estrarre elenco subtasks testate tramite il campo 'group_subtasks'
      # se il value corrispondente è lista vuota: è subtask
      # else, è task. in quel caso va estratta la lista value contenente le subtasks
      group_subtasks = data['group_subtasks'].keys()
      subtasksResult = []
      for subt in group_subtasks:
        if len(data['group_subtasks'][subt]) == 0:
          subtasksResult.append(subt)
        else:
          subtasksResult.extend(data['group_subtasks'][subt])
      # estratte le sottotask, si aggiorna la tabella
      for subt in subtasksResult:
        try:
          # possibile errore, sotto task non nella lista originale
          if subt not in lista_subtasks:
            raise Exception(f"subtask '{subt}' non presente nell'elenco delle task, trovata nel file: {resultsFilePath}",subt,resultsFilePath)
          else:
            modello = modelli[modelIndex]
            tabellaFinale[subt][modello] = "yes"
        except Exception as e:
          error_message, subtaskError, fileError = e.args
          if subtaskError in LISTA_IGNORE:
            pass
          elif subtaskError in DICT_RENAMED.keys():
            subtask_newname = DICT_RENAMED[subtaskError]
            modello = modelli[modelIndex]
            tabellaFinale[subtask_newname][modello] = "yes"
          else:
            raise Exception(e.args)

  # Convertire in DataFrame
  df = pd.DataFrame.from_dict(tabellaFinale, orient="index")
  df.index.name = "Subtask"

  # Salvare in CSV
  csv_filename = "tasks_done.csv"
  df.to_csv(csv_filename)
  print(f"tabella creata in {csv_filename}\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="""Script per generazione tabella tasks x modelli
                                   
                | modello1 | modello2 | ..
    |  subtask1 |   yes    |   yes    | ..
    |  subtask2 |    no    |    no    | ..
                    ...
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
  parser.add_argument("--resultspath", type=str, help="Path relativo alla cartella results da cui vengono estratti i dati per la creazione della tabella")
  args = parser.parse_args()
  if args.resultspath:
    main(args.resultspath)
  else:
    resultspath = input("Inserisci il path relativo alla cartella results.\nPremi invio se è './'\n")
    if resultspath == "":
      resultspath = "."
    main(resultspath)