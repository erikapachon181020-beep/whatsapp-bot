from groq import Groq
from config import config
from prompts import get_system_prompt

client = Groq(api_key=config.GROQ_KEY)

def get_ai_response(phone: str, user_message: str, history: list) -> str:
    
    # 1. System prompt
    messages = [{
        "role": "system",
        "content": get_system_prompt(config.EMPRESA)
    }]

    # 2. Historial previo (memoria del bot)
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # 3. Mensaje actual del usuario
    messages.append({
        "role": "user",
        "content": user_message
    })

    # 4. Llamar a Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=600,
        temperature=0.7,
    )

    return response.choices[0].message.content