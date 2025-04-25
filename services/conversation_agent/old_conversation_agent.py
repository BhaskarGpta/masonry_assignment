#PLEASE IGNORE THIS CODE, USED THIS ONE FOR TESTING PURPOSES ONLY

from utils.file import FileHandler
from utils.output import OutputHadler
from core import Prompts
from core import LLMInitializer
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import StuffDocumentsChain
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain.chains import ConversationChain,  ConversationalRetrievalChain
from langchain.memory.vectorstore import VectorStoreRetriever
import os
from typing import Dict, List, Any

try:
    llm_initializer = LLMInitializer() #instantiate the class
    llm = llm_initializer.set_llm()  # Call the set_llm method
    #print("LLM initialized successfully!")
except Exception as e:
        print(f"Couldn't initialize LLM: {e}")

class Chatbot:
    def __init__(self, query: str):
        self.file_handler = FileHandler()
        self.output_handler = OutputHadler()
        self.model = llm
        self.input_dir = "data/scraped_data"
        self.faiss_dir = "data/vector_database"
        self.query = query
        self.embedder = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)

    def build_database(self) -> VectorStoreRetriever:
        all_documents = []
        for filename in os.listdir(self.input_dir):
            if not filename.endswith(".json"):
                continue
            data = self.file_handler.load_json(os.path.join(self.input_dir, filename))
            for heading in data.get("headings", []):
                all_documents.append(Document(page_content=heading, metadata={"type": "heading", "source": filename}))

        # Paragraphs
            for para in data.get("paragraphs", []):
                chunks = self.splitter.split_text(para)
                for chunk in chunks:
                    all_documents.append(Document(page_content=chunk, metadata={"type": "paragraph", "source": filename}))

            # Lists
            for lst in data.get("lists", []):
                for item in lst:
                    if item.strip():
                        chunks = self.splitter.split_text(item)
                        for chunk in chunks:
                            all_documents.append(Document(page_content=chunk, metadata={"type": "list", "source": filename}))

            # Tables
            for table in data.get("tables", []):
                if not isinstance(table, dict):
                    continue
                title = table.get("heading", [])
                headers = table.get("headers", [])
                for row in table.get("rows", []):
                    if isinstance(row, dict):
                        row["heading"] = title
                        row_text = " | ".join(f"{k}: {v}" for k, v in row.items())
                    elif isinstance(row, list):
                        row_text = f"heading: {title} | " + " | ".join(
                            f"{headers[i]}: {v}" for i, v in enumerate(row) if i < len(headers)
                        )
                    else:
                        continue
                    chunks = self.splitter.split_text(row_text)
                    for chunk in chunks:
                        all_documents.append(Document(page_content=chunk, metadata={"type": "table_row", "source": filename}))

        self.vectorstore = FAISS.from_documents(all_documents, self.embedder)
        self.vectorstore.save_local(self.faiss_dir)
        return self.vectorstore


    def initiate_convo(self):
        vectorstore = self.build_database()
        system_prompt = Prompts.query_retrieval
        human_prompt = "{input}"

        prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
        document_chain = create_stuff_documents_chain(self.model, prompt)

        retriever = vectorstore.as_retriever(search_kwargs={"k": 50})  
        retrieval_chain = create_retrieval_chain(
            retriever = retriever,
            combine_docs_chain = document_chain
        )

        response = retrieval_chain.invoke({"input": self.query})
        print(response["answer"])

    