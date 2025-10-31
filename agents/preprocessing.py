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

    print("🤖 Sending to Ollama for validation/translation...")
    prompt = f"""
You are a literary expert.
Below is a list of English terms extracted from a book.
Select ONLY the terms that are ambiguous, culturally specific, or essential to understanding the story (e.g., names, unique slang, or invented concepts).
Return them as a JSON array of strings, nothing else.

Terms:
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
