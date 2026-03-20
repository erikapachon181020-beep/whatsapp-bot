from fastapi import FastAPI,Form, Request
from fastapi.responses import Response,PlainTextResponse
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import uvicorn

from config import config
from database import get_history, save_messages, is_human_mode, set_human_mode
from ai_engine import get_ai_response
from sheets import registrar_pedido

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
async def webhook(From: str = Form(...), Body: str = Form(...)):
    phone = From
    text = Body.strip()
    print("[MSG] " + phone + ": " + text)

    # Comando vendedor: reactivar bot para un cliente
    if text.startswith("/bot-on"):
        partes = text.split(" ")
        if len(partes) == 2:
            numero = partes[1].strip()
            if not numero.startswith("whatsapp:"):
                numero = "whatsapp:" + numero
            set_human_mode(numero, False)
            reply = "Bot reactivado para " + numero
            send_whatsapp(phone, reply)
            return PlainTextResponse("", status_code=200)

    # Comando vendedor: desactivar bot para un cliente
    if text.startswith("/bot-off"):
        partes = text.split(" ")
        if len(partes) == 2:
            numero = partes[1].strip()
            if not numero.startswith("whatsapp:"):
                numero = "whatsapp:" + numero
            set_human_mode(numero, True)
            reply = "Bot desactivado para " + numero
            send_whatsapp(phone, reply)
            return PlainTextResponse("", status_code=200)

    if is_human_mode(phone):
        print("[HUMANO] " + phone + " bot desactivado")
        return PlainTextResponse("", status_code=200)

    triggers = ["humano", "asesor", "persona", "agente"]
    if any(w in text.lower() for w in triggers):
        set_human_mode(phone, True)
        reply = "Un asesor humano se comunicara contigo pronto. Horario: Lun-Sab 9am-7pm."
        send_whatsapp(phone, reply)
        save_messages(phone, text, reply)
        return PlainTextResponse("", status_code=200)

    try:
        history = get_history(phone)
        reply = await get_ai_response(phone, text, history)

        if "TRANSFERIR_HUMANO" in reply:
            set_human_mode(phone, True)
            reply = "No tengo esa informacion. Un asesor te contactara pronto."

        elif "PEDIDO_CONFIRMAR" in reply:
            linea = ""
            for l in reply.split("\n"):
                if "PEDIDO_CONFIRMAR" in l:
                    linea = l.strip()
                    break
            print("[PEDIDO LINEA] " + linea)
            partes = linea.split("|")
            print("[PEDIDO PARTES] " + str(partes))
            exito = False
            try:
                nombre     = partes[1].strip()
                referencia = partes[2].strip()
                producto   = partes[3].strip()
                talla      = partes[4].strip()
                color      = partes[5].strip()
                cantidad   = int(partes[6].strip())
                precio_raw = partes[7].strip().replace("$","").replace(".","").replace(",","")
                precio     = int(precio_raw)
                total      = cantidad * precio
                ok = await registrar_pedido(phone, nombre, referencia, producto, talla, color, cantidad, precio)
                if ok:
                    reply = ("Pedido registrado exitosamente.\n"
                             "Producto: " + producto + "\n"
                             "Talla: " + talla + " | Color: " + color + "\n"
                             "Cantidad: " + str(cantidad) + "\n"
                             "Total: $" + "{:,}".format(total).replace(",", ".") + "\n\n"
                             "Un asesor te confirmara el pedido pronto.")
                    exito = True
            except Exception as ep:
                print("[ERROR PARSE] " + str(ep))
            if not exito:
                reply = "Hubo un problema procesando tu pedido. Un asesor te ayudara."

        save_messages(phone, text, reply)
        send_whatsapp(phone, reply)
        print("[OK] Respuesta enviada a " + phone)

    except Exception as e:
        print("[ERROR] " + str(e))
        send_whatsapp(phone, "Tuve un problema tecnico. Intenta en unos minutos.")

    return PlainTextResponse("", status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)