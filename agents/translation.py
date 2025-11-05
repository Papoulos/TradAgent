import json
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from agents.review import review_and_merge_text

def translate_text(text_blocks: list, glossary: dict, author_profile: dict, max_blocks: int = None, use_reviewer: bool = False):
    """
    Translates text blocks using an LLM and an optional reviewer agent for stylistic consistency.
    """
    if max_blocks is not None and max_blocks > 0:
        text_blocks = text_blocks[:max_blocks]

    translated_blocks = []
    final_reviewed_text_parts = []
    total_blocks = len(text_blocks)
    last_reviewed_block_index = -1

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

        if use_reviewer and len(translated_blocks) > 0 and len(translated_blocks) % 5 == 0:
            print(f"🔬 Reviewing blocks from {len(translated_blocks) - 4} to {len(translated_blocks)}...")

            segments_to_review = translated_blocks[-5:]

            start_index = max(0, i - 9)
            end_index = i + 1
            source_window = text_blocks[start_index:end_index]

            reviewed_part = review_and_merge_text(
                translated_segments=segments_to_review,
                source_segments=source_window,
                glossary=glossary_terms,
                author_profile=style_summary
            )
            final_reviewed_text_parts.append(reviewed_part)
            last_reviewed_block_index = i

    if use_reviewer:
        remaining_blocks = translated_blocks[last_reviewed_block_index + 1:]
        if remaining_blocks:
            print(f"🔬 Reviewing the final {len(remaining_blocks)} blocks...")

            start_index_source = last_reviewed_block_index + 1
            source_window_start = max(0, start_index_source - (10 - len(remaining_blocks)))
            source_window = text_blocks[source_window_start:]

            reviewed_part = review_and_merge_text(
                translated_segments=remaining_blocks,
                source_segments=source_window,
                glossary=glossary_terms,
                author_profile=style_summary
            )
            final_reviewed_text_parts.append(reviewed_part)

        print("✅ Translation and review complete.")
        return "\n\n".join(final_reviewed_text_parts)
    else:
        print("✅ Translation complete (reviewer not activated).")
        return "\n\n".join(translated_blocks)
