FROM rabbitmq:4.1-management

# Configuracion propia del taller: definiciones (usuario + cola durable)
COPY rabbitmq.conf /etc/rabbitmq/conf.d/20-taller.conf
COPY definitions.json /etc/rabbitmq/definitions.json
