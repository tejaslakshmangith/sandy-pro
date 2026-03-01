"""Gemini AI service for rock/mineral/ore classification."""

import json
import logging
import re
from io import BytesIO

import google.generativeai as genai
from PIL import Image

from backend.config import Config

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """You are an expert geological AI assistant for smart mining operations with deep knowledge of mineralogy, petrology, and ore characterization.

Analyze the provided image/description and return a JSON response with the following structure:
{
  "category": "ore|mineral|rock|stone",
  "specific_name": "exact geological name",
  "common_name": "common trade name if any",
  "chemical_formula": "chemical formula if applicable",
  "color_description": "observed colors",
  "texture": "crystalline|massive|granular|foliated|etc",
  "luster": "metallic|vitreous|resinous|etc",
  "hardness_mohs": 1-10,
  "purity_percentage": 0-100,
  "quality_grade": "A1|A2|A3|B1|B2|B3|C1|C2",
  "commercial_value": "premium|high|medium|low|marginal",
  "mining_suitability": "open-pit|underground|placer|quarry|not-recommended",
  "primary_elements": ["Fe", "Si"],
  "associated_minerals": ["quartz", "pyrite"],
  "formation_type": "igneous|sedimentary|metamorphic|hydrothermal",
  "geological_age": "estimated age or era",
  "industrial_uses": ["steel production", "jewelry"],
  "confidence_score": 0-100,
  "analysis_notes": "detailed geological analysis paragraph",
  "extraction_difficulty": "easy|moderate|difficult|very-difficult",
  "environmental_impact": "low|moderate|high",
  "market_value_usd_per_ton": 0,
  "recommended_processing": "crushing|flotation|smelting|leaching|etc"
}

Grade Scale:
- A1: Purity >= 95% — Premium export quality
- A2: Purity 85-94% — High commercial grade
- A3: Purity 75-84% — Standard industrial grade
- B1: Purity 65-74% — Low industrial grade
- B2: Purity 55-64% — Processing required
- B3: Purity 45-54% — Heavy processing needed
- C1: Purity 30-44% — Marginal viability
- C2: Purity < 30% — Waste/gangue material

Return ONLY valid JSON. No markdown, no extra text."""

FAST_PROMPT = """You are a geological expert. Analyze this rock/mineral/ore sample and return ONLY a JSON object with:
{
  "category": "ore|mineral|rock|stone",
  "specific_name": "geological name",
  "purity_percentage": 0-100,
  "quality_grade": "A1|A2|A3|B1|B2|B3|C1|C2",
  "confidence_score": 0-100,
  "commercial_value": "premium|high|medium|low|marginal"
}"""


def _configure_genai():
    """Configure genai with API key."""
    if Config.GEMINI_API_KEY:
        genai.configure(api_key=Config.GEMINI_API_KEY)


def _extract_json(text: str) -> dict:
    """Extract JSON from model response, handling markdown code blocks."""
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    return json.loads(text)


def analyze_image(image_bytes: bytes, description: str = "") -> dict:
    """Analyze an image using Gemini 2.5 Pro for deep classification.

    Args:
        image_bytes: Raw image bytes.
        description: Optional text description of the sample.

    Returns:
        Classification dict.

    Raises:
        Exception: If Gemini API call fails.
    """
    _configure_genai()

    pro_model = genai.GenerativeModel(
        model_name=Config.GEMINI_PRO_MODEL,
        generation_config={
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        },
    )

    image = Image.open(BytesIO(image_bytes))

    prompt = CLASSIFICATION_PROMPT
    if description:
        prompt += f"\n\nAdditional description from user: {description}"

    response = pro_model.generate_content([prompt, image])
    return _extract_json(response.text)


def analyze_description(description: str) -> dict:
    """Analyze a text description using Gemini 2.5 Flash for fast classification.

    Args:
        description: Text description of the mineral/rock/ore sample.

    Returns:
        Classification dict.

    Raises:
        Exception: If Gemini API call fails.
    """
    _configure_genai()

    flash_model = genai.GenerativeModel(
        model_name=Config.GEMINI_FLASH_MODEL,
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        },
    )

    prompt = f"{CLASSIFICATION_PROMPT}\n\nSample description: {description}"
    response = flash_model.generate_content(prompt)
    return _extract_json(response.text)


def fast_classify(image_bytes: bytes) -> dict:
    """Fast classification using Gemini 2.5 Flash.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Basic classification dict.

    Raises:
        Exception: If Gemini API call fails.
    """
    _configure_genai()

    flash_model = genai.GenerativeModel(
        model_name=Config.GEMINI_FLASH_MODEL,
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 512,
            "response_mime_type": "application/json",
        },
    )

    image = Image.open(BytesIO(image_bytes))
    response = flash_model.generate_content([FAST_PROMPT, image])
    return _extract_json(response.text)
