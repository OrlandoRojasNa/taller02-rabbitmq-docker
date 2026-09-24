# Taller de Laboratorio N.º 2: mensajería con RabbitMQ en contenedores Docker

**Asignatura:** Sistemas Distribuidos · **Programa:** Ingeniería de Software · **Periodo:** 2026-2
**Docente:** Juan Carlos Polania Cortes
**Integrantes:** Derly Dayana Garcia Carrillo · Orlando Rojas Narvaez

Sistema de mensajería asíncrona **100 % dockerizado**:

| Servicio     | Qué hace                                                              | Puerto en el equipo |
|--------------|-----------------------------------------------------------------------|---------------------|
| `rabbitmq`   | Intermediario de mensajes, con la cola durable `cola.sensores` ya creada | `15672` (consola)   |
| `productor`  | API REST (Java 21 + Spring Boot) que recibe JSON y lo publica en la cola | `8080` (API)        |
| `consumidor` | Servicio (Java 21 + Spring Boot) que lee la cola y muestra cada mensaje en sus logs | (ninguno)           |

```
Postman ──POST /api/mensajes──▶ productor ──AMQP──▶ [ rabbitmq : cola.sensores ] ──AMQP──▶ consumidor ──▶ docker logs
```

---

## 1. Requisitos

Solo **Docker** (Docker Desktop en Windows/Mac, o Docker Engine + plugin Compose en Linux).
No hay que instalar Java, Maven ni RabbitMQ: todo se compila y se ejecuta dentro de las imágenes.

## 2. Levantar todo el entorno (un solo comando)

```bash
git clone https://github.com/OrlandoRojasNa/taller02-rabbitmq-docker.git
cd taller02-rabbitmq-docker
docker compose up -d --build
```

La primera vez tarda unos minutos porque descarga imágenes y dependencias Maven.
Para comprobar que los tres contenedores quedaron arriba:

```bash
docker compose ps
```

| Recurso                     | URL / dato                                                   |
|-----------------------------|--------------------------------------------------------------|
| Consola de RabbitMQ         | http://localhost:15672 · usuario `lab` · contraseña `lab123` |
| Endpoint del productor      | `POST http://localhost:8080/api/mensajes`                    |
| Cola                        | `cola.sensores` (durable, vhost `/`)                         |
| Logs del consumidor         | `docker compose logs -f consumidor`                          |

Para apagar: `docker compose down` (conserva los mensajes en el volumen).
Para borrar todo, incluidos los datos: `docker compose down -v`.

## 3. Cómo cumple cada requisito

| Requisito del taller | Implementación |
|---|---|
| Todo dockerizado | Dockerfiles multi-etapa: la etapa `maven:3.9-eclipse-temurin-21` compila y la etapa `eclipse-temurin:21-jre` ejecuta. |
| Consola accesible | Imagen `rabbitmq:4.1-management`, puerto `15672` publicado. |
| Cola durable que existe al levantar el entorno | [`rabbitmq/definitions.json`](rabbitmq/definitions.json) se carga al arrancar el nodo (`load_definitions`). Además, productor y consumidor la declaran con los mismos atributos, lo cual es idempotente. |
| Productor POST + JSON | `POST /api/mensajes`. Valida que el cuerpo sea un **objeto JSON** y publica con `deliveryMode = PERSISTENT`. Espera la confirmación del broker (*publisher confirms*) antes de responder `"Mensaje encolado"`. |
| `status` booleano | Se responde con `record Respuesta(boolean status, String message)`, así que Jackson lo serializa como `true`/`false`, no como texto. |
| Consumidor muestra contenido y hora | Log: `[#n] Mensaje recibido \| hora de recepcion: … \| id: … \| contenido: {…}` (zona horaria `America/Bogota`). |
| Retirar el mensaje solo después de procesarlo | `acknowledge-mode: manual` + `basicAck` al terminar de procesar. Si falla, `basicNack` con reencolado. `prefetch: 1`. |
| Un único archivo de composición | [`docker-compose.yml`](docker-compose.yml). |
| Servicios por nombre, no por `localhost` | Las apps se conectan a `SPRING_RABBITMQ_HOST=rabbitmq`. El puerto AMQP `5672` **no** se publica al equipo. |
| Reintentar si RabbitMQ no está listo | `depends_on: condition: service_healthy` + reintentos propios de Spring AMQP (el listener reintenta cada 5 s y el productor se conecta en cada publicación). |
| Persistencia ante reinicios | Cola durable + mensajes persistentes + volumen `rabbitmq_data` + `hostname: rabbitmq` fijo (el nombre del nodo no cambia). |

