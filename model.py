import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

#calling the model
def chat(system,conversation, model):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "system", "content": system}] + conversation,
        model=model,  
        temperature=0,
        max_tokens=8000,
        top_p=1,
    )
    return chat_completion.choices[0].message.content