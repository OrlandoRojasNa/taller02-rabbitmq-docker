"""Genera un documento HTML por cada entregable del taller (seccion 9 del enunciado).

Uso:  python docs/entregables/generar.py
Luego cada HTML se imprime a PDF con Chrome/Edge (ver generar-pdf.ps1 en esta carpeta).
El contenido de codigo, Dockerfiles y coleccion se lee de los archivos del repositorio,
asi que los documentos siempre coinciden con lo entregado.
"""
import html
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "html"
EVID = "../../evidencias"

CSS = (RAIZ / "docs/informe/informe.html").read_text(encoding="utf-8")
CSS = re.search(r"<style>(.*?)</style>", CSS, re.S).group(1) + """
  .cab { border-bottom: 3px solid var(--verde); padding-bottom: 8px; margin-bottom: 6px; }
  .cab .inst { font-size: 9pt; color: var(--gris); }
  .cab h1 { font-size: 18pt; margin: 6px 0 2px; }
  .cab .meta { font-size: 9pt; color: var(--gris); }
  .archivo { font-family: Consolas, monospace; font-size: 9pt; font-weight: 600; background: var(--fondo); border: 1px solid var(--borde); border-bottom: 0; padding: 3px 8px; margin-top: 12px; break-after: avoid; }
  pre.codigo { margin-top: 0; border-radius: 0 0 4px 4px; break-inside: auto; font-size: 8.3pt; }
"""

AVISO_JS = """<script>
  document.querySelectorAll('.marco img').forEach(function (img) {
    function avisar() {
      var aviso = document.createElement('div');
      aviso.className = 'pendiente';
      aviso.textContent = 'Captura no incluida en esta entrega: ' + img.getAttribute('src').split('/').pop();
      img.parentNode.replaceWith(aviso);
    }
    if (img.complete && img.naturalWidth === 0) { avisar(); } else { img.addEventListener('error', avisar); }
  });
</script>"""


def e(texto):
    return html.escape(texto, quote=False)


def leer(ruta):
    return (RAIZ / ruta).read_text(encoding="utf-8")


def archivo(ruta, titulo=None):
    return f'<div class="archivo">{e(titulo or ruta)}</div><pre class="codigo">{e(leer(ruta).rstrip())}</pre>'


def figura(img, texto, clase=""):
    c = f' class="{clase}"' if clase else ""
    return f'<figure><div class="marco"><img{c} src="{EVID}/{img}"></div><figcaption>{texto}</figcaption></figure>'


def documento(nombre, numero, titulo, cuerpo):
    pagina = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>{e(titulo)}</title><style>{CSS}</style></head>
<body>
<div class="cab">
  <div class="inst">FUNDACIÓN ESCUELA TECNOLÓGICA DE NEIVA "JESÚS OVIEDO PÉREZ" · Sistemas Distribuidos · Taller de Laboratorio N.º 2</div>
  <h1>Entregable {numero}. {e(titulo)}</h1>
  <div class="meta">Integrantes: Derly Dayana Garcia Carrillo · Orlando Rojas Narvaez &nbsp;|&nbsp; Docente: Juan Carlos Polania Cortes &nbsp;|&nbsp; Periodo 2026-2 &nbsp;|&nbsp; Repositorio: github.com/OrlandoRojasNa/taller02-rabbitmq-docker</div>
