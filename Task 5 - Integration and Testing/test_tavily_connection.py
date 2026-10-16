
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise SystemExit(
        "API key not loaded. Check that .env exists "
        "in the project root."
    )

try:
    client = TavilyClient(api_key=api_key)

    response = client.search(
        query="startup market trends in India",
        max_results=2,
    )

    results = response.get("results", [])

    print("Tavily connection successful!")
    print("Number of results:", len(results))

    for result in results:
        print("\nTitle:", result.get("title"))
        print("URL:", result.get("url"))

except Exception as exc:
    print("Tavily search failed:", type(exc).__name__)
    print("Check your API key, internet connection, and Tavily dashboard.")
