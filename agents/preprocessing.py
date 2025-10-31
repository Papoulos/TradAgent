import json
import re
import yake
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama


def create_glossary(source_text: str, max_words: int = 100):
    """
    Creates a glossary of ambiguous words, proper nouns, and untranslatable words
    from the source text using YAKE and a large language model.
    """
    print("🔍 Extracting terms with YAKE...")
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,
        dedupLim=0.9,
        top=max_words,
        features=None
    )
    keywords = kw_extractor.extract_keywords(source_text)
    candidate_terms = [kw for kw, score in keywords]
    print(f"✅ {len(candidate_terms)} terms extracted.")

    print("🤖 Sending to LLM for validation...")
    prompt = f"""
You are a terminology expert. You will select from the list below only the terms that are **specific to the book** and **require inclusion in a translation glossary**.

**Book Context**
- Title: {config.BOOK_CONTEXT.get('book_title', 'N/A')}
- Author: {config.BOOK_CONTEXT.get('author', 'N/A')}
- Theme: {config.BOOK_CONTEXT.get('theme_description', 'N/A')}
- Style: {config.BOOK_CONTEXT.get('author_style', 'N/A')}
- Audience: {config.BOOK_CONTEXT.get('target_audience', 'N/A')}
- Cultural Context: {config.BOOK_CONTEXT.get('cultural_context', 'N/A')}

**Instructions:**
1. Keep only the terms that are **ambiguous, metaphorical, or culturally specific**.
2. Exclude generic words.
3. Prefer terms that have **social, psychological, or cultural significance** in the text depending of the context.
4. Output a JSON list of selected English terms only.

**Candidate Terms (from automatic extraction):**
{json.dumps(candidate_terms, ensure_ascii=False, indent=2)}
"""

    if config.LLM_TOOL == "gemini":
        llm = ChatGoogleGenerativeAI(model=config.GLOSSARY_CREATION_MODEL)
    elif config.LLM_TOOL == "ollama":
        llm = ChatOllama(model=config.OLLAMA_GLOSSARY_CREATION_MODEL)
    else:
        raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

    result = llm.invoke(prompt)
    response = result.content.strip()

    try:
        # Look for a JSON array first, as requested in the prompt
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            json_str = match.group(0)
            glossary = json.loads(json_str)
        else:
            # Fallback for JSON object responses
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                json_str = match.group(0)
                glossary = json.loads(json_str)
            else:
                raise ValueError("No JSON detected")
        print(f"✅ Translated Glossary: {len(glossary)} entries.")
    except Exception as e:
        print(f"⚠️ JSON parsing error ({e}). Raw response:\n{response}")
        glossary = []

    return glossary


def evaluate_glossary(glossary: list[str]):
    """
    Evaluates the glossary using a large language model.
    """
    if config.LLM_TOOL == "gemini":
        llm = ChatGoogleGenerativeAI(model=config.GEMINI_EVALUATION_MODEL)
    elif config.LLM_TOOL == "ollama":
        llm = ChatOllama(model=config.OLLAMA_EVALUATION_MODEL)
    else:
        raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

    prompt = f"Here is a glossary of terms: {', '.join(glossary)}. Please review it for accuracy and suggest any improvements."

    result = llm.invoke(prompt)
    return result.content
