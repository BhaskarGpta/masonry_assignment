from core import LLMInitializer
from services.query_breakdown import QueryProcessor
from services.link_retrieval import LinkRetriever 
from services.scraping import WebScraper 
from services.conversation_agent import Chatbot

def main():
    """
    Main function to run the application.
    """
    query = "How did Inida respond to the recent Kashmir, Pahalgam incident?"

    QueryAnalyzer = QueryProcessor(query) #Initialize our Query Analyzer Agent
    QueryAnalyzer.break_query()

    QueryQill = LinkRetriever() #Initialize our smart Link Retriever and Ranking Agent
    QueryQill.rank()

    Scraper = WebScraper("data/links/scored_links.json")
    Scraper.start_scraping()

    BT_7274 = Chatbot(query)
    BT_7274.start_chat()
    
    print("Chatbot conversation ended. Exiting...")
    print("Hope you enjoyed the conversation! Have a great day ahead! 😊") #make user experience more personalised
    print("Just remember you always have a buddy to help you out! 🤖") #make user experience even more personalised

if __name__ == "__main__":
    main()