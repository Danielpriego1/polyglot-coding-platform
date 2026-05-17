import json
import os
import openai

def handler(event, context):
    """
    Edge Function para el Tutor de IA.
    Centraliza las llamadas a LLMs en el servidor.
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    body = json.loads(event.get("body", "{}"))
    
    prompt = body.get("prompt", "")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un tutor de programación útil."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        advice = response.choices[0].message.content.strip()
        return {
            "statusCode": 200,
            "body": json.dumps({"advice": advice})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
