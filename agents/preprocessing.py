import langextract as lx
import textwrap
import config

def create_glossary(source_text: str, max_words: int = 100):
    """
    Creates a glossary of ambiguous words, proper nouns, and untranslatable words
    from the source text using langextract.
    """
    prompt = textwrap.dedent("""\
        Extract ambiguous words, proper nouns, and words that should not be translated from the text.
        Use exact text for extractions. Do not paraphrase or overlap entities.
        Provide meaningful attributes for each entity to add context.
        """)

    examples = [
        lx.data.ExampleData(
            text="Mr. Smith went to the bank.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="proper_noun",
                    extraction_text="Mr. Smith",
                    attributes={"reason": "Person's name"}
                ),
                lx.data.Extraction(
                    extraction_class="ambiguous_word",
                    extraction_text="bank",
                    attributes={"reason": "Can mean a financial institution or a river bank"}
                ),
            ]
        ),
        lx.data.ExampleData(
            text="The cat sat on the mat.",
            extractions=[]
        )
    ]

    result = lx.extract(
        text_or_documents=source_text,
        prompt_description=prompt,
        examples=examples,
        model_id=config.GLOSSARY_CREATION_MODEL,
    )

    glossary = []
    if result and result.extractions:
        for extraction in result.extractions:
            glossary.append(extraction.extraction_text)

    return glossary[:max_words]

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama

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
