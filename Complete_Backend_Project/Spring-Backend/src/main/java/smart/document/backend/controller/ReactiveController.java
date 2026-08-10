package smart.document.backend.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import smart.document.backend.service.ReactiveDocumentService;

@RestController
public class ReactiveController {

    private final ReactiveDocumentService reactiveDocumentService;

    public ReactiveController(
            ReactiveDocumentService reactiveDocumentService) {

        this.reactiveDocumentService =
                reactiveDocumentService;
    }

    @GetMapping("/api/reactive/message")
    public Mono<String> getMessage() {

        return reactiveDocumentService
                .getReactiveMessage();
    }

    @GetMapping("/api/reactive/stream")
    public Flux<String> getStream() {

        return reactiveDocumentService
                .getReactiveStream();
    }
}