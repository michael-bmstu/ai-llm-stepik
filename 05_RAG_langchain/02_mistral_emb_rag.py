import time
import numpy as np
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_mistralai import MistralAIEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

def sim(v1: np.array, v2: np.array) -> float:
    return (v1 * v2).sum() / np.linalg.norm(v1) / np.linalg.norm(v2)

relevant_doc = Document(page_content="Большая языковая модель это языковая модель, состоящая из нейронной сети со множеством параметров (обычно миллиарды весовых коэффициентов и более), обученной на большом количестве неразмеченного текста с использованием обучения без учителя.")
irrelevant_doc = Document(page_content="Задачи сокращения размерности. Исходная информация представляется в виде признаковых описаний, причём число признаков может быть достаточно большим. Задача состоит в том, чтобы представить эти данные в пространстве меньшей размерности, по возможности, минимизировав потери информации..")

embeddings = MistralAIEmbeddings(model="mistral-embed", api_key=os.getenv("MISTRAL_KEY"))

query_vector = embeddings.embed_query("Что такое LLM?")
time.sleep(2) # avoid bloking free model
doc_vectors = embeddings.embed_documents([relevant_doc.page_content, irrelevant_doc.page_content])
print(len(query_vector))
print("Relevant document score:", sim(np.array(query_vector), np.array(doc_vectors[0])))
print("Irrelevant document score:", sim(np.array(query_vector), np.array(doc_vectors[1])))

vectorstore = InMemoryVectorStore.from_documents(
    [relevant_doc, irrelevant_doc],
    embedding=embeddings,
)
retriever = vectorstore.as_retriever(search_kwargs={'k': 1})
time.sleep(2)

result = retriever.invoke("Что такое большая языковая модель?")
print(result[0].page_content)