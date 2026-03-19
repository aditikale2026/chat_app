global active_doc_ids 
active_doc_ids=[]

def store_doc_id(doc_id):
    active_doc_ids.append(doc_id)
    print("Current doc_ids:", active_doc_ids)


def get_doc_id():
    return active_doc_ids    

result = get_doc_id()
print(result)