import json
import os
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from agents.review import review_and_merge_text

def translate_text(source_dir: str, translated_dir: str, glossary: dict, author_profile: dict, max_blocks: int = None):
    """
    Translates text blocks from files in a source directory and saves them to a translated directory.
    """

    source_files = sorted([f for f in os.listdir(source_dir) if f.endswith('.txt')])

    if max_blocks is not None and max_blocks > 0:
        source_files = source_files[:max_blocks]

    total_blocks = len(source_files)
    print("🤖 Starting translation...")

    for i, filename in enumerate(source_files):
        print(f"🔄 Translating block {i + 1}/{total_blocks} ({filename})...")

        source_filepath = os.path.join(source_dir, filename)
        with open(source_filepath, 'r', encoding='utf-8') as f:
            segment = f.read()

        prompt = f"""
You are a professional literary translator.

**Objective:**
Translate the following English text into {config.TARGET_LANGUAGE}.

**Instructions:**
1. Maintain a natural and fluid {config.TARGET_LANGUAGE} expression.
2. Output ONLY the translated {config.TARGET_LANGUAGE} text.

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

        translated_filepath = os.path.join(translated_dir, filename)
        with open(translated_filepath, 'w', encoding='utf-8') as f:
            f.write(translated_segment)

    print("✅ Translation complete.")


def review_translated_files(source_dir: str, translated_dir: str, revised_dir: str, glossary: dict, author_profile: dict):
    """
    Reviews translated files and saves the harmonized result.
    """
    print("🔬 Starting review process...")

    source_files = sorted([f for f in os.listdir(source_dir) if f.endswith('.txt')])
    translated_files = sorted([f for f in os.listdir(translated_dir) if f.endswith('.txt')])

    style_summary = "\n".join(
        [f"- {k.replace('_', ' ').title()}: {v}" for k, v in author_profile.get("style_analysis", {}).items()])
    glossary_terms = json.dumps(glossary, ensure_ascii=False, indent=2)

    num_files = len(translated_files)
    batch_size = 5
    review_counter = 0

    for i in range(0, num_files, batch_size):
        batch_filenames = translated_files[i:i + batch_size]
        print(f"🔬 Reviewing blocks {i + 1} to {i + len(batch_filenames)}...")

        # Read translated segments for the current batch
        translated_segments = []
        for filename in batch_filenames:
            with open(os.path.join(translated_dir, filename), 'r', encoding='utf-8') as f:
                translated_segments.append(f.read())

        # Determine the context window for source files
        start_index_source = i
        end_index_source = i + len(batch_filenames)

        # Sliding window of 10 for context
        source_window_start = max(0, end_index_source - 10)
        source_filenames = source_files[source_window_start:end_index_source]

        source_segments = []
        for filename in source_filenames:
            with open(os.path.join(source_dir, filename), 'r', encoding='utf-8') as f:
                source_segments.append(f.read())

        # Call the review agent
        reviewed_part = review_and_merge_text(
            translated_segments=translated_segments,
            source_segments=source_segments,
            glossary=glossary_terms,
            author_profile=style_summary
        )

        # Save the reviewed part to a new file in the revised directory
        review_filename = os.path.join(revised_dir, f"reviewed_{review_counter:05d}.txt")
        with open(review_filename, 'w', encoding='utf-8') as f:
            f.write(reviewed_part)
        review_counter += 1

    print("✅ Review complete.")
