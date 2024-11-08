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
    return input
##

def f1_score_func(y_true, y_pred):
    return f1_score(y_true, y_pred, average='macro')

# Funzioni di aggregazione che vengono richiamate direttamente dallo YAML [PER IL PROBLEMA BINARIO]
def f1_score_agg(dati):
    correct_answers = np.array(["".join(sublist[0]) for sublist in dati])
    generations = np.array(["".join(sublist[1][0]) for sublist in dati])
    print()
    print()
    print (correct_answers)
    print (generations)
    print()
    print()
    return f1_score_func(correct_answers,generations)