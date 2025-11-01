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
You are a terminology expert. Your task is to create a translation glossary for the following book.

**Book Context**
- Title: {config.BOOK_CONTEXT.get('book_title', 'N/A')}
- Author: {config.BOOK_CONTEXT.get('author', 'N/A')}
- Theme: {config.BOOK_CONTEXT.get('theme_description', 'N/A')}
- Style: {config.BOOK_CONTEXT.get('author_style', 'N/A')}
- Audience: {config.BOOK_CONTEXT.get('target_audience', 'N/A')}
- Cultural Context: {config.BOOK_CONTEXT.get('cultural_context', 'N/A')}
- Target Language: {config.TARGET_LANGUAGE}

**Instructions:**
1. From the candidate terms provided, select only the terms that are **ambiguous, metaphorical, culturally specific, or essential to the story's meaning.**
2. **Exclude common nouns and generic words** that do not require a specific translation in the context of the book.
3. For each selected term, provide a translation in **{config.TARGET_LANGUAGE}**.
4. Return the result as a **JSON object**, where keys are the original English terms and values are their {config.TARGET_LANGUAGE} translations.

**Candidate Terms (from automatic extraction):**
{json.dumps(candidate_terms, ensure_ascii=False, indent=2)}

**Example JSON Output:**
{{
  "example term 1": "translation 1",
  "example term 2": "translation 2"
}}

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

    try:
        # Look for a JSON object first, as requested in the prompt
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            json_str = match.group(0)
            glossary = json.loads(json_str)
        else:
            # Fallback for JSON array responses
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                json_str = match.group(0)
                glossary = json.loads(json_str)
            else:
                raise ValueError("No JSON detected")
        print(f"✅ Translated Glossary: {len(glossary)} entries.")
    except Exception as e:
        print(f"⚠️ JSON parsing error ({e}). Raw response:\n{response}")
        glossary = {}

    return glossary


def evaluate_glossary(glossary: dict[str, str]):
    """
    Filters the glossary by removing common nouns.
    """
    print("🤖 Filtering glossary with LLM...")
    if config.LLM_TOOL == "gemini":
        llm = ChatGoogleGenerativeAI(model=config.GEMINI_EVALUATION_MODEL)
    elif config.LLM_TOOL == "ollama":
        llm = ChatOllama(model=config.OLLAMA_EVALUATION_MODEL)
    else:
        raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

    prompt = f"""
You are a terminology expert. Your task is to refine a translation glossary.

**Instructions:**
1. Review the following JSON glossary.
2. **Remove any entries that are common nouns or generic words** (e.g., "time", "night", "friend").
3. Keep only the terms that are **ambiguous, metaphorical, culturally specific, or essential to the story's meaning.**
4. Return the filtered glossary as a **valid JSON object**.

**Glossary to Filter:**
{json.dumps(glossary, ensure_ascii=False, indent=2)}

**Example JSON Output:**
{{
  "example term 1": "translation 1",
  "example term 2": "translation 2"
}}

**IMPORTANT: Your response must contain only the JSON object, without any introductory text, explanations, or code block markers.**
"""

    result = llm.invoke(prompt)
    response = result.content.strip()

    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            json_str = match.group(0)
            filtered_glossary = json.loads(json_str)
            print(f"✅ Filtered Glossary: {len(filtered_glossary)} entries.")
            return filtered_glossary
        else:
            print("⚠️ No JSON object found in the LLM response for filtering.")
            return glossary
    except Exception as e:
        print(f"⚠️ JSON parsing error during filtering ({e}). Raw response:\n{response}")
        return glossary
