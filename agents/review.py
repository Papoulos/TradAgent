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
You are a bilingual literary editor and reviewer.

You will receive {num_segments} consecutive translated text segments from English to French,
along with their original English versions for context.

Your job is to:
1. Verify the **stylistic and tonal continuity** across the {num_segments} segments.
2. **Smooth transitions** between paragraphs and ensure consistent vocabulary.
3. **Correct minor translation inconsistencies** (tense, register, rhythm).
4. Preserve the author's tone as described in the provided profile.
5. Output the final **merged and refined French text** — no commentary, no explanations.

**Author Profile:**
{author_profile_str}

**Glossary (use consistently):**
{glossary_terms_str}

**Source excerpts:**
---
{source_excerpt_str}
---

**Translated segments (to review):**
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
