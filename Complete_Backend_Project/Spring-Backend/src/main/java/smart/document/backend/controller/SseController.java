package smart.document.backend.controller;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;

@RestController
public class SseController {

    @GetMapping(value = "/api/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamEvents() {

        SseEmitter emitter = new SseEmitter(0L);

        try {
            emitter.send(
                    SseEmitter.event()
                            .name("document-update")
                            .data("Smart Document Backend is running")
            );
        } catch (IOException e) {
            emitter.completeWithError(e);
        }

        return emitter;
    }
}
