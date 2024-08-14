import random
import string
import httpx
import time
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Constants
MODEL_NAME = "03yl40nq"
YOUR_API_KEY = os.getenv("BASETEN_API_KEY")
MODEL_URL = f"https://model-{MODEL_NAME}.api.baseten.co/production/predict"
CONNECTIONS = 32
TOTAL_REQUESTS = 32
CUSTOM_PROMPT_FIELDS = {"max_tokens": 400}
CUSTOM_FIELDS = {"stream": False}

# Prompt template
prompt_template = """You are tasked with extracting relevant information from a user's query for a financial search engine. Your goal is to identify search keywords and various filters such as time, country, industry, and company from the given query. This will help in creating a more targeted and efficient search. Here's the user's query: <user_query> {USER_QUERY} </user_query> Follow these steps to extract the necessary information: 1. Search Keywords: - Identify the main topics or concepts in the query. - Extract key terms that are essential for the search. - Exclude common words, articles, and prepositions. 2. Time Filter: - Look for any mentions of specific dates, years, or time periods (e.g., 'last quarter', '2022', 'past 5 years'). - If a time frame is mentioned, include it in the time filter. 3. Country Filter: - Identify any country names or regions mentioned in the query. - Include both full country names and their common abbreviations (e.g., 'United States' or 'US'). 4. Industry Filter: - Look for mentions of specific industries or sectors (e.g., 'technology', 'healthcare', 'finance'). - Include any industry-specific terms that could help narrow down the search. 5. Company Filter: - Identify any specific company names mentioned in the query. - Include both full company names and their common abbreviations or stock symbols if present. Return only the output and nothing else in the following format: <extracted_info> <search_keywords> [List the main search keywords, separated by commas] </search_keywords> <time_filter> [Specify the time filter, if any. If none, do not return this field.] </time_filter> <country_filter> [List the countries or regions, if any. If none, do not return this field.] </country_filter> <industry_filter> [List the industries or sectors, if any. If none, do not return this field.] </industry_filter> <company_filter> [List the companies, if any. If none, do not return this field.] </company_filter> </extracted_info>"""


# Companies and user queries
companies = [
    "Apple",
    "Microsoft",
    "Alphabet",
    "Amazon",
    "Facebook",
    "Johnson & Johnson",
    "Procter & Gamble",
    "Coca-Cola",
    "McDonald's",
    "Visa",
    "UnitedHealth Group",
    "Mastercard",
    "Intel",
    "Home Depot",
    "Verizon Communications",
    "Cisco Systems",
    "Pfizer",
    "Merck",
    "3M",
    "ExxonMobil",
    "Chevron",
    "Bristol-Myers Squibb",
    "Amgen",
    "Gilead Sciences",
    "Eli Lilly and Company",
    "PepsiCo",
    "Philip Morris International",
    "Union Pacific",
    "Caterpillar",
    "United Technologies",
    "Boeing",
    "Dow Inc.",
    "Walmart",
    "Disney",
    "McKesson",
]

user_queries = [f"What was {company}'s revenue last quarter?" for company in companies]
prompts = [
    prompt_template.replace("{USER_QUERY}", user_query) for user_query in user_queries
]

# write prompts to a file
with open("prompts.txt", "w") as f:
    for prompt in prompts:
        for prompt in prompts:
            f.write(f"{prompt}\n")
exit()
# Function to send requests and gather stats
def send_request(i):
    formatted_prompt = prompts[i % len(prompts)]
    start_time = time.time()

    resp = session.post(
        MODEL_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YOUR_API_KEY}",
        },
        json={"prompt": formatted_prompt, **CUSTOM_PROMPT_FIELDS},
        **CUSTOM_FIELDS,
    )

    resp.raise_for_status()  # Check for HTTP errors

    total_time = time.time() - start_time
    print(resp.status_code, resp.json())
    total_times.append(total_time)


# Function to print statistics
def get_stats(times):
    total_time_array = np.array(times)
    avg_ttft = np.mean(total_time_array)
    p95_ttft = np.percentile(total_time_array, 95)
    p99_ttft = np.percentile(total_time_array, 99)
    max_ttft = np.max(total_time_array)
    min_ttft = np.min(total_time_array)

    print(f"Average: {avg_ttft:.2f} seconds")
    print(f"95th percentile: {p95_ttft:.2f} seconds")
    print(f"99th percentile: {p99_ttft:.2f} seconds")
    print(f"Maximum: {max_ttft:.2f} seconds")
    print(f"Minimum: {min_ttft:.2f} seconds")


# Execution
session = httpx.Client()
ttfts = []
total_times = []

try:
    with ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        executor.map(send_request, range(TOTAL_REQUESTS))
finally:
    print("Statistics")
    print("Time to first token:")
    get_stats(total_times)