### Respuestas de la API

| Caso | HTTP | Cuerpo |
|---|---|---|
| Mensaje publicado | 200 | `{"status": true, "message": "Mensaje encolado"}` |
| Cuerpo vacío, no JSON, JSON mal formado o que no es un objeto | 400 | `{"status": false, "message": "Formato de mensaje inválido"}` |
| RabbitMQ no disponible | 503 | `{"status": false, "message": "No se pudo publicar el mensaje en la cola"}` |

Todas las respuestas llevan `Content-Type: application/json`.

## 4. Pruebas con Postman

1. Importe [`postman/Taller02-RabbitMQ.postman_collection.json`](postman/Taller02-RabbitMQ.postman_collection.json).
2. Peticiones incluidas:
   - **Enviar mensaje valido**: incluye tests que verifican `status === true` (boolean).
   - **Enviar mensaje invalido (JSON mal formado)** y **(texto plano)**: verifican `status === false`.
   - **Estado de la cola**: consulta la API de administración de RabbitMQ (mensajes listos, sin ACK, consumidores).
3. **10 mensajes válidos:** *Runner* → marque solo *Enviar mensaje valido* → *Iterations* = `10` → *Run*.
   Luego verifique en la consola (*Queues and Streams → cola.sensores*) y en `docker compose logs consumidor` que llegaron los 10.

## 5. Casos a comprobar (punto 7 del taller)

> Tome capturas **antes y después** en la consola: *Queues and Streams → cola.sensores* (columnas *Ready*, *Unacked*, *Total* y la gráfica de *Queued messages*).
> Guárdelas en [`docs/evidencias/`](docs/evidencias/). Allí está la lista de capturas, cuáles faltan y el paso a paso para tomarlas.

### Caso 1: consumidor detenido

```bash
docker compose stop consumidor
```
Envíe varios mensajes válidos desde Postman. En la consola, *Ready* aumenta y *Consumers* = 0.
```bash
docker compose start consumidor
docker compose logs -f consumidor
```
El consumidor procesa todos los mensajes acumulados y *Ready* vuelve a 0.

### Caso 2: reinicio de RabbitMQ con mensajes pendientes

```bash
docker compose stop consumidor
```
Envíe varios mensajes y anote la cantidad en *Ready*.
```bash
docker compose restart rabbitmq
```
Espere unos segundos, recargue la consola (vuelva a iniciar sesión) y verifique que la cola tiene **la misma cantidad** de mensajes. Luego:
```bash
docker compose start consumidor
```
Para una prueba aún más fuerte, puede recrear el contenedor: `docker compose rm -sf rabbitmq && docker compose up -d rabbitmq`. Los mensajes siguen ahí gracias al volumen.

### Caso 3: mensaje inválido

Anote el total de la cola, envíe *Enviar mensaje invalido* desde Postman y verifique:
- la respuesta es `{"status": false, "message": "Formato de mensaje inválido"}`;
- el total de la cola **no cambia**;
- en `docker compose logs productor` aparece `Mensaje rechazado, no se publica: …`.

## 6. Comandos útiles

```bash
docker compose logs -f productor          # logs del productor
docker compose logs -f consumidor         # mensajes recibidos
docker compose exec rabbitmq rabbitmqctl list_queues name durable messages_ready messages_unacknowledged consumers
```

Ejemplo con `curl`:

```bash
curl -i -X POST http://localhost:8080/api/mensajes -H "Content-Type: application/json" -d '{"sensor": "OD-01", "valor": 4.2, "unidad": "mg/L"}'
```

## 7. Estructura del proyecto

```
taller02-rabbitmq-docker/
├── docker-compose.yml          # levanta los 3 servicios
├── rabbitmq/                   # imagen del broker + definiciones (cola durable)
├── productor/                  # API Spring Boot (Dockerfile + código + tests)
├── consumidor/                 # listener Spring Boot (Dockerfile + código)
├── postman/                    # colección exportada
├── docs/
│   ├── DECLARACION_IA.md       # declaración de uso de IA (obligatoria)
│   └── evidencias/             # capturas de pantalla
└── pom.xml                     # agregador, solo para abrir todo en IntelliJ
```

## 8. Abrir en IntelliJ IDEA

*File → Open* → seleccione la carpeta raíz (el `pom.xml` agregador carga `productor` y `consumidor` como módulos).
IntelliJ se usa solo como **editor**. La ejecución es siempre con `docker compose up -d --build`.

## 9. Declaración de uso de IA

Ver [`docs/DECLARACION_IA.md`](docs/DECLARACION_IA.md).
