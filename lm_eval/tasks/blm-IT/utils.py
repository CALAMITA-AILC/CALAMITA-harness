from sklearn.metrics import f1_score
import datasets
import re
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer

def doc_to_text(doc) -> str:
  Context_concatenated= doc['Context_concatenated']
  Answer_concatenated = doc['Answer_concatenated']
  doc_to_text = f"Ti chiedo di risolvere un quesito. La lingua di questo quesito e' l'italiano."
  doc_to_text += f"\nTi daro' una lista di frasi (numerate da 1 a 7) che chiameremo **Contesto**, e un insieme di frasi (identificate da una lettera) che chiameremo **Risposte**.."
  doc_to_text += f"\nIl tuo compito e' di scegliere fra le **Risposte** la frase che potrebbe essere la frase seguente del **Contesto**."
  doc_to_text += f"\n# FORMATO: Devi mettere **SOLO** la lettera che corrisponde alla risposta migliore. Non inserire altro testo, ne' prima ne' dopo."
  doc_to_text += f"\n# DOMANDA"
  doc_to_text += f"\n**Contesto**"
  doc_to_text += f"\n{Context_concatenated}"
  doc_to_text += f"\n**Risposte**"
  doc_to_text += f"\n{Answer_concatenated}"
  doc_to_text += f"\n**La tua scelta**\n"
  return doc_to_text

def preprocess_dataset(dataset):
    dataset = dataset.select([i for i in range(1)])      # selecting 4 rows for DEBUG
    return dataset


# Funzioni passthrough per le metriche f1 da fare con aggregazione
def f1_score(input):
  f1_score_func()
##

def process_results(doc, results):
  # doc: original doc
  # results[0]: string output of the model
  print(doc)
  print(results[0])
   

def f1_score_func(y_true, y_pred):
    return f1_score(y_true, y_pred, labels=["A", "B", "C", "D", "E", "F", "G", "H"] ,average='macro')

# Funzioni di aggregazione che vengono richiamate direttamente dallo YAML [PER IL PROBLEMA BINARIO]
def f1_score_agg2(dati):
    correct_answers = np.array(["".join(sublist[0]) for sublist in dati])
    generations = np.array(["".join(sublist[1][0]) for sublist in dati])
    print("!!!!")
    print("!!!")
    print(dati)
    print("!!!")
    print("!!!")
    return f1_score_func(correct_answers,generations)

def f1_score_agg(items):
  unzipped_list = list(zip(*items))
  golds = unzipped_list[0]
  preds = unzipped_list[1]
  fscore = f1_score(golds, preds, average="macro")
  return fscore