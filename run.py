from app import create_app
from dotenv import load_dotenv
load_dotenv() 
def run_assistant(self, message):
    # ... autre code ...
    run = self.openAI.beta.threads.runs.create(
        thread_id=self.thread.id,
        assistant_id=self.assistant_id,  # Utilisez l'ID de l'assistant ici
    )
    # ... reste du code ...
if __name__ == '__main__':
    app = create_app()
    app.run()