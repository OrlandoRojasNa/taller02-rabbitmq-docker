package co.edu.fet.sd.productor.dto;

/**
 * Formato de respuesta de la API. {@code status} es boolean, asi Jackson lo
 * serializa como true/false y no como la cadena "true".
 */
public record Respuesta(boolean status, String message) {

    public static Respuesta ok(String message) {
        return new Respuesta(true, message);
    }

    public static Respuesta error(String message) {
        return new Respuesta(false, message);
    }
}
