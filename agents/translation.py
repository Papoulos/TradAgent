import json
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama

def translate_text(text_blocks: list, glossary: dict, author_profile: dict):
    """
    Translates text blocks using an LLM, incorporating context and stylistic elements.
    """
    translated_blocks = []
    total_blocks = len(text_blocks)

    print("🤖 Starting translation...")

    author_name = author_profile.get("author", "Unknown")
    style_analysis = author_profile.get("style_analysis", {})
    style_summary = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in style_analysis.items()])
    glossary_terms = json.dumps(glossary, ensure_ascii=False, indent=2)

    for i, segment in enumerate(text_blocks):
        print(f"🔄 Translating block {i + 1}/{total_blocks}...")

        previous_translated_segment = translated_blocks[i - 1] if i > 0 else "None"
        next_segment = text_blocks[i + 1] if i < total_blocks - 1 else "None"

        prompt = f"""
You are a professional literary translator.

**Objective:**
Translate the following English text into {config.TARGET_LANGUAGE},
preserving the author’s tone, humor, and narrative rhythm.

**Context:**
- Author: {author_name}
- Style Analysis:
{style_summary}
- Glossary: {glossary_terms}
- Previous Translated Segment (for continuity): {previous_translated_segment}
- Next Segment (for context): {next_segment}

**Instructions:**
1. Maintain the author’s voice and rhythm.
2. Use glossary terms exactly as defined.
3. Ensure transitions are fluid between segments.
4. Avoid literal translation when a natural {config.TARGET_LANGUAGE} expression exists.
5. Output ONLY the translated {config.TARGET_LANGUAGE} text.

**Text to translate:**
---
{segment}
---
"""

        if config.LLM_TOOL == "gemini":
            llm = ChatGoogleGenerativeAI(model=config.GLOSSARY_CREATION_MODEL)
        elif config.LLM_TOOL == "ollama":
            llm = ChatOllama(model=config.OLLAMA_GLOSSARY_CREATION_MODEL)
        else:
            raise ValueError(f"Unsupported LLM tool: {config.LLM_TOOL}")

        result = llm.invoke(prompt)
        translated_segment = result.content.strip()
        translated_blocks.append(translated_segment)

    print("✅ Translation complete.")
    return "\n\n".join(translated_blocks)
