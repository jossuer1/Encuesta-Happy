def html_correo(token):
    return f"""
<div style="max-width:600px;margin:auto;font-family:Arial,sans-serif;color:#1a1a1a">
  <div style="background:{VERDE};color:#fff;padding:28px;border-radius:12px">
    <h1 style="margin:0 0 8px">Tu opinión <i style="color:#8be28b">nos importa</i></h1>
    <p style="margin:0">En Happy queremos conocer tu experiencia y seguir mejorando nuestro servicio.</p>
  </div>
  <p>Estimado/a cliente,</p>
  <p>Nos ayudaría mucho si puedes responder estas 2 preguntas.</p>

  <div style="background:#eef7f2;padding:18px;border-radius:12px;margin-bottom:14px">
    <p><b>1.</b> En una escala del 1 al 5, ¿qué tan satisfecho/a estás con el servicio de garantía y reparación de pantalla de Happy?</p>
    <p style="color:#666;font-size:13px">1 = Muy insatisfecho/a | 5 = Muy satisfecho/a</p>
    {botones(token, 1, range(1, 6))}
  </div>

  <div style="background:#eef7f2;padding:18px;border-radius:12px">
    <p><b>2.</b> Del 0 al 10, ¿qué tan probable es que recomiendes comprar un celular con Happy a un familiar o amigo?</p>
    <p style="color:#666;font-size:13px">0 = Nada probable | 10 = Totalmente probable</p>
    {botones(token, 2, range(0, 11))}
  </div>

  <p style="text-align:center;color:{VERDE};margin-top:24px"><b>¡Gracias por ayudarnos a mejorar!</b><br>Happy</p>
</div>"""