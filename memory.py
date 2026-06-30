import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect(database = 'chatbot.db', check_same_thread=False)
checkpointer=SqliteSaver(conn)

def all_thread_id():
    ids=set()
    for cp in checkpointer.list(None):
        ids.add(cp.config["configurable"]["thread_id"])
    return list(ids)