</div>
{cuerpo}
{AVISO_JS}
</body></html>"""
    (SALIDA / f"{nombre}.html").write_text(pagina, encoding="utf-8")


def md_a_html(md):
    """Conversor minimo para el README (titulos, tablas, listas, bloques de codigo, citas)."""
    out, lineas, i = [], md.splitlines(), 0

    def inline(t):
        t = e(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", t)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", t)
        return t

    while i < len(lineas):
        l = lineas[i]
        if l.startswith("```"):
            bloque = []
            i += 1
            while not lineas[i].startswith("```"):
                bloque.append(lineas[i]); i += 1
            out.append(f"<pre>{e(chr(10).join(bloque))}</pre>")
        elif l.startswith("# "):
            pass  # el titulo va en la cabecera
        elif l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("### "):
            out.append(f"<h3>{inline(l[4:])}</h3>")
        elif l.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in celdas):
                    filas.append(celdas)
                i += 1
            i -= 1
            t = "<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in filas[0]) + "</tr>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in f) + "</tr>" for f in filas[1:])
            out.append(t + "</table>")
        elif re.match(r"\s*(-|\d+\.) ", l):
            items = []
            while i < len(lineas) and re.match(r"\s*(-|\d+\.) ", lineas[i]):
                items.append(re.sub(r"\s*(-|\d+\.) ", "", lineas[i], count=1)); i += 1
            i -= 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
        elif l.startswith(">"):
            out.append(f'<div class="nota">{inline(l.lstrip("> "))}</div>')
        elif l.strip() and l.strip() != "---":
            out.append(f"<p>{inline(l)}</p>")
        i += 1
    return "\n".join(out)


# ---------------------------------------------------------------- 1. Codigo fuente
def codigo_fuente():
    prod = sorted((RAIZ / "productor/src").rglob("*.java")) + [RAIZ / "productor/src/main/resources/application.yml"]
    cons = sorted((RAIZ / "consumidor/src").rglob("*.java")) + [RAIZ / "consumidor/src/main/resources/application.yml"]
    rel = lambda p: p.relative_to(RAIZ).as_posix()
    cuerpo = """
<h2>Resumen</h2>
<p>Ambos servicios están escritos en <b>Java 21 con Spring Boot 3.5</b> y usan <b>Spring AMQP</b> para hablar con RabbitMQ. Cada uno se compila dentro de su propia imagen Docker.</p>
<table>
  <tr><th>Servicio</th><th>Clase</th><th>Responsabilidad</th></tr>
  <tr><td rowspan="5">productor</td><td><code>MensajeController</code></td><td>Expone <code>POST /api/mensajes</code> y responde <code>{"status": true, "message": "Mensaje encolado"}</code>.</td></tr>
  <tr><td><code>PublicadorService</code></td><td>Valida que el cuerpo sea un objeto JSON, lo publica como mensaje <b>persistente</b> y espera la confirmación del broker.</td></tr>
  <tr><td><code>ManejadorErrores</code></td><td>Convierte los errores en <code>400</code> (mensaje inválido) o <code>503</code> (RabbitMQ no disponible) con <code>status: false</code>.</td></tr>
  <tr><td><code>Respuesta</code></td><td><code>record Respuesta(boolean status, String message)</code>: garantiza que <code>status</code> sea booleano.</td></tr>
  <tr><td><code>RabbitConfig</code></td><td>Declara la cola durable <code>cola.sensores</code> (idempotente).</td></tr>
  <tr><td rowspan="2">consumidor</td><td><code>MensajeListener</code></td><td>Lee la cola, registra en el log el contenido y la hora de recepción, y confirma con <code>basicAck</code> solo después de procesar.</td></tr>
  <tr><td><code>RabbitConfig</code></td><td>Declara la misma cola durable.</td></tr>
</table>
<p>El productor incluye pruebas unitarias (<code>MensajeControllerTest</code>) que verifican el mensaje válido, los inválidos y el caso de broker caído.</p>
<h2 class="salto">Productor</h2>
""" + "".join(archivo(rel(p)) for p in prod) + """
<h2 class="salto">Consumidor</h2>
""" + "".join(archivo(rel(p)) for p in cons)
    documento("01-codigo-fuente", 1, "Código fuente del productor y del consumidor", cuerpo)


# ---------------------------------------------------------------- 2. Docker
def docker():
    cuerpo = """
