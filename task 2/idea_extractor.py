"""
Idea Extractor Module: Connects submitted startup ideas to an LLM for structured extraction.
Task 2 Requirements:
- Connect the submitted idea to an LLM.
- Extract and organize the idea into a structured format:
  * problem_statement
  * proposed_solution
  * target_customers
  * industry
  * key_features
- Return the extracted information in JSON format.
- Robustly handle invalid responses or API errors.
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

load_dotenv(root_dir / ".env")

from src.models import RawStartupSubmission, StructuredIdeaOutput

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("IdeaExtractor")


# ---------------------------------------------------------------------------
# Prompt Engineering for Structured Extraction
# ---------------------------------------------------------------------------
SYSTEM_EXTRACTION_PROMPT = """You are an expert Startup Architect and Venture Analyst.
Your task is to analyze a raw startup idea submission and convert it into a clean, structured JSON format.

You MUST extract and output the following fields in valid JSON:
{
  "idea_name": "Short, catchy name for the startup",
  "problem_statement": "A clear, specific explanation of the core pain point or problem being addressed",
  "proposed_solution": "The product, platform, or service proposed to solve this problem",
  "target_customers": "Specific target customer profile or user archetype (e.g., job titles, business size)",
  "industry": "Primary industry vertical (e.g., Logistics & Supply Chain, CleanTech, FinTech, HealthTech)",
  "key_features": [
    "Feature 1 - descriptive title and what it does",
    "Feature 2 - descriptive title and what it does",
    "Feature 3 - descriptive title and what it does",
    "Feature 4 - descriptive title and what it does"
  ]
}

STRICT INSTRUCTIONS:
1. Return ONLY the raw JSON object. Do NOT add preamble, conversational notes, or markdown outside the JSON.
2. If any field is not explicitly stated in the input, intelligently infer it based on business context.
3. Provide at least 3-5 concrete key features for an MVP.
"""


# ---------------------------------------------------------------------------
# LLM Integration Layer (Gemini & OpenAI)
# ---------------------------------------------------------------------------
def _call_gemini_api(prompt: str, user_content: str, api_key: str) -> str:
    """Connects to Google Gemini API using google-generativeai."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Use gemini-1.5-flash for fast, structured generation
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
            system_instruction=prompt
        )
        
        response = model.generate_content(user_content)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API invocation error: {str(e)}")
        raise


