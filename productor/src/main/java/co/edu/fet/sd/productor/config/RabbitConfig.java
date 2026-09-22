package co.edu.fet.sd.productor.config;

import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    /**
     * La cola ya viene creada por definitions.json al arrancar RabbitMQ.
     * Declararla aqui tambien es idempotente (mismos atributos) y sirve de respaldo.
     */
    @Bean
    public Queue colaSensores(@Value("${app.cola}") String nombreCola) {
        return QueueBuilder.durable(nombreCola).build();
    }
}