<h2>Resumen</h2>
<table>
  <tr><th>Archivo</th><th>Qué hace</th></tr>
  <tr><td><code>docker-compose.yml</code></td><td>Único archivo de composición: levanta <code>rabbitmq</code>, <code>productor</code> y <code>consumidor</code> con <code>docker compose up -d --build</code>. Solo publica los puertos 15672 (consola) y 8080 (API). Los servicios se conectan por nombre (<code>rabbitmq</code>), esperan a que el broker esté <i>healthy</i> y el volumen <code>rabbitmq_data</code> conserva los mensajes.</td></tr>
  <tr><td><code>rabbitmq/Dockerfile</code></td><td>Parte de <code>rabbitmq:4.1-management</code> y copia la configuración y las definiciones.</td></tr>
  <tr><td><code>rabbitmq/rabbitmq.conf</code> y <code>definitions.json</code></td><td>Crean el usuario <code>lab</code> y la cola durable <code>cola.sensores</code> al arrancar, sin pasos manuales.</td></tr>
  <tr><td><code>productor/Dockerfile</code>, <code>consumidor/Dockerfile</code></td><td>Multi-etapa: <code>maven:3.9-eclipse-temurin-21</code> compila y <code>eclipse-temurin:21-jre</code> ejecuta. En el equipo no se instala Java ni Maven.</td></tr>
</table>
<h2>Archivo de composición</h2>
""" + archivo("docker-compose.yml") + """
<h2 class="salto">Imagen de RabbitMQ</h2>
""" + archivo("rabbitmq/Dockerfile") + archivo("rabbitmq/rabbitmq.conf") + archivo("rabbitmq/definitions.json") + """
<h2>Imagen del productor</h2>
""" + archivo("productor/Dockerfile") + """
<h2>Imagen del consumidor</h2>
""" + archivo("consumidor/Dockerfile")
    documento("02-dockerfiles-y-compose", 2, "Dockerfiles y archivo Docker Compose", cuerpo)


# ---------------------------------------------------------------- 3. Instructivo
def instructivo():
    documento("03-instructivo", 3, "Instructivo para levantar el entorno desde cero", md_a_html(leer("README.md")))


# ---------------------------------------------------------------- 4. Postman
def postman():
    col = json.loads(leer("postman/Taller02-RabbitMQ.postman_collection.json"))
    variables = "".join(f"<tr><td><code>{e(v['key'])}</code></td><td><code>{e(v['value'])}</code></td></tr>" for v in col.get("variable", []))
    peticiones = ""
    for it in col["item"]:
        req = it["request"]
        url = req["url"] if isinstance(req["url"], str) else req["url"].get("raw", "")
        cuerpo = req.get("body", {}).get("raw")
        tests = "\n".join(l for ev in it.get("event", []) for l in ev["script"]["exec"])
        peticiones += f"<h3>{e(it['name'])}</h3><p><code>{e(req['method'])} {e(url)}</code></p>"
        if cuerpo:
            peticiones += f"<p>Cuerpo:</p><pre>{e(cuerpo)}</pre>"
        if tests:
            peticiones += f"<p>Tests:</p><pre>{e(tests)}</pre>"
    cuerpo = f"""
<h2>Resumen</h2>
<p>Archivo exportado: <code>postman/Taller02-RabbitMQ.postman_collection.json</code> (formato Postman Collection v2.1). Para usarla: Postman → <i>Import</i> → seleccionar el archivo.</p>
<table><tr><th>Variable</th><th>Valor</th></tr>{variables}</table>
<div class="nota"><b>10 mensajes válidos:</b> <i>Runner</i> → marcar solo <i>Enviar mensaje valido</i> → <i>Iterations</i> = 10 → <i>Run</i>. Resultado obtenido: 40/40 tests aprobados (figura 3 de este documento).</div>
<h2>Peticiones</h2>
{peticiones}
<h2 class="salto">Ejecución</h2>
{figura("03-postman-valido.png", "<b>Figura 1.</b> Mensaje válido: <code>200 OK</code>, <code>{&quot;status&quot;: true, &quot;message&quot;: &quot;Mensaje encolado&quot;}</code>. Tests 4/4.")}
{figura("04-postman-invalido.png", "<b>Figura 2.</b> Mensaje inválido (JSON mal formado): <code>400 Bad Request</code>, <code>{&quot;status&quot;: false, &quot;message&quot;: &quot;Formato de mensaje inválido&quot;}</code>. Tests 4/4.")}
{figura("05-runner-10-mensajes.png", "<b>Figura 3.</b> Collection Runner: 10 iteraciones de «Enviar mensaje valido». <b>40/40 tests aprobados, 0 errores</b>.")}
<h2 class="salto">Colección exportada (JSON)</h2>
{archivo("postman/Taller02-RabbitMQ.postman_collection.json")}
"""
    documento("04-coleccion-postman", 4, "Colección de Postman exportada", cuerpo)


# ---------------------------------------------------------------- 5. Consola
def consola():
    cuerpo = f"""
