import json
import re
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama

def create_author_profile(author_name: str, text_sample: str):
    """
    Analyzes the writing style of an author and returns a structured JSON profile.
    """
    print(f"🤖 Generating literary profile for {author_name}...")

    prompt = f"""
You are a literary analyst. Your task is to analyze the writing style of an author based on a text sample.

**Instructions:**
1.  Read the provided text sample.
2.  Analyze the author's style based on the text.
3.  Return a JSON object with the following structure:
    {{
        "author": "{author_name or 'Unknown'}",
        "style_analysis": {{
            "tone": "<analysis of the tone>",
            "sentence_structure": "<analysis of sentence structure>",
            "vocabulary": "<analysis of vocabulary>",
            "emotional_register": "<analysis of emotional register>",
            "cultural_context": "<analysis of the cultural context>",
            "comparison_to_other_authors": "<comparison to other authors>"
        }}
    }}

**Text sample:**
---
{text_sample[:2000]}
---

**IMPORTANT: Your response must contain ONLY the JSON object, without any introductory text, explanations, or code block markers (e.g., ```json).**
"""

    if config.LLM_TOOL == "gemini":
        llm = ChatGoogleGenerativeAI(model=config.GLOSSARY_CREATION_MODEL)
    elif config.LLM_TOOL == "ollama":
        llm = ChatOllama(model=config.OLLAMA_GLOSSARY_CREATION_MODEL)
    else:
        raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

    result = llm.invoke(prompt)
    response_text = result.content.strip()

    try:
        # Clean the response to ensure it's a valid JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            profile = json.loads(json_str)
        else:
            print("Error: Could not parse JSON from the LLM response.")
            return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON returned from the LLM.")
        print("LLM Response:", response_text)
        return None

    print(f"✅ Literary profile created for {author_name}.")

    return profile
