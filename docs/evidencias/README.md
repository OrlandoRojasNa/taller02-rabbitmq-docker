# Evidencias (capturas)

Lista de capturas que pide el taller. Guárdelas en esta carpeta con estos nombres:

| Archivo | Qué debe mostrar |
|---|---|
| `01-contenedores-arriba.png` | `docker compose ps` con los 3 servicios en ejecución |
| `02-cola-creada.png` | Consola → *Queues and Streams* con `cola.sensores` (D = durable) recién levantado |
| `03-postman-valido.png` | Respuesta `{"status": true, ...}` |
| `04-postman-invalido.png` | Respuesta `{"status": false, ...}` |
| `05-runner-10-mensajes.png` | Runner de Postman con 10 iteraciones exitosas |
| `06-logs-consumidor.png` | `docker compose logs consumidor` con los mensajes, su contenido y la hora |
| `07-caso1-antes.png` / `07-caso1-despues.png` | Consumidor detenido: mensajes acumulados → consumidos al reiniciarlo |
| `08-caso2-antes.png` / `08-caso2-despues.png` | Misma cantidad de mensajes antes y después de `docker compose restart rabbitmq` |
| `09-caso3-antes.png` / `09-caso3-despues.png` | Mensaje inválido: el total de la cola no cambia |
