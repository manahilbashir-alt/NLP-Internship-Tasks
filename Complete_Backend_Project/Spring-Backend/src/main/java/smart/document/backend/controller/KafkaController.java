package smart.document.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import smart.document.backend.service.KafkaProducerService;

@RestController
@RequestMapping("/api/kafka")
public class KafkaController {

    private final KafkaProducerService kafkaProducerService;

    public KafkaController(KafkaProducerService kafkaProducerService) {
        this.kafkaProducerService = kafkaProducerService;
    }

    @PostMapping("/send")
    public ResponseEntity<String> sendMessage(
            @RequestParam String message) {

        kafkaProducerService.sendMessage(message);

        return ResponseEntity.ok(
                "Message sent successfully to Kafka"
        );
    }
}