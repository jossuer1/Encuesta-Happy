import os, secrets, time, sys
import pandas as pd
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
BASE = os.environ["FRONTEND_URL"].rstrip("/")
VERDE = "#0a7a4f"

IMG_HEADER = f"{BASE}/img/header.jpeg"
IMG_FOOTER = f"{BASE}/img/footer.jpeg"


def botones(token, q, valores):
    links = ""
    for v in valores:
        url = f"{BASE}/?t={token}&q={q}&v={v}"
        links += (
            f'<a href="{url}" style="display:inline-block;margin:3px;min-width:38px;'
            f'padding:9px 0;text-align:center;border:2px solid {VERDE};border-radius:20px;'
            f'color:{VERDE};background:#ffffff;font-weight:bold;text-decoration:none;'
            f'font-family:Arial,sans-serif">{v}</a>'
        )
    return f'<div style="margin-top:14px">{links}</div>'


def tarjeta(n, texto, escala, token, valores, margen=""):
    return f"""
  <div style="background:#eef7f2;padding:20px;border-radius:12px;{margen}">
    <table role="presentation" width="100%"><tr>
      <td width="44" valign="top">
        <span style="display:inline-block;width:34px;height:34px;line-height:34px;border-radius:50%;
        background:{VERDE};color:#fff;font-weight:bold;text-align:center;font-family:Arial,sans-serif">{n}</span>
      </td>
      <td valign="top" style="font-family:Arial,sans-serif;font-size:16px;font-weight:bold;color:#0a4a33">{texto}</td>
    </tr></table>
    <p style="color:#666;font-size:13px;margin:10px 0 0;font-family:Arial,sans-serif">{escala}</p>
    {botones(token, n, valores)}
  </div>"""


def html_correo(token):
    p1 = tarjeta(
        1,
        "En una escala del 1 al 5, ¿qué tan satisfecho/a estás con el servicio de garantía y reparación de pantalla de Happy?",
        "1 = Muy insatisfecho/a | 5 = Muy satisfecho/a",
        token, range(1, 6), "margin-bottom:16px;",
    )
    p2 = tarjeta(
        2,
        "Del 0 al 10, ¿qué tan probable es que recomiendes comprar un celular con Happy a un familiar o amigo?",
        "0 = Nada probable | 10 = Totalmente probable",
        token, range(0, 11),
    )
    return f"""
<div style="max-width:600px;margin:auto;font-family:Arial,sans-serif;color:#1a1a1a">
  <img src="{IMG_HEADER}" alt="Happy - Tu opinión nos ayuda a mejorar" width="600"
       style="display:block;width:100%;max-width:600px;height:auto;border:0;border-radius:12px 12px 0 0">
  <div style="padding:20px 8px">
    <p style="margin:0 0 12px">Estimado/a cliente,</p>
    <p style="margin:0 0 20px">Nos ayudaría mucho si puedes responder estas 2 preguntas.</p>
    {p1}
    {p2}
    <p style="text-align:center;color:{VERDE};margin:28px 0 20px"><b>¡Gracias por ayudarnos a mejorar!</b></p>
  </div>
  <img src="{IMG_FOOTER}" alt="Gracias por compartir tu opinión - Happy" width="600"
       style="display:block;width:100%;max-width:600px;height:auto;border:0;border-radius:0 0 12px 12px">
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