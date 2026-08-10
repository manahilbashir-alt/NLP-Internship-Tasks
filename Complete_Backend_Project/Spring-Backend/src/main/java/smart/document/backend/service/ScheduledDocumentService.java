package smart.document.backend.service;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
public class ScheduledDocumentService {

    @Scheduled(fixedRate = 60000)
    public void processDocuments() {

        System.out.println(
                "Scheduled document processing is running..."
        );
    }
}