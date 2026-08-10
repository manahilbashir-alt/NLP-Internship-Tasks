package smart.document.backend.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import reactor.core.publisher.Mono;

import smart.document.backend.service.ExternalApiService;

@RestController
public class ExternalApiController {

    private final ExternalApiService externalApiService;

    public ExternalApiController(ExternalApiService externalApiService) {
        this.externalApiService = externalApiService;
    }

    @GetMapping("/api/external-post")
    public Mono<String> getExternalPost() {
        return externalApiService.getExternalPost();
    }
}