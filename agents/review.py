import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama

def review_and_merge_text(translated_segments: list, source_segments: list, glossary: dict, author_profile: dict):
    """
    Reviews and merges translated text segments using an LLM to ensure stylistic and tonal continuity.
    """
    num_segments = len(translated_segments)
    author_profile_str = author_profile
    glossary_terms_str = glossary
    source_excerpt_str = "\n---\n".join(source_segments)
    translated_segments_str = "\n---\n".join(translated_segments)

    reviewer_prompt = f"""
You are a text-processing agent. Your task is to assemble and harmonize a series of translated text segments.

**Input:**
- **Author Profile:** A description of the author's style.
- **Glossary:** A list of specific terms to be used consistently.
- **Source Segments:** {num_segments} original English text segments.
- **Translated Segments:** {num_segments} French translated text segments.

**Instructions:**
1. **Assemble:** Concatenate the provided French translated segments in the order they are given.
2. **Harmonize:** Make minor corrections to ensure stylistic and tonal continuity, smooth transitions, and consistent vocabulary based on the author profile and glossary.
3. **Output:** Return *only* the final, clean, merged French text. Do not add any extra text, commentary, or explanations. Do not re-narrate or create a story.

**Author Profile:**
{author_profile_str}

**Glossary:**
{glossary_terms_str}

**Source Segments (for context):**
---
{source_excerpt_str}
---

**Translated Segments (to assemble and harmonize):**
---
{translated_segments_str}
---
"""

    if config.LLM_TOOL == "gemini":
        llm = ChatGoogleGenerativeAI(model=config.GLOSSARY_CREATION_MODEL)
    elif config.LLM_TOOL == "ollama":
        llm = ChatOllama(model=config.OLLAMA_GLOSSARY_CREATION_MODEL)
    else:
        raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

    result = llm.invoke(reviewer_prompt)
    return result.content.strip()
