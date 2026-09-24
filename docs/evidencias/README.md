# Evidencias (capturas)

Lista de capturas que pide el taller. Guárdelas en esta carpeta con estos nombres:

| Archivo | Qué debe mostrar | Estado |
|---|---|---|
| `01-contenedores-arriba.png` | `docker compose ps` con los 3 servicios en ejecución | ✅ |
| `02-cola-creada.png` | Consola → *Queues and Streams* con `cola.sensores` (D = durable) recién levantado | ✅ |
| `03-postman-valido.png` | Respuesta `{"status": true, ...}` | ✅ |
| `04-postman-invalido.png` | Respuesta `{"status": false, ...}` | ✅ |
| `05-runner-10-mensajes.png` | Runner de Postman con 10 iteraciones exitosas | ✅ |
| `06-logs-consumidor.png` | `docker compose logs consumidor` con los mensajes, su contenido y la hora | ✅ |
| `07-caso1-antes.png` / `07-caso1-despues.png` / `07-caso1-logs.png` | Consumidor detenido: mensajes acumulados → consumidos al reiniciarlo | ✅ |
| `08-caso2-antes.png` / `08-caso2-despues.png` | Misma cantidad de mensajes antes y después de `docker compose restart rabbitmq` | ⏳ pendiente |
| `09-caso3-antes.png` / `09-caso3-despues.png` | Mensaje inválido: el total de la cola no cambia | ⏳ pendiente |

El informe (`docs/informe/informe.html`) ya tiene el texto y los pies de figura de los casos 2 y 3 (figuras 10 a 13).
Solo falta guardar las capturas con estos nombres y regenerar el PDF.

---

## Cómo tomar las capturas pendientes

Antes de empezar:

```bash
docker compose up -d --build
docker compose ps        # los 3 servicios arriba, rabbitmq "healthy"
```

Abra la consola en http://localhost:15672 (`lab` / `lab123`) → *Queues and Streams* → `cola.sensores`.

### Caso 2: reinicio de RabbitMQ (`08-caso2-*.png`)

1. Detenga el consumidor para que los mensajes se queden en la cola:
   ```bash
   docker compose stop consumidor
   ```
2. En Postman, envíe *Enviar mensaje valido* varias veces (por ejemplo, 5 con el Runner).
3. Espere unos segundos a que la consola se actualice. **Captura `08-caso2-antes.png`**: *Ready* con los mensajes acumulados y *Consumers (0)*.
   Como respaldo, también sirve esta salida de la terminal:
   ```bash
   docker compose exec rabbitmq rabbitmqctl list_queues name durable messages_ready consumers
   ```
4. Reinicie el broker:
   ```bash
   docker compose restart rabbitmq
   ```
5. Espere unos 15 s, recargue la consola y vuelva a iniciar sesión. **Captura `08-caso2-despues.png`**: *Ready* con **la misma cantidad** que en el paso 3.
   La gráfica empieza de cero porque las estadísticas no se guardan, pero los mensajes sí.
6. Vuelva a iniciar el consumidor para vaciar la cola:
   ```bash
   docker compose start consumidor
   ```

### Caso 3: mensaje inválido (`09-caso3-*.png`)

1. Con el consumidor **detenido** (`docker compose stop consumidor`) y algunos mensajes en la cola, el total queda fijo y se ve más fácil que no cambia.
2. **Captura `09-caso3-antes.png`**: la consola con el total (*Total* / *Ready*) de `cola.sensores`.
3. En Postman, envíe *Enviar mensaje invalido (JSON mal formado)*: responde `400` con `{"status": false, "message": "Formato de mensaje inválido"}`.
4. **Captura `09-caso3-despues.png`**: la respuesta de Postman y la consola con **el mismo total** del paso 2 (puede ser una captura con ambas ventanas o dos recortes en una imagen).
5. Opcional: `docker compose logs productor` muestra `Mensaje rechazado, no se publica: JSON mal formado: …`.
6. Al terminar: `docker compose start consumidor`.

### Regenerar el PDF

Con las cuatro capturas en esta carpeta, en Windows (PowerShell):

```powershell
.\docs\informe\generar-pdf.ps1
```

Si falta alguna imagen, el PDF mostrará un recuadro vacío en esa figura.
