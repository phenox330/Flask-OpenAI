import os

class Config:
    FLASK_DEBUG = os.getenv("FLASK_DEBUG")
    OPENAI_KEY = os.getenv('OPENAI_KEY')
    ASSISTANT_ID = os.getenv('ASSISTANT_ID')  # Ajoutez cette ligne