from fastapi import FastAPI,Form, Request
from fastapi.responses import Response,PlainTextResponse
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import uvicorn

from config import config
from database import get_history, save_messages, is_human_mode, set_human_mode
from ai_engine import get_ai_response

app = FastAPI(title="WhatsApp AI Bot")
twilio_client = Client(config.TWILIO_SID, config.TWILIO_TOKEN)


def send_whatsapp(to: str, body:str):
    """Envia un mensaje de WhatsApp via Twilio"""
    twilio_client.messages.create(
        body=body,
        from_="whatsapp:" + config.TWILIO_NUMBER,
        to=to #ya viene como "whatsapp:+57..."
    )


@app.get("/health")
def health_check():
    """Endpoint de verificacion-Railway lo usa para saber si el bot vive"""
    return {"status": "ok", "bot": config.EMPRESA}
@app.post("/webhook")
async def webhook(
    From: str = Form(...), 
    Body: str = Form(...),
    ) -> PlainTextResponse:
    
    """
    Endpoint principal.Twilio envia aqui cada mesaje entrante.
    From: numero del usuario (ej:whatsapp:+573001234567)
    Body:texto del mensaje
    """
    phone = From #ej: whatssap: +573102897401
    text = Body.strip()
    print(f"[MENSAJE] {phone}: {text}")
    # Modo atencion Humana
    #Si el usuario esta siendo atendido por un humano ,no responder
    if is_human_mode(phone):
        print("f[HUMANO] {phone} en modohumano ignorando")
        return PlainTextResponse("", status_code=200)
    #Activar modo humano si el usuario lo pide
    triggers_words = ["humano", "asesor", "persona", "agente"]
    if any(w in text.lower() for w in triggers_words):
        set_human_mode(phone, True)
        reply = "Un asesor humano se comunicara contigo pronto. Horario: Lun-Vie 8am-6pm."
        send_whatsapp(phone, reply)
        save_messages(phone, text, reply)
        return PlainTextResponse("", status_code=200)
 #Respuesta normal IA
    try:
#Obtener Historial de Supabase
        history = get_history(phone)
#Generear respuesta con GPT-40
        reply = get_ai_response(phone, text, history)
#Verificar si la IA quiere transferir a humano
        if "TRANSFERIR_HUMANO" in reply:
            set_human_mode(phone, True)
            reply = "No tengo esa informacion disponible en este momento. Un asesor te contactara pronto."
        #Guardar en Supabase
        save_messages(phone, text, reply)
        #Enviar respuesta por whatsapp
        send_whatsapp(phone, reply)
        print(f"[RESPUESTA] {phone}: {reply[ :80]}...")
    except Exception as e:
        print(f"[ERROR] {phone}: {e}")
        send_whatsapp(phone, "Tuve un problema tecnico. Intenta en unos minutos.")
        return PlainTextResponse("",status_code=200)
    if __name__ == "__main__":
        uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)