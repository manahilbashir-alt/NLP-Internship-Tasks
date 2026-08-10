package smart.document.backend.controller;

import jakarta.validation.Valid;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import smart.document.backend.dto.DocumentRequest;
import smart.document.backend.entity.Document;
import smart.document.backend.service.DocumentService;

import java.util.List;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @PostMapping
    public Document createDocument(
            @Valid @RequestBody DocumentRequest request,
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        return documentService.createDocument(
                request.getTitle(),
                request.getContent(),
                ownerEmail
        );
    }

    @GetMapping
    public List<Document> getMyDocuments(
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        return documentService.getUserDocuments(ownerEmail);
    }

    @GetMapping("/{id}")
    public Document getDocument(
            @PathVariable Long id,
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        return documentService.getDocument(id, ownerEmail);
    }

    @PutMapping("/{id}")
    public Document updateDocument(
            @PathVariable Long id,
            @Valid @RequestBody DocumentRequest request,
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        return documentService.updateDocument(
                id,
                request.getTitle(),
                request.getContent(),
                ownerEmail
        );
    }

    @DeleteMapping("/{id}")
    public void deleteDocument(
            @PathVariable Long id,
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        documentService.deleteDocument(id, ownerEmail);
    }
}