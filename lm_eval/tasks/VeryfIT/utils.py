def doc_to_text(doc) -> str:
    statement = doc["statement"]
    statement_date = doc["statement_date"]
    return f"Il seguente statement, se non esplicitamente specificato, riguarda il contesto italiano. Nella data indicata era vero o falso? Rispondi solo 'Vero' o 'Falso'.\nStatement: {statement}\nData: {statement_date}"

def doc_to_text_clarified(doc) -> str:
    if doc["annotato"]:
      statement = doc["statement_revised"]
    else:
      statement = doc["statement"]
    statement_date = doc["statement_date"]
    return f"Il seguente statement, se non esplicitamente specificato, riguarda il contesto italiano. Nella data indicata era vero o falso? Rispondi solo 'Vero' o 'Falso'.\nStatement: {statement}\nData: {statement_date}"