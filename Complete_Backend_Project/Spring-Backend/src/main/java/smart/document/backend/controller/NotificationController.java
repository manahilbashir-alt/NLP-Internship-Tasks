package smart.document.backend.controller;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;

@RestController
@RequestMapping("/api/notifications")
public class NotificationController {

    @GetMapping(
            value = "/stream",
            produces = MediaType.TEXT_EVENT_STREAM_VALUE
    )
    public SseEmitter streamNotifications() {

        SseEmitter emitter = new SseEmitter(0L);

        new Thread(() -> {
            try {
                emitter.send(
                        SseEmitter.event()
                                .name("message")
                                .data("Smart Document SSE connection established")
                );

                Thread.sleep(3000);

                emitter.send(
                        SseEmitter.event()
                                .name("document")
                                .data("New document notification")
                );

            } catch (IOException | InterruptedException e) {
                emitter.completeWithError(e);
            }
        }).start();

        return emitter;
    }
}