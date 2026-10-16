"""
Interactive Pipeline Viewer: Displays the sample structured output and search results.
Usage: python src/view_sample_pipeline.py
"""

import json
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
idea_file = root_dir / "data" / "sample_submission_output.json"
search_file = root_dir / "data" / "sample_search_results.json"


def display_pipeline():
    border = "=" * 80
    print("\n" + border)
    print("      AI STARTUP IDEA VALIDATOR — SAMPLE PIPELINE DEMONSTRATION")
    print(border)

    # 1. Load Idea Output
    if idea_file.exists():
        with open(idea_file, "r", encoding="utf-8") as f:
            idea_data = json.load(f)
            
        print("\n[STEP 1: STRUCTURED IDEA INTAKE]")
        print(f"  Idea Name      : {idea_data.get('idea_name')}")
        print(f"  Tagline        : {idea_data.get('tagline')}")
        print(f"  Industry       : {idea_data.get('primary_industry')}")
        print(f"  Target Market  : {idea_data.get('target_geography')}")
        print(f"  Monetization   : {idea_data.get('monetization_model')}")
        print(f"  Painkiller/Vit : {idea_data.get('target_customer', {}).get('urgency_level')}")
        print(f"  Problem Summary: {idea_data.get('problem_statement')}")
        print(f"  Target Queries Generated for Search Agent:")
        for q in idea_data.get("search_queries", []):
            print(f"    - \"{q}\"")
    else:
        print("[!] sample_submission_output.json not found. Run: python src/idea_extractor.py first.")

    # 2. Load Web Search Output
    if search_file.exists():
        with open(search_file, "r", encoding="utf-8") as f:
            search_data = json.load(f)
            
        print("\n" + "-" * 80)
        print("[STEP 2: WEB SEARCH AGENT INTELLIGENCE (TAVILY)]")
        print(f"  Query Executed : {search_data.get('query')}")
        print(f"\n  AI Synthesis / Direct Answer:")
        print(f"  {search_data.get('answer')}\n")
        print("  Top Retrieved Industry Sources:")
        for idx, src in enumerate(search_data.get("results", [])[:3], 1):
            print(f"    [{idx}] {src.get('title')}")
            print(f"        URL  : {src.get('url')}")
            snippet = src.get('content', '')[:160] + "..."
            print(f"        Info : {snippet}")
    else:
        print("[!] sample_search_results.json not found. Run: python src/web_search_test.py first.")

    print("\n" + border)
    print("  Validation Status: READY FOR MILESTONE 2 (Market & Competitor Agents)")
    print(border + "\n")


if __name__ == "__main__":
    display_pipeline()
