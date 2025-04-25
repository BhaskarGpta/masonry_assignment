from datetime import datetime
from utils.file import FileHandler
from utils.output import OutputHadler
from core import Prompts
from core import LLMInitializer
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

try:
    llm_initializer = LLMInitializer() #instantiate the class
    llm = llm_initializer.set_llm()  # Call the set_llm method
    #print("LLM initialized successfully!")
except Exception as e:
        print(f"Couldn't initialize LLM: {e}")

class QueryProcessor:
    def __init__(self, query: str):
        self.file_handler = FileHandler()
        self.output_handler = OutputHadler()
        self.model = llm
        self.output_dir = "data/query/query.json"
        self.query = query

    def get_time(self):
        today = datetime.today()
        formatted_date = today.strftime("%B %d, %Y.")
        self.date = today.strftime("%d")
        self.month = today.strftime("%B")
        self.year = today.strftime("%Y")
    
    def break_query(self):
        print("🧠 Understanding your Query")
        system_prompt = Prompts.query_breakdown
        human_prompt = "{query}, {date}, {month}, {year}"

        prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

        chain = prompt | self.model

        self.get_time()

        response = chain.invoke({
            "query": self.query,
            "date": self.date,
            "month": self.month,
            "year": self.year
        })

        breakdown = self.output_handler.clean_llm_output(response.content)
        print("📖 Deeply Analysing your query")
        self.file_handler.save_json(breakdown, self.output_dir)