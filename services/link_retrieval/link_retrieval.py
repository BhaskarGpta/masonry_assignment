from utils.file import FileHandler
from utils.output import OutputHadler
from core import Prompts
from core import LLMInitializer
from langchain.prompts import ChatPromptTemplate
import requests
from dotenv import load_dotenv
import os
import math
from typing import List, Dict, Any
import time

try:
    llm_initializer = LLMInitializer()
    llm = llm_initializer.set_llm()
except Exception as e:
    print(f"Couldn't initialize LLM: {e}")

class LinkRetriever:
    def __init__(self):
        load_dotenv()
        self.links_output_dir: str = "data/links/links.json"
        self.score_output_dir = "data/links/scored_links.json"
        self.file_handler = FileHandler()
        self.output_handler = OutputHadler()
        self.query_file = self.file_handler.load_json("data/query/query.json")
        self.search_terms = self.query_file["search_terms"]
        self.API_KEY = os.getenv("API_KEY")
        self.SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
        self.query = self.query_file["query"]
        self.intent = self.query_file["intent"]
        self.topics = self.query_file["topics"]
        self.location = self.query_file["location"]
        self.time = self.query_file["time"]
        self.num_results_per_page = 10
        self.max_search_pages = 5
        self.max_total_filtered_links = 10

    def get_results_from_search(self, term: str, api_key: str, search_engine_id: str, start_index: int = 1, num_results: int = 10) -> List[Dict[str, Any]]:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": term,
            "key": api_key,
            "cx": search_engine_id,
            "num": num_results,
            "start": start_index,
        }
        #Implementing the search API
        response = requests.get(url, params=params)

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data["error"]["message"]
            except Exception:
                error_msg = response.text  # fallback if json parsing fails
            raise Exception(f"Search error: {error_msg}")

        data = response.json()

        return [
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "formattedUrl": item.get("formattedUrl", ""),
                "pagemap": {
                    k: v for k, v in item.get("pagemap", {}).items() #storing metadata dor better scoring, can help in identfying factual news sources
                    if k not in ["cse_image", "cse_thumbnail", "thumbnail"] #removing unnecessary image data since the pipeline can't currently process it
                },
            }
            for item in data.get("items", [])
        ]

    def score_links(self, links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        system_prompt = Prompts.scoring
        human_prompt = "{query}, {intent}, {topics}, {location}, {time}, {title}, {snippet}, {url}, {formattedurl}, {metadata}"
        prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
        chain = prompt | llm

        scored_links: List[Dict[str, Any]] = []
        for link_data in links:
            try:
                response = chain.invoke({
                    "query": self.query,
                    "intent": self.intent,
                    "topics": self.topics,
                    "location": self.location,
                    "time": self.time,
                    "title": link_data["title"],
                    "snippet": link_data["snippet"],
                    "url": link_data["link"],
                    "formattedurl": link_data["formattedUrl"],
                    "metadata": link_data["pagemap"],
                })

                scores = self.output_handler.clean_llm_output(response.content)
                scored_links.append(link_data | scores)

            except Exception as e: #Very frequent Resource exhaustion errors, need to handle them
                if "ResourceExhausted" in str(e):
                    print(f"ResourceExhausted Error: {e}")
                    print("Saving scored links so far...")
                    self.file_handler.save_json(scored_links, self.score_output_dir)
                    return scored_links
                else:
                    print(f"Error during scoring: {e}")
                    continue

            time.sleep(1)
        return scored_links

    def collect_all_links(self) -> List[Dict[str, Any]]:
        print("Collecting links from search...")
        all_links: List[Dict[str, Any]] = []
        page_number = 0

        while page_number < self.max_search_pages and len(all_links) < self.max_total_filtered_links:
            start_index = page_number * self.num_results_per_page + 1 #If there are not enough links move to the next page by adjusting the start index.
            remaining_needed = self.max_total_filtered_links - len(all_links)

            try:
                raw_links = self.get_results_from_search(
                    self.search_terms[0],
                    self.API_KEY,
                    self.SEARCH_ENGINE_ID,
                    start_index,
                    min(self.num_results_per_page, remaining_needed)
                )
            except Exception as e:
                print(f"Search error: {e}")
                break

            if not raw_links:
                break

            all_links.extend(raw_links)
            page_number += 1

        return all_links

    def rank(self) -> None:
        print("Ranking the sources...")
        all_filtered_links: List[Dict[str, Any]] = []

        all_links = self.collect_all_links()
        if not all_links:
            print("No links found to rank.")
            return

        scored_links = self.score_links(all_links)
        if not scored_links:
            print("No scored links to rank.")
            return

        avg_score = sum(l["score"] for l in scored_links) / len(scored_links) #fILTERING OUT SOURCES WHICH RANK LOWER THAN AVERAGE 
        filtered = [l for l in scored_links if l["score"] >= math.floor(avg_score)]

        all_filtered_links.extend(filtered)

        all_filtered_links = all_filtered_links[:self.max_total_filtered_links]  # Ensure we don't exceed 10
        self.file_handler.save_json(all_filtered_links, self.score_output_dir)
        print(f"Saved {len(all_filtered_links)} ranked links.")
