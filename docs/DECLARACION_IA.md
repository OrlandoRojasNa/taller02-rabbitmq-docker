# Declaración de uso de herramientas de inteligencia artificial

**Integrantes:** Derly Dayana Garcia Carrillo · Orlando Rojas Narvaez

## Herramienta utilizada

**Claude Code** (Anthropic), modelo Claude Opus 5.5, usado desde la aplicación de escritorio de Claude.

## Finalidad

- Leer el enunciado del taller (PDF), extraer los requisitos y revisar que el documento no tuviera texto oculto.
- Generar el proyecto completo: `docker-compose.yml`, Dockerfiles, configuración y definiciones de RabbitMQ (cola durable), el código del productor y del consumidor (Java 21 + Spring Boot) y las pruebas unitarias del productor.
- Generar la colección de Postman y el instructivo (`README.md`).
- Crear el repositorio en GitHub, hacer los commits y agregar a la integrante como colaboradora.
- Guiar paso a paso la ejecución de las pruebas y la toma de capturas, y armar el informe en PDF.
- Diagnosticar dos problemas durante la ejecución: una caída momentánea de red al descargar las imágenes de Docker Hub y Docker Desktop, que no se inició después de reiniciar el equipo.
- Redactar la documentación de los casos 2 y 3 del punto 7 (procedimiento, explicación y pies de figura en el informe, y la guía de capturas en `docs/evidencias/README.md`). Antes de redactarla, la herramienta ejecutó ambos casos en un entorno de pruebas propio para comprobar el comportamiento. Las capturas de evidencia las tomaron los integrantes en su equipo; las de los casos 2 y 3 no se incluyen en esta entrega.
- Regenerar el informe en PDF, generar un documento PDF por cada entregable (`docs/entregables/`) y armar el archivo comprimido de entrega.

## Qué se modificó del resultado

**No se modificó el código generado por la herramienta.** El trabajo de los integrantes sobre el resultado fue:

- Instalar Docker Desktop y levantar el entorno completo con `docker compose up -d --build`.
- Importar la colección en Postman y ejecutar las peticiones (mensaje válido, mensaje inválido y el Runner con 10 mensajes).
- Ejecutar los casos del punto 7 (detener el consumidor, reiniciar RabbitMQ, enviar mensajes inválidos) y verificar los resultados en la consola de administración y en los logs del consumidor.
- Tomar las capturas de evidencia.

## Responsabilidad

Los integrantes respondemos por el funcionamiento del proyecto entregado.
