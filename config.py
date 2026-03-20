from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TWILIO_SID    = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
    GROQ_KEY      = os.getenv("GROQ_API_KEY")
    SUPABASE_URL  = os.getenv("https://tjtphhvjvdwmocpyrdyx.supabase.co")
    SUPABASE_KEY  = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqdHBoaHZqdmR3bW9jcHlyZHl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3OTkwODcsImV4cCI6MjA4OTM3NTA4N30.9LTMc3NXtq9J3TGNbTVBvS1Gp6lSaEZK-Xeyb_ZPniA")
    EMPRESA       = os.getenv("EMPRESA_NOMBRE", "la empresa")
    MAX_HISTORIAL = int(os.getenv("MAX_HISTORIAL", "20"))
    PORT          = int(os.getenv("PORT", "8000"))

config = Config()