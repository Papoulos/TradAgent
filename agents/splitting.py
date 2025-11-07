import tiktoken
import config
import os

def split_text(text: str, output_dir: str):
    """
    Splits the text into blocks of approximately a given token size, respecting paragraph boundaries,
    and saves them as numbered files in the output directory.
    """
    tokenizer = tiktoken.get_encoding("cl100k_base")

    paragraphs = text.split('\n\n')

    blocks = []
    current_block = ""
    current_block_token_count = 0

    for paragraph in paragraphs:
        paragraph_token_count = len(tokenizer.encode(paragraph))

        if current_block_token_count + paragraph_token_count > config.TOKENS_PER_BLOCK:
            blocks.append(current_block)
            current_block = paragraph
            current_block_token_count = paragraph_token_count
        else:
            if current_block:
                current_block += "\n\n"
            current_block += paragraph
            current_block_token_count += paragraph_token_count

    if current_block:
        blocks.append(current_block)

    # Save blocks to files
    for i, block in enumerate(blocks):
        filename = os.path.join(output_dir, f"{i+1:05d}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(block)

    print(f"✅ Text split into {len(blocks)} blocks in directory '{output_dir}'.")
