from elasticsearch import Elasticsearch
from .config import settings

es_client = Elasticsearch([
    {'host': settings.ELASTICSEARCH_HOST, 'port': settings.ELASTICSEARCH_PORT}
])

def get_elasticsearch():
    try:
        yield es_client
    finally:
        pass  # Elasticsearch connection is managed by the client

def index_document(index: str, document: dict, doc_id: str = None):
    return es_client.index(index=index, body=document, id=doc_id)

def search_documents(index: str, query: dict):
    return es_client.search(index=index, body=query)

def get_document(index: str, doc_id: str):
    return es_client.get(index=index, id=doc_id)

def delete_document(index: str, doc_id: str):
    return es_client.delete(index=index, id=doc_id)

def update_document(index: str, doc_id: str, document: dict):
    return es_client.update(index=index, id=doc_id, body={"doc": document}) 