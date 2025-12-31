from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


loader = PyPDFLoader("05_rag_langchain/paper.pdf")
pages = loader.load()
print(len(pages))
print(pages[0].page_content[:100])
print(pages[0].metadata)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
print()
chunks = text_splitter.split_documents(pages)
print(len(chunks))
print([len(chunk.page_content) for chunk in chunks[:5]])
print(chunks[3])