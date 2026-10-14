import os, secrets, time, sys
import pandas as pd
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
BASE = os.environ["FRONTEND_URL"].rstrip("/")
VERDE = "#0a7a4f"


def boton(token):
    url = f"{BASE}/?t={token}"
    return (
        f'<p style="text-align:center;margin:28px 0">'
        f'<a href="{url}" style="display:inline-block;background:{VERDE};color:#fff;'
        f'padding:14px 36px;border-radius:28px;font-weight:bold;font-size:16px;'
        f'text-decoration:none;font-family:Arial,sans-serif">Responder encuesta</a></p>'
    )


def html_correo(token):
    return f"""
<div style="max-width:600px;margin:auto;font-family:Arial,sans-serif;color:#1a1a1a">
  <div style="background:{VERDE};color:#fff;padding:28px;border-radius:12px">
    <h1 style="margin:0 0 8px">Tu opinión <i style="color:#8be28b">nos importa</i></h1>
    <p style="margin:0">En Happy queremos conocer tu experiencia y seguir mejorando nuestro servicio.</p>
  </div>
  <p>Estimado/a cliente,</p>
  <p>Nos ayudaría mucho si puedes responder 2 preguntas rápidas sobre tu experiencia con nuestro servicio de garantía y reparación de pantalla. Te tomará menos de un minuto.</p>
  {boton(token)}
  <p style="text-align:center;color:{VERDE};margin-top:24px"><b>¡Gracias por ayudarnos a mejorar!</b><br>Happy</p>
</div>"""

def enviar(email, token):
    r = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": os.environ["BREVO_API_KEY"], "content-type": "application/json"},
        json={
            "sender": {"name": os.environ["SENDER_NAME"], "email": os.environ["SENDER_EMAIL"]},
            "to": [{"email": email}],
            "subject": "Tu opinión nos importa - Happy",
            "htmlContent": html_correo(token),
        },
        timeout=30,
    )
    if r.status_code >= 300:
        raise Exception(f"{r.status_code} {r.text}")


def main(ruta_excel):
    df = pd.read_excel(ruta_excel, header=None)
    correos = (
        df.iloc[:, 0].dropna().astype(str).str.strip().str.lower().drop_duplicates().tolist()
    )
    correos = [c for c in correos if "@" in c]  # descarta encabezados o basura

    ya = {r["email"] for r in sb.table("encuesta_garantia").select("email").execute().data}
    pendientes = [c for c in correos if c not in ya]
    print(f"{len(correos)} correos, {len(pendientes)} por enviar")

    for email in pendientes:
        token = secrets.token_urlsafe(16)
        sb.table("encuesta_garantia").insert({"email": email, "token": token}).execute()
        try:
            enviar(email, token)
            print("OK  ", email)
        except Exception as e:
            # si falla, borra el registro para poder reintentar
            sb.table("encuesta_garantia").delete().eq("token", token).execute()
            print("FAIL", email, e)
        time.sleep(0.2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "correos.xlsx")