package smart.document.backend.service;

import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Duration;

@Service
public class ReactiveDocumentService {

    public Mono<String> getReactiveMessage() {

        return Mono.just(
                "Reactive processing is working"
        );
    }

    public Flux<String> getReactiveStream() {

        return Flux.just(
                "Document 1 processed",
                "Document 2 processed",
                "Document 3 processed"
        ).delayElements(Duration.ofMillis(500));
    }
}