package co.edu.fet.sd.productor.service;

public class MensajeInvalidoException extends RuntimeException {

    public MensajeInvalidoException(String detalle) {
        super(detalle);
    }
}
