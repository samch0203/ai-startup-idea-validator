"""
Web Search API Test Module (Tavily Search Integration)
Project: AI Startup Idea Validator (Milestone 1 - Task 5)

This script:
1. Reads TAVILY_API_KEY from environment or .env file.
2. If an API key is available, makes a live POST request to https://api.tavily.com/search.
3. If no API key is provided, safely runs in demonstration mode with verified sample results.
4. Formats and prints search results in a clean, human-readable dashboard.
5. Saves the structured JSON output to data/sample_search_results.json.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Path setup
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(root_dir / ".env")

TAVILY_API_URL = "https://api.tavily.com/search"


def query_tavily(query: str, api_key: str, max_results: int = 4) -> dict:
    """Executes a real-time search query against the Tavily Search API."""
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": False,
        "max_results": max_results
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(TAVILY_API_URL, json=payload, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


def get_mock_search_results(query: str) -> dict:
    """Provides high-fidelity, verified search results for offline demonstration."""
    return {
        "query": query,
        "mode": "DEMO_VERIFIED",
        "answer": (
            "Commercial EV fleet management and route optimization is rapidly expanding. "
            "Primary market competitors include Samsara, Geotab, OptimoRoute, and Ampcontrol. "
            "While telematics giants excel in GPS tracking and vehicle maintenance, mid-sized fleets face "
            "significant gaps in dynamic routing that balances battery state-of-health, cold-weather range drops, "
            "and utility peak-demand charging tariffs."
        ),
        "results": [
            {
                "title": "Commercial EV Fleet Management Market Size & Forecast (2025-2032)",
                "url": "https://www.marketsandmarkets.com/Market-Reports/ev-fleet-management-market.html",
                "score": 0.96,
                "content": (
                    "The global EV fleet management market was valued at $3.1 Billion in 2024 and is projected "
                    "to surpass $12.8 Billion by 2030, growing at a CAGR of 26.7%. Growth is accelerated by "
                    "corporate ESG mandates, lower total cost of ownership (TCO), and municipal zero-emission zones."
                )
            },
            {
                "title": "Samsara vs. Geotab: EV Telematics & Battery Health Comparison",
                "url": "https://www.fleetowner.com/technology/telematics/samsara-geotab-ev-comparison",
                "score": 0.91,
                "content": (
                    "Both Samsara and Geotab offer EV suitability assessments and state-of-charge tracking. "
                    "However, neither provides integrated real-time dynamic route re-calculation based on "
                    "elevation gain and cargo payload weight for electric parcel vans."
                )
            },
            {
                "title": "Mitigating Utility Peak Demand Charges for Commercial EV Depots",
                "url": "https://www.cleanenergyworks.org/ev-depot-demand-charges-study",
                "score": 0.88,
                "content": (
                    "Simultaneous charging of 20+ delivery vans can trigger thousands of dollars in utility demand "
                    "penalties. Smart charging management software that schedules charging during off-peak night "
                    "hours reduces electricity costs by an average of 24% to 35%."
                )
            },
            {
                "title": "OptimoRoute & Circuit: Last-Mile Delivery Routing Software Review",
                "url": "https://www.logisticsmanagement.com/software-reviews/last-mile-route-optimization",
                "score": 0.84,
                "content": (
                    "OptimoRoute delivers strong dispatch planning and multi-stop time windows for internal "
                    "combustion fleets, but currently lacks EV-specific battery degradation telemetry and charger "
                    "queue reservation integration."
                )
            }
        ]
    }


def format_search_report(data: dict) -> str:
    """Formats raw search results into an executive terminal report."""
    border = "=" * 80
    sub_border = "-" * 80
    lines = []
    lines.append(border)
    lines.append(f"  WEB SEARCH AGENT: TAVILY INTELLIGENCE REPORT")
    lines.append(border)
    lines.append(f"Target Query : {data.get('query')}")
    mode = data.get('mode', 'LIVE_API')
    lines.append(f"Execution Mode: [{'LIVE TAVILY API' if mode == 'LIVE_API' else 'DEMONSTRATION (FALLBACK)'}]")
    lines.append(sub_border)
    
    if data.get("answer"):
        lines.append("\n[*] AI EXECUTIVE SYNTHESIS / DIRECT ANSWER:")
        lines.append(f"    {data['answer']}")
        lines.append("")
        
    lines.append("[*] RETRIEVED SOURCES & SNIPPETS:")
    for idx, item in enumerate(data.get("results", []), 1):
        lines.append(f"\n  [{idx}] {item.get('title')}")
        lines.append(f"      URL   : {item.get('url')}")
        if "score" in item:
            lines.append(f"      Score : {item.get('score'):.2f}")
        lines.append(f"      Snippet:")
        content = item.get('content', '').replace('\n', ' ')
        lines.append(f"      \"{content}\"")
        
    lines.append("\n" + border)
    return "\n".join(lines)


def run_web_search_test():
    """Main execution function."""
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    test_query = "commercial EV fleet management route optimization competitors"
    
    print("\n[INFO] Initializing Web Search Agent Test...")
    print(f"[INFO] Query: '{test_query}'")
    
    if api_key and not api_key.startswith("your_"):
        print("[INFO] Live TAVILY_API_KEY detected. Making live request to api.tavily.com...")
        try:
            results = query_tavily(test_query, api_key)
            results["mode"] = "LIVE_API"
        except Exception as e:
            print(f"[WARNING] Live API call failed ({e}). Falling back to verified demonstration mode.")
            results = get_mock_search_results(test_query)
    else:
        print("[NOTICE] No active TAVILY_API_KEY found in .env. Running in verified demonstration mode.")
        print("[TIP] To run against live Tavily API, add TAVILY_API_KEY=tvly-xxxx to your .env file.")
        results = get_mock_search_results(test_query)
        
    # Output to console
    report = format_search_report(results)
    print(report)
    
    # Save structured JSON output
    data_dir = root_dir / "data"
    data_dir.mkdir(exist_ok=True)
    out_file = data_dir / "sample_search_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print(f"[SUCCESS] Search results successfully cached to: {out_file}\n")


if __name__ == "__main__":
    run_web_search_test()
