import json
import re
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama

def create_author_profile(author_name: str, text_sample: str):
    """
    Analyzes the writing style of an author or a text sample using an LLM.
    """
    print(f"🤖 Generating literary profile for {author_name}...")

    prompt = f"""
You are a literary analyst. Analyze the writing style of the following author or text.

If an author name is provided, summarize their general writing style.
If a text is provided, analyze its tone, pacing, and stylistic traits.

**Output format:**
Author: {author_name or 'Unknown'}
Style Summary:
- Tone:
- Sentence Structure:
- Vocabulary:
- Emotional register:
- Cultural context:
- Comparison to other authors:

**Text sample (if any):**
---
{text_sample[:2000]}
---

**IMPORTANT: Your response must contain only the JSON object, without any introductory text, explanations, or code block markers.**
"""

    if config.LLM_TOOL == "gemini":
        llm = ChatGoogleGenerativeAI(model=config.GLOSSARY_CREATION_MODEL)
    elif config.LLM_TOOL == "ollama":
        llm = ChatOllama(model=config.OLLAMA_GLOSSARY_CREATION_MODEL)
    else:
        raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

    result = llm.invoke(prompt)
    response = result.content.strip()

    # The prompt asks for a specific format, but not JSON.
    # For now, we'll save the raw text response.
    # In a future step, we could refine the prompt to request JSON.

    # Let's create a simple JSON structure to hold the analysis
    profile = {
        "author": author_name,
        "style_analysis": response
    }

    print(f"✅ Literary profile created for {author_name}.")

    return profile
