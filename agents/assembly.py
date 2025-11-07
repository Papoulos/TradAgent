import os

def assemble_text(directory_path: str) -> str:
    """
    Assembles text from files in a directory into a single string.
    Files are sorted numerically based on their filenames.
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"The path {directory_path} is not a valid directory.")

    # Get a sorted list of file paths
    files = sorted([f for f in os.listdir(directory_path) if f.endswith('.txt')])

    assembled_content = []
    for filename in files:
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            assembled_content.append(f.read())

    return "\n\n".join(assembled_content)
