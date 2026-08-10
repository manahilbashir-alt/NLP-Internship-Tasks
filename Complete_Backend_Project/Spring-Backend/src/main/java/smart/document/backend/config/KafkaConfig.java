package smart.document.backend.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaConfig {

    @Bean
    public NewTopic documentTopic() {
        return TopicBuilder
                .name("document-topic")
                .partitions(1)
                .replicas(1)
                .build();
    }
}