package smart.document.backend.service;

import smart.document.backend.entity.Document;
import smart.document.backend.repository.DocumentRepository;

import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DocumentService {

    private final DocumentRepository documentRepository;

    public DocumentService(DocumentRepository documentRepository) {
        this.documentRepository = documentRepository;
    }

    public Document createDocument(
            String title,
            String content,
            String ownerEmail) {

        Document document = new Document(
                title,
                content,
                ownerEmail
        );

        return documentRepository.save(document);
    }

    public List<Document> getUserDocuments(String ownerEmail) {
        return documentRepository.findByOwnerEmail(ownerEmail);
    }

    @Cacheable(value = "documents", key = "#id + '-' + #ownerEmail")
    public Document getDocument(Long id, String ownerEmail) {

        System.out.println("Fetching document from DATABASE...");

        return documentRepository
                .findByIdAndOwnerEmail(id, ownerEmail)
                .orElseThrow(
                        () -> new RuntimeException("Document not found")
                );
    }

    @CacheEvict(value = "documents", key = "#id + '-' + #ownerEmail")
    public Document updateDocument(
            Long id,
            String title,
            String content,
            String ownerEmail) {

        Document document = documentRepository
                .findByIdAndOwnerEmail(id, ownerEmail)
                .orElseThrow(
                        () -> new RuntimeException("Document not found")
                );

        document.setTitle(title);
        document.setContent(content);

        return documentRepository.save(document);
    }

    @CacheEvict(value = "documents", key = "#id + '-' + #ownerEmail")
    public void deleteDocument(Long id, String ownerEmail) {

        Document document =
                documentRepository
                        .findByIdAndOwnerEmail(id, ownerEmail)
                        .orElseThrow(
                                () -> new RuntimeException("Document not found")
                        );

        documentRepository.delete(document);
    }
}