<p>Consola de administración de RabbitMQ en <code>http://localhost:15672</code> (usuario <code>lab</code>, contraseña <code>lab123</code>), sección <i>Queues and Streams</i>.</p>
<h2>Cola creada al levantar el entorno</h2>
{figura("01-contenedores-arriba.png", "<b>Figura 1.</b> <code>docker compose ps</code>: los tres contenedores en ejecución, <code>rabbitmq</code> en estado <i>healthy</i>.")}
{figura("02-cola-creada.png", "<b>Figura 2.</b> Recién levantado el entorno, la cola <code>cola.sensores</code> ya existe, marcada con <b>D</b> (durable), sin haberla creado a mano.")}
<h2 class="salto">Cola con mensajes acumulados</h2>
{figura("07-caso1-antes.png", "<b>Figura 3.</b> Con el consumidor detenido se acumulan los mensajes: <b>Ready = 5</b>, <b>Consumers (0)</b>. La cola es <code>durable: true</code> y los 5 mensajes son <b>Persistent</b>.", "recorte-antes")}
{figura("07-caso1-despues.png", "<b>Figura 4.</b> Al levantar el consumidor la gráfica baja de 5 a 0: <b>Consumers (1)</b> con <b>Ack required</b> (ACK manual) y <b>Prefetch count 1</b>.", "recorte-despues")}
"""
    documento("05-capturas-consola", 5, "Capturas de la consola de administración", cuerpo)


# ---------------------------------------------------------------- 6. Logs consumidor
def logs():
    cuerpo = f"""
<p>Comando: <code>docker compose logs -f consumidor</code>. Cada línea muestra el número de mensaje, la <b>hora de recepción</b> (zona <code>America/Bogota</code>), el id, si fue reentregado y el <b>contenido</b> JSON:</p>
<pre>[#n] Mensaje recibido | hora de recepcion: yyyy-MM-dd HH:mm:ss.SSS -05:00 | id: … | reentregado: false | contenido: {{…}}</pre>
{figura("06-logs-consumidor.png", "<b>Figura 1.</b> Los 10 mensajes del Runner de Postman (<code>[#2]</code> a <code>[#11]</code>, 18:21:01–18:21:02) con su contenido y hora de recepción. <code>[#1]</code> corresponde a mensajes de prueba previos.")}
{figura("07-caso1-logs.png", "<b>Figura 2.</b> Los 5 mensajes acumulados con el consumidor detenido, recibidos a las 18:34:08 apenas se levantó el consumidor.")}
"""
    documento("06-capturas-logs-consumidor", 6, "Capturas del registro del consumidor", cuerpo)


# ---------------------------------------------------------------- 7. Casos punto 7
def casos():
    informe = leer("docs/informe/informe.html")
    seccion = re.search(r'<h2 class="salto">5\. Casos del punto 7</h2>(.*?)<!-- =+ 6\.', informe, re.S).group(1)
    seccion = seccion.replace('src="../evidencias/', f'src="{EVID}/')
    documento("07-evidencias-casos-punto-7", 7, "Evidencias de los tres casos del punto 7", seccion)


# ---------------------------------------------------------------- 8. Declaracion IA
def declaracion():
    md = leer("docs/DECLARACION_IA.md")
    documento("08-declaracion-uso-ia", 8, "Declaración de uso de herramientas de inteligencia artificial", md_a_html(md))


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    for f in (codigo_fuente, docker, instructivo, postman, consola, logs, casos, declaracion):
        f()
    print("HTML generados en", SALIDA)
