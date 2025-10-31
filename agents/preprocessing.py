import textwrap
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama


def create_glossary(source_text: str, max_words: int = 100):
    """
    Creates a glossary of ambiguous words, proper nouns, and untranslatable words
    from the source text using a large language model.
    """
    if config.LLM_TOOL == "gemini":
        llm = ChatGoogleGenerativeAI(model=config.GLOSSARY_CREATION_MODEL)
    elif config.LLM_TOOL == "ollama":
        llm = ChatOllama(model=config.OLLAMA_GLOSSARY_CREATION_MODEL)
    else:
        raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

    prompt = textwrap.dedent(f"""\
        You are an expert in linguistics and translation. Your task is to analyze the following text and extract a glossary of terms that require special attention during translation.

        Please identify the following types of terms:
        1.  **Proper Nouns:** Names of people, places, organizations, and specific titles (e.g., "Mr. Smith", "Wildemount", "the Dwendalian Empire").
        2.  **Ambiguous Words:** Words that could have multiple meanings depending on the context (e.g., "bank", "rock", "lead").
        3.  **Untranslatable or Technical Terms:** Words that should be kept in their original language or that are specific to a domain (e.g., "Dungeons & Dragons", "arcane", "deity").

        Analyze the text provided below and extract these terms.

        **Instructions:**
        - Return a single line of text.
        - The terms should be separated by commas.
        - Do not add any explanation, preamble, or conclusion.
        - Use the exact text for extractions. Do not paraphrase.
        - Limit the list to a maximum of {max_words} of the most important terms.

        **Text to Analyze:**
        ---
        {source_text}
        ---

        **Glossary:**
        """)

    result = llm.invoke(prompt)

    content = result.content.strip()
    if not content:
        return []

    glossary = [term.strip() for term in content.split(',')]
    glossary = [term for term in glossary if term]

    return glossary[:max_words]


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
