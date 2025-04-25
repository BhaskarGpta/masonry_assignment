# Masonry - Conversational Agent

This is a conversational agent designed to search the web for user queries and engage in meaningful conversations based on the retrieved information. By combining web scraping, natural language processing (NLP), and conversational AI, this agent provides an interactive and informative user experience, making it suitable for various use cases where real-time, accurate information is required.

**Features**
Web Search Integration: Automatically fetches relevant information from the web based on user queries to provide accurate and up-to-date responses.

Conversational AI: Utilizes advanced NLP techniques to engage in dynamic, context-aware conversations. It ensures the conversation is meaningful by processing the retrieved data intelligently.

Efficient Memory Management: Uses a memory system to remember the context of the conversation and deliver personalized responses based on past interactions.

Error Handling: Includes mechanisms to gracefully manage issues like failed searches, unsupported queries, and rate limits.

**Modules**
**1. Query Analyser**
Purpose: The Query Analyser module is responsible for understanding the user’s input and extracting the main intent and keywords.

How it works:

The input is parsed to detect key components such as dates, locations, and other important entities.

The system also handles ambiguous or incomplete queries by employing intelligent prompting methods like Chain of Thought (CoT) and One-Shot Prompting. This helps the system break down complex queries and make them ready for web searches.

Prompts are defined in core/prompt/query_breakdown.txt, where various strategies for query breakdown are outlined, allowing the agent to better understand different types of user queries.

Edge Cases:

Handles cases where the user input is vague or incomplete, such as asking for "news" without specifying a topic, by using the CoT method to guide the conversation.

**2. Link Retriever and Scorer**
Purpose: This module interacts with search APIs (like Google Custom Search) to retrieve relevant links based on the user’s query.

How it works:

Search API Integration: Utilizes the Google Custom Search API to fetch a list of potential links that might contain relevant information for the query.

Scoring Mechanism: Each retrieved link is ranked based on relevance, which is determined using a scoring function defined in core/prompts/scoring.txt. This helps prioritize high-quality and relevant links over less useful ones.

Filters: Filters out links with low relevance scores, ensuring that only the most relevant pages are considered for web scraping.

Pagination: If many links are filtered out, the module can move on to subsequent pages of search results to retrieve additional links (within the limits of 10 links). This ensures that enough relevant data is collected without overwhelming the system.

Limits: The maximum number of links retrieved is set to 10 to balance performance and relevance, with a minimum threshold of 5 links to ensure some useful data is always returned.

**3. Web Scraper**
Purpose: The Web Scraper is tasked with extracting structured information from the retrieved links. It supports dynamic websites using Selenium and handles multiple data types like lists, paragraphs, tables, and headings.

How it works:

Dynamic Web Scraping: Uses Selenium to interact with dynamic websites that require scrolling or waiting for elements to load. The scraper ensures that all content on the page is fully loaded before starting the extraction process.

Data Extraction:

Scrapes headings, paragraphs, lists, and tables separately to ensure clean and structured data extraction.

The scraper handles all types of content (like plain text, lists, or tabular data) and converts them into a format suitable for processing.

Scroll Feature: Implements a scrolling mechanism to ensure the entire page is loaded, including content that only appears when the page is scrolled.

Error Handling: If a webpage causes an error during scraping (e.g., a broken link or page load failure), the scraper skips that link and continues to the next one.

Multithreading: Previously, multithreading was implemented to improve speed, but it was found to cause system crashes due to heavy load. This feature was adjusted for stability.

**4. Conversational Agent**
Purpose: The Conversational Agent combines the web-scraped data into a structured knowledge base (vector database) and uses it to engage in dynamic conversations with users.

How it works:

Vector Database: The scraped data is stored in a vector database, where each document is tagged with metadata (e.g., source and content type). This allows the system to easily retrieve relevant information based on the user’s query.

Memory Implementation:

Uses ConversationBufferMemory to store the context of the conversation, ensuring that the agent can reference previous interactions for a more coherent and context-aware dialogue.

Contradiction Resolution: The prompt and memory setup also help identify contradictions in the retrieved information and resolve them. This is especially useful when different sources provide conflicting details.

Prompt-based Retrieval: Utilizes efficient prompting methods, as defined in core/prompts/query_retrieval.txt, to guide the agent in identifying relevant information from the vector store, ensuring accuracy and relevance in responses.

Memory Strategies for Improvement to limit token size (Not Used):

Summarized Memory: Reduces the token usage by summarizing past conversations.

ConversationBufferWindowMemory: Keeps adding new interactions to the vector database, providing a history-aware context for the agent.

**5. Error Handling**
Purpose: Manages various errors that might occur during the operation of the system, ensuring smooth interaction with the user.

How it works:

Search Failures: If a web search fails (e.g., due to rate limits or network issues), the system automatically retries or provides a fallback response to keep the conversation flowing.

Scraping Errors: In case a page fails to load or the scraper encounters an error, the current link is skipped, and the system continues to the next available link.

Rate Limit Management: Implements rate limit checks when interacting with APIs to avoid hitting usage limits, providing appropriate fallback or retry mechanisms when necessary.

Fallback Responses: If the system cannot retrieve relevant information or encounters errors, it provides a meaningful fallback response (e.g., "Sorry, I couldn't find that information. Can you try asking something else?").
