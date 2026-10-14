
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

TAVILY_API_URL = "https://api.tavily.com/search"


def generate_search_queries(startup_idea: str) -> list[str]:
    """Generate queries for market research and competitor discovery."""

    if not isinstance(startup_idea, str) or not startup_idea.strip():
        raise ValueError("Startup idea cannot be empty.")

    idea = " ".join(startup_idea.split())

    return [
        f"{idea} market trends and industry analysis",
        f"companies and competitors offering {idea}",
        f"customer needs and problems related to {idea}",
        f"similar startups and alternative solutions for {idea}",
    ]


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web through the Tavily API."""

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is missing. Configure your .env file."
        )

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    payload = {
        "query": query,
        "topic": "general",
        "search_depth": "basic",
        "max_results": max_results,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            TAVILY_API_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

    except requests.Timeout as exc:
        raise RuntimeError("Tavily request timed out.") from exc

    except requests.RequestException as exc:
        raise RuntimeError(f"Tavily API request failed: {exc}") from exc

    except ValueError as exc:
        raise RuntimeError("Tavily returned invalid JSON.") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected Tavily response format.")

    raw_results = data.get("results", [])

    if not isinstance(raw_results, list):
        raise RuntimeError("Tavily results must be a list.")

    results = []

    for item in raw_results:
        if not isinstance(item, dict):
            continue

        title = item.get("title")
        url = item.get("url")
        content = item.get("content", "")

        if not isinstance(title, str) or not isinstance(url, str):
            continue

        if not url.startswith(("https://", "http://")):
            continue

        results.append({
            "title": title,
            "url": url,
            "content": content if isinstance(content, str) else "",
            "score": item.get("score"),
            "search_query": query,
        })

    return results


def run_web_search_agent(startup_idea: str) -> dict:
    """Run multiple searches and combine their results."""

    queries = generate_search_queries(startup_idea)

    all_results = []
    seen_urls = set()
    failed_queries = []

    for query in queries:
        try:
            results = search_web(query)

            for result in results:
                if result["url"] not in seen_urls:
                    seen_urls.add(result["url"])
                    all_results.append(result)

        except (RuntimeError, ValueError) as exc:
            failed_queries.append({
                "query": query,
                "error": str(exc),
            })

    if failed_queries and not all_results:
        raise RuntimeError(
            "All web searches failed: "
            + "; ".join(item["error"] for item in failed_queries)
        )

    if all_results and failed_queries:
        status = "partial"
    elif all_results:
        status = "success"
    else:
        status = "no_results"

    return {
        "startup_idea": startup_idea.strip(),
        "generated_queries": queries,
        "total_results": len(all_results),
        "results": all_results,
        "failed_queries": failed_queries,
        "status": status,
    }


if __name__ == "__main__":
    idea = input("Enter your startup idea: ")

    try:
        output = run_web_search_agent(idea)

        print("\nStatus:", output["status"])
        print("Total results:", output["total_results"])

        print("\nGenerated queries:")
        for query in output["generated_queries"]:
            print("-", query)

        print("\nSearch results:")
        for result in output["results"]:
            print("\nTitle:", result["title"])
            print("URL:", result["url"])
            print("Content:", result["content"][:300])

        if output["failed_queries"]:
            print("\nSome queries failed:")
            for failure in output["failed_queries"]:
                print(failure)

    except (RuntimeError, ValueError) as exc:
        print("\nError:", exc)
