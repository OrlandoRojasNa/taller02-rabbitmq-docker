package co.edu.fet.sd.productor.controller;

import co.edu.fet.sd.productor.service.PublicadorService;
import org.junit.jupiter.api.Test;
import org.springframework.amqp.AmqpConnectException;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.net.ConnectException;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(MensajeController.class)
@Import({PublicadorService.class, ManejadorErrores.class})
@TestPropertySource(properties = {"app.cola=cola.test", "app.confirm-timeout-ms=1000"})
class MensajeControllerTest {

    @Autowired
    private MockMvc mvc;

    @MockitoBean
    private RabbitTemplate rabbitTemplate;

    @Test
    void mensajeValidoSeEncolaYStatusEsBoolean() throws Exception {
        mvc.perform(post("/api/mensajes")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"sensor\": \"OD-01\", \"valor\": 4.2, \"unidad\": \"mg/L\"}"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.status").value(true))
                .andExpect(jsonPath("$.status").isBoolean())
                .andExpect(jsonPath("$.message").value("Mensaje encolado"));

        verify(rabbitTemplate).invoke(any());
    }

    @Test
    void jsonMalFormadoNoSePublica() throws Exception {
        mvc.perform(post("/api/mensajes")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"sensor\": \"OD-01\", \"valor\": }"))
                .andExpect(status().isBadRequest())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.status").value(false))
                .andExpect(jsonPath("$.status").isBoolean())
                .andExpect(jsonPath("$.message").value("Formato de mensaje inválido"));

        verify(rabbitTemplate, never()).invoke(any());
    }

    @Test
    void textoPlanoNoSePublica() throws Exception {
        mvc.perform(post("/api/mensajes")
                        .contentType(MediaType.TEXT_PLAIN)
                        .content("esto no es json"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(false));

        verify(rabbitTemplate, never()).invoke(any());
    }

    @Test
    void cuerpoVacioNoSePublica() throws Exception {
        mvc.perform(post("/api/mensajes").contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(false));

        verify(rabbitTemplate, never()).invoke(any());
    }

    @Test
    void jsonConBasuraAlFinalNoSePublica() throws Exception {
        mvc.perform(post("/api/mensajes")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"sensor\": \"OD-01\"} basura"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(false));

        verify(rabbitTemplate, never()).invoke(any());
    }

    @Test
    void brokerCaidoRespondeStatusFalse() throws Exception {
        when(rabbitTemplate.invoke(any())).thenThrow(new AmqpConnectException(new ConnectException("sin broker")));

        mvc.perform(post("/api/mensajes")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"sensor\": \"OD-01\"}"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.status").value(false));
    }
}
