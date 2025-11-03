import tiktoken
import config

def split_text(text: str):
    """
    Splits the text into blocks of approximately a given token size, respecting paragraph boundaries.
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

    return blocks
