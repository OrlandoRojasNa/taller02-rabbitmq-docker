package co.edu.fet.sd.productor.controller;

import co.edu.fet.sd.productor.dto.Respuesta;
import co.edu.fet.sd.productor.service.MensajeInvalidoException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.AmqpException;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** Toda respuesta de error sale en JSON con el mismo formato {status, message}. */
@RestControllerAdvice
public class ManejadorErrores {

    private static final Logger log = LoggerFactory.getLogger(ManejadorErrores.class);

    @ExceptionHandler(MensajeInvalidoException.class)
    public ResponseEntity<Respuesta> mensajeInvalido(MensajeInvalidoException e) {
        log.warn("Mensaje rechazado, no se publica: {}", e.getMessage());
        return responder(HttpStatus.BAD_REQUEST, "Formato de mensaje inválido");
    }

    @ExceptionHandler(AmqpException.class)
    public ResponseEntity<Respuesta> brokerNoDisponible(AmqpException e) {
        log.error("No se pudo publicar en RabbitMQ: {}", e.getMessage());
        return responder(HttpStatus.SERVICE_UNAVAILABLE, "No se pudo publicar el mensaje en la cola");
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<Respuesta> metodoNoSoportado(HttpRequestMethodNotSupportedException e) {
        return responder(HttpStatus.METHOD_NOT_ALLOWED, "Método no permitido, use POST");
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Respuesta> inesperado(Exception e) {
        log.error("Error inesperado", e);
        return responder(HttpStatus.INTERNAL_SERVER_ERROR, "Error interno al procesar el mensaje");
    }

    private ResponseEntity<Respuesta> responder(HttpStatus estado, String mensaje) {
        return ResponseEntity.status(estado)
                .contentType(MediaType.APPLICATION_JSON)
                .body(Respuesta.error(mensaje));
    }
}
