package smart.document.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.cache.annotation.EnableCaching;
@SpringBootApplication
@EnableScheduling
public class SmartDocumentBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(
                SmartDocumentBackendApplication.class,
                args
        );
    }
}