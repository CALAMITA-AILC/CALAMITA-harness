import json
import pandas as pd
import requests
import os
import argparse
import subprocess

DICT_RENAMED = {'conflict_detect': 'gita_conflict_detect', 'physical_state':'gita_physical_state', 'story_class':'gita_story_class'}
LISTA_IGNORE = ['agr_tasks', 'od_tasks', 'caus_tasks'] #per la sottotask a due livelli di blm
REPO_URL = "https://huggingface.co/datasets/CALAMITA-AILC/results_calamita_2024"
SUBTASKS_LIST_URL = 'https://raw.githubusercontent.com/CALAMITA-AILC/CALAMITA-harness/refs/heads/main/calamita/calamita_tasks_v1.txt'

def clone_repository(repo_url, destination_folder):
  try:
    subprocess.run(["git", "clone", repo_url, destination_folder], check=True)
    print(f"\nRepository clonato con successo in {destination_folder}")
  except subprocess.CalledProcessError as e:
    print(f"Errore durante il cloning del repository: {e}")
    raise(e)

def git_fetch_and_pull(repo_path):
  try:
    # Esegue git fetch
    subprocess.run(["git", "fetch"], cwd=repo_path, check=True)
    print("Fetch completato con successo.")
    # Esegue git pull
    subprocess.run(["git", "pull"], cwd=repo_path, check=True)
    print("Pull completato con successo.")
  except subprocess.CalledProcessError as e:
    print(f"Errore durante l'esecuzione di git fetch o git pull: {e}\n -> Procedo con i dati locali\n")
  except FileNotFoundError:
    print("Git non è installato o il percorso del repository non è valido.")

def dict_renamed_check(lista_subtasks):
  print(DICT_RENAMED.values())
  for t in DICT_RENAMED.values():
    if t not in lista_subtasks:
      raise Exception(f"\nrenamed subtask {t} not in the current subtasks list\nCheck the rename or update the list")

def main(path_cartella_results):
  # check path della cartella con i risultati
  try:
    if 'results_calamita_2024' not in os.listdir(path_cartella_results):
      raise FileNotFoundError("cartella 'results_calamita_2024' non presente nel path")
  except FileNotFoundError:
    print("cartella/file non presenti, procede a fare il git clone\n")
    clone_repository(REPO_URL, path_cartella_results+'/results_calamita_2024')
  except Exception as e:
    raise(e)
  
  # git fetch e pull della repo per assicurarsi dati aggiornati:
  print("\nfetch e pull della repo con i risultati, per avere i dati aggiornati.")
  git_fetch_and_pull(path_cartella_results+'/results_calamita_2024')

  # retrieve della subtasks list dal github
  response = requests.get(SUBTASKS_LIST_URL)
  if response.status_code == 200:
    file_content = response.text
    lista_elementi = file_content.split('\n')
    lista_subtasks = [elemento.strip() for elemento in lista_elementi if elemento.strip()]
  else:
    raise Exception(f"Failed to retrieve the calamita_tasks_v1.txt file. Status code: {response.status_code}\n")

  # controllo che il DICT_RENAMED contenga valori di subtask esistenti
  dict_renamed_check(lista_subtasks)
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
            raise Exception(f"\nsubtask '{subt}' non presente nell'elenco delle task, trovata nel file: {resultsFilePath}",subt,resultsFilePath)
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
            print(f"\nRENAMED: subtask '{subt}' rinominata in {subtask_newname} trovata con il nome originale nel file: {resultsFilePath}")
          else:
            raise Exception(e.args)

  # Convertire in DataFrame
  df = pd.DataFrame.from_dict(tabellaFinale, orient="index")
  df.index.name = "Subtask"

  # Salvare in CSV
  csv_filename = "tasks_done.csv"
  df.to_csv(csv_filename)
  print(f"\ntabella creata in {csv_filename}\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="""Script per generazione tabella tasks x modelli
                                   
                | modello1 | modello2 | ..
    |  subtask1 |   yes    |   yes    | ..
    |  subtask2 |    no    |    no    | ..
                    ...
    
    MACROS:
      - DICT_RENAMED : lista di subtask di cui si hanno valutazioni con un nome passato ed uno presente
      - REPO_URL : url della repo HF su cui sono salvati i risultati
      - SUBTASKS_LIST_URL : url del file raw su github contenente la lista dei subtask 
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
  parser.add_argument("--resultspath", type=str, help="Path relativo alla cartella results da cui vengono estratti i dati per la creazione della tabella\nSe nel path non è già presente una cartella results, lo script provvederà a fare il git clone.\n")
  args = parser.parse_args()
  if args.resultspath:
    main(args.resultspath)
  else:
    resultspath = input("\nInserisci il path relativo alla cartella results.\nPremi invio se è './'")
    if resultspath == "":
      resultspath = "."
    main(resultspath)