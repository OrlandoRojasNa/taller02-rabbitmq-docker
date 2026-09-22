package co.edu.fet.sd.productor.controller;

import co.edu.fet.sd.productor.dto.Respuesta;
import co.edu.fet.sd.productor.service.PublicadorService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/mensajes")
public class MensajeController {

    private final PublicadorService publicador;

    public MensajeController(PublicadorService publicador) {
        this.publicador = publicador;
    }

    /**
     * Recibe el cuerpo como texto crudo para validar nosotros mismos el JSON
     * y poder responder siempre con el formato {status, message}.
     */
    @PostMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Respuesta> publicar(@RequestBody(required = false) String cuerpo) {
        publicador.publicar(cuerpo);
        return ResponseEntity.ok(Respuesta.ok("Mensaje encolado"));
    }
}
