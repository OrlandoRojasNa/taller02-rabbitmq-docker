package co.edu.fet.sd.productor.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectReader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageBuilder;
import org.springframework.amqp.core.MessageDeliveryMode;
import org.springframework.amqp.core.MessageProperties;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.UUID;

@Service
public class PublicadorService {

    private static final Logger log = LoggerFactory.getLogger(PublicadorService.class);

    private final RabbitTemplate rabbitTemplate;
    private final ObjectReader lectorJson;
    private final String cola;
    private final long confirmTimeoutMs;

    public PublicadorService(RabbitTemplate rabbitTemplate,
                             ObjectMapper objectMapper,
                             @Value("${app.cola}") String cola,
                             @Value("${app.confirm-timeout-ms}") long confirmTimeoutMs) {
        this.rabbitTemplate = rabbitTemplate;
        // Rechaza cuerpos como '{"a":1} basura' (contenido extra despues del JSON)
        this.lectorJson = objectMapper.reader().with(DeserializationFeature.FAIL_ON_TRAILING_TOKENS);
        this.cola = cola;
        this.confirmTimeoutMs = confirmTimeoutMs;
    }

    /**
     * Valida que el cuerpo sea un objeto JSON y lo publica como mensaje persistente.
     * Si no es valido lanza {@link MensajeInvalidoException} y no se publica nada.
     */
    public String publicar(String cuerpo) {
        JsonNode json = validar(cuerpo);

        String id = UUID.randomUUID().toString();
        Message mensaje = MessageBuilder
                .withBody(json.toString().getBytes(StandardCharsets.UTF_8))
                .setContentType(MessageProperties.CONTENT_TYPE_JSON)
                .setContentEncoding(StandardCharsets.UTF_8.name())
                // Persistente: sobrevive a un reinicio del broker (junto con la cola durable)
                .setDeliveryMode(MessageDeliveryMode.PERSISTENT)
                .setMessageId(id)
                .setTimestamp(new Date())
                .build();

        // Publica por el exchange por defecto (routing key = nombre de la cola)
        // y espera la confirmacion del broker antes de responder.
        rabbitTemplate.invoke(operaciones -> {
            operaciones.send("", cola, mensaje);
            operaciones.waitForConfirmsOrDie(confirmTimeoutMs);
            return null;
        });

        log.info("Mensaje publicado en '{}' id={} contenido={}", cola, id, json);
        return id;
    }

    private JsonNode validar(String cuerpo) {
        if (cuerpo == null || cuerpo.isBlank()) {
            throw new MensajeInvalidoException("cuerpo vacio");
        }
        JsonNode json;
        try {
            json = lectorJson.readTree(cuerpo);
        } catch (JsonProcessingException e) {
            throw new MensajeInvalidoException("JSON mal formado: " + e.getOriginalMessage());
        }
        if (json == null || !json.isObject() || json.isEmpty()) {
            throw new MensajeInvalidoException("se esperaba un objeto JSON con al menos un campo");
        }
        return json;
    }
}
