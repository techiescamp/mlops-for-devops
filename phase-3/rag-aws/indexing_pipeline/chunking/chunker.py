from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(md_docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=50)
    documents = []

    try:
        for doc in md_docs:
            split_texts = text_splitter.split_text(doc['content'])
            for i, chunk in enumerate(split_texts):
                documents.append(Document(
                    page_content=chunk,
                    metadata={'source': f"{doc['filename']}-{i}"}
                ))
        print(f"Total document chunks created: {len(documents)}")
        if documents:
            print(f"First chunk sample - Content length: {len(documents[0].page_content)}")
            print(f"First chunk sample - Metadata: {documents[0].metadata}")
        return documents
    except Exception as e:
        print(f"Error in text splitting: {e}")
        raise