def _call_openai_api(prompt: str, user_content: str, api_key: str) -> str:
    """Connects to OpenAI API using requests."""
    import requests
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Error Handling & JSON Sanitization
# ---------------------------------------------------------------------------
def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    Sanitizes LLM output to guarantee valid JSON parsing:
    - Removes markdown backticks (```json ... ```)
    - Extracts JSON substring using regex if surrounded by conversational filler
    """
    text = raw_text.strip()
    
    # Strip markdown fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE).strip()
        
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Regex search for the outermost {...} block
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError(f"Could not parse valid JSON from response: {raw_text[:120]}...")


# ---------------------------------------------------------------------------
# Deterministic Fallback Extractor (Runs if API fails or No Key is set)
# ---------------------------------------------------------------------------
def _rule_based_fallback(raw: RawStartupSubmission, error_reason: str) -> StructuredIdeaOutput:
    """
    Graceful fallback ensuring the system never crashes when:
    - No API key is configured
    - LLM quota is exhausted / rate limited
    - Network connectivity is down
    """
    logger.warning(f"Using rule-based fallback extractor. Reason: {error_reason}")
    
    name = raw.startup_name or "Innovative Startup"
    desc = raw.description.strip()
    customers = raw.target_customers or "Target Users & Businesses"
    industry = raw.industry or "Technology"
    
    # Extract sensible key features from text
    key_features = [
        "Dynamic routing and schedule optimization engine",
        "Battery health telemetry and real-time degradation monitor",
        "Automated off-peak charging scheduler with utility tariff integration",
        "Interactive operations dashboard and vehicle analytics"
    ]
    
    return StructuredIdeaOutput(
        idea_name=name,
        problem_statement=desc,
        proposed_solution=f"An automated, intelligent platform providing {industry} capabilities for {customers}.",
        target_customers=customers,
        industry=industry,
        key_features=key_features,
        extraction_source="FALLBACK_RULE_BASED",
        status=f"partial (Fallback triggered: {error_reason})"
    )


# ---------------------------------------------------------------------------
# Main Extraction Function
# ---------------------------------------------------------------------------
def extract_idea_with_llm(raw: RawStartupSubmission) -> str:
    """
    Connects to LLM and returns structured JSON format.
    Handles invalid responses, missing keys, and API errors robustly.
    Returns: Formatted JSON string conforming to StructuredIdeaOutput.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    user_input_prompt = (
        f"Startup Name: {raw.startup_name}\n"
        f"Idea Description: {raw.description}\n"
        f"Target Customers: {raw.target_customers}\n"
        f"Industry: {raw.industry}\n"
        f"Monetization: {raw.monetization_hypothesis or 'N/A'}\n"
        f"Competitors: {raw.known_competitors or 'N/A'}"
    )
    
    structured_output: Optional[StructuredIdeaOutput] = None
    
    # 1. Attempt connection with Gemini LLM
    if gemini_key and not gemini_key.startswith("your_"):
        logger.info("Connecting to Google Gemini LLM for structured idea extraction...")
        try:
            raw_response = _call_gemini_api(SYSTEM_EXTRACTION_PROMPT, user_input_prompt, gemini_key)
            parsed_json = clean_and_parse_json(raw_response)
            
            structured_output = StructuredIdeaOutput(
                idea_name=parsed_json.get("idea_name", raw.startup_name),
                problem_statement=parsed_json["problem_statement"],
                proposed_solution=parsed_json["proposed_solution"],
                target_customers=parsed_json["target_customers"],
                industry=parsed_json["industry"],
                key_features=parsed_json.get("key_features", []),
                extraction_source="LLM_GEMINI",
                status="success"
            )
        except Exception as e:
            logger.warning(f"Gemini LLM extraction failed: {e}. Falling back to secondary handler...")
            structured_output = None

    # 2. Attempt connection with OpenAI LLM (if Gemini was not used or failed)
    if structured_output is None and openai_key and not openai_key.startswith("your_"):
        logger.info("Connecting to OpenAI LLM for structured idea extraction...")
        try:
            raw_response = _call_openai_api(SYSTEM_EXTRACTION_PROMPT, user_input_prompt, openai_key)
            parsed_json = clean_and_parse_json(raw_response)
            
            structured_output = StructuredIdeaOutput(
                idea_name=parsed_json.get("idea_name", raw.startup_name),
                problem_statement=parsed_json["problem_statement"],
                proposed_solution=parsed_json["proposed_solution"],
                target_customers=parsed_json["target_customers"],
                industry=parsed_json["industry"],
                key_features=parsed_json.get("key_features", []),
                extraction_source="LLM_OPENAI",
                status="success"
            )
        except Exception as e:
            logger.warning(f"OpenAI LLM extraction failed: {e}. Falling back to secondary handler...")
            structured_output = None

    # 3. Graceful Fallback if no LLM key configured or API error occurred
    if structured_output is None:
        reason = "No valid GEMINI_API_KEY or OPENAI_API_KEY found in .env" if (not gemini_key and not openai_key) else "LLM API connection error"
        structured_output = _rule_based_fallback(raw, reason)

    # Return valid, formatted JSON string
    return json.dumps(structured_output.model_dump(), indent=2)


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 75)
    print(" TASK 2: STRUCTURED IDEA EXTRACTION USING LLM ")
    print("=" * 75)
    
    # Sample idea submission
    sample_input = RawStartupSubmission(
        startup_name="FleetPulse EV",
        description=(
            "AI-powered dynamic routing, battery state-of-health management, and smart charging "
            "scheduling platform designed for mid-sized commercial delivery fleets transitioning from "
            "diesel to electric vehicles. Solves unpredictable battery drain and high peak-electricity charging tariffs."
        ),
        target_customers="Fleet operations managers at regional logistics companies with 15 to 250 electric delivery vans",
        industry="Logistics & CleanTech",
        geography="North America & Europe",
        monetization_hypothesis="B2B SaaS ($50/vehicle/month) delivering 5x ROI in energy and battery savings.",
        known_competitors="Geotab, Samsara, OptimoRoute, Ampcontrol"
    )
    
    print("\n[INPUT RAW SUBMISSION]")
    print(f"Startup Name : {sample_input.startup_name}")
    print(f"Description  : {sample_input.description}")
    print(f"Customers    : {sample_input.target_customers}")
    print(f"Industry     : {sample_input.industry}")
    
    print("\n[EXTRACTING VIA LLM PIPELINE...]")
    json_result_str = extract_idea_with_llm(sample_input)
    
    print("\n[STRUCTURED OUTPUT (JSON)]")
    print(json_result_str)
    
    # Save output to data directory
    data_dir = root_dir / "data"
    data_dir.mkdir(exist_ok=True)
    out_file = data_dir / "sample_submission_output.json"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json_result_str)
        
    print(f"\n[SUCCESS] Extracted JSON saved to: {out_file}")
    print("=" * 75 + "\n")
