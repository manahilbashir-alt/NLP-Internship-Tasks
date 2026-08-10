package smart.document.backend.service;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class ExternalApiService {

    private final WebClient webClient;

    public ExternalApiService(WebClient.Builder builder) {
        this.webClient = builder
                .baseUrl("https://jsonplaceholder.typicode.com")
                .build();
    }

    public String getExternalPost() {
        return webClient
                .get()
                .uri("/posts/1")
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }
}