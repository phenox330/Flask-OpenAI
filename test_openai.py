import os
from openai import OpenAI
from dotenv import load_dotenv

# Afficher le répertoire de travail actuel
print(f"Current working directory: {os.getcwd()}")

# Charger les variables d'environnement depuis le fichier .env
load_dotenv(verbose=True)

# Récupérer la clé API et l'ID de l'assistant depuis les variables d'environnement
api_key = os.getenv('OPENAI_API_KEY')
assistant_id = os.getenv('ASSISTANT_ID')

# Afficher les valeurs des variables d'environnement (en masquant la plupart de la clé API)
if api_key:
    print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
else:
    print("API Key not found")

if assistant_id:
    print(f"Assistant ID: {assistant_id}")
else:
    print("Assistant ID not found")

# Vérifier si le fichier .env existe
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    print(f".env file found at {env_path}")
    # Lire et afficher le contenu du fichier .env (en masquant la clé API)
    with open(env_path, 'r') as f:
        env_contents = f.read()
        print("Contents of .env file:")
        for line in env_contents.split('\n'):
            if line.startswith('OPENAI_API_KEY='):
                key = line.split('=', 1)[1]
                print(f"OPENAI_API_KEY={key[:5]}...{key[-5:]}")
            else:
                print(line)
else:
    print(f".env file not found at {env_path}")

# Initialiser le client OpenAI
try:
    client = OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {str(e)}")

def test_openai_connection():
    try:
        # Tester la récupération de l'assistant
        assistant = client.beta.assistants.retrieve(assistant_id)
        print(f"Assistant récupéré avec succès. Nom: {assistant.name}")

        # Le reste du code de test...

    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")

if __name__ == "__main__":
    test_openai_connection()