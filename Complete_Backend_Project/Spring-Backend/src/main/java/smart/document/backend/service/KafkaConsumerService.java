package smart.document.backend.service;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class KafkaConsumerService {

    @KafkaListener(
            topics = "document-topic",
            groupId = "smart-document-group"
    )
    public void consumeDocumentEvent(String message) {

        System.out.println(
                "Kafka Event Received: " + message
        );
    }
}