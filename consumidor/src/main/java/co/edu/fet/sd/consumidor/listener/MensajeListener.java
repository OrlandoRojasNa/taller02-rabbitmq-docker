package co.edu.fet.sd.consumidor.listener;

import com.rabbitmq.client.Channel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageProperties;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.atomic.AtomicLong;

@Component
public class MensajeListener {

    private static final Logger log = LoggerFactory.getLogger(MensajeListener.class);
    private static final DateTimeFormatter FORMATO_HORA = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS XXX");

    private final AtomicLong contador = new AtomicLong();

    @RabbitListener(queues = "${app.cola}")
    public void recibir(Message mensaje, Channel canal) throws IOException {
        MessageProperties props = mensaje.getMessageProperties();
        long deliveryTag = props.getDeliveryTag();

        try {
            String contenido = new String(mensaje.getBody(), StandardCharsets.UTF_8);
            String horaRecepcion = ZonedDateTime.now().format(FORMATO_HORA);

            log.info("[#{}] Mensaje recibido | hora de recepcion: {} | id: {} | reentregado: {} | contenido: {}",
                    contador.incrementAndGet(), horaRecepcion, props.getMessageId(),
                    props.isRedelivered(), contenido);

            // Solo despues de procesarlo se confirma (ACK) y RabbitMQ lo retira de la cola
            canal.basicAck(deliveryTag, false);
        } catch (Exception e) {
            log.error("Error procesando el mensaje, se devuelve a la cola", e);
            canal.basicNack(deliveryTag, false, true);
        }
    }
}
