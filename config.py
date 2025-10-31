# Configuration settings
TOKENS_PER_BLOCK = 2000

# LLM provider ("gemini" or "ollama")
LLM_TOOL = "gemini"

# Models for preprocessing
GLOSSARY_CREATION_MODEL = "gemini-1.5-flash"

# Configuration for Gemini
GEMINI_EVALUATION_MODEL = "gemini-pro"

# Configuration for Ollama
OLLAMA_EVALUATION_MODEL = "mistral"

# Book context
BOOK_CONTEXT = {
    "book_title": "The Lord of the Rings",
    "author": "J.R.R. Tolkien",
    "theme_description": "An epic fantasy adventure about the struggle between good and evil.",
    "author_style": "Descriptive and formal prose with extensive world-building.",
    "target_audience": "Fans of epic fantasy and complex narratives.",
    "cultural_context": "Rooted in European mythology, especially Norse and Anglo-Saxon sagas."
}
