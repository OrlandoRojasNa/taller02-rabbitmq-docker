package co.edu.fet.sd.consumidor.config;

import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    /** Misma declaracion que el productor y que definitions.json: cola durable. */
    @Bean
    public Queue colaSensores(@Value("${app.cola}") String nombreCola) {
        return QueueBuilder.durable(nombreCola).build();
    }
}
