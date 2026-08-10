package smart.document.backend.controller;

import jakarta.validation.Valid;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import smart.document.backend.dto.DocumentRequest;
import smart.document.backend.entity.Document;
import smart.document.backend.service.DocumentService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

import java.util.List;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @Operation(
            summary = "Create document",
            description = "Creates a new document for the authenticated user"
    )
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Document created successfully"),
            @ApiResponse(responseCode = "400", description = "Invalid document data"),
            @ApiResponse(responseCode = "401", description = "Unauthorized")
    })
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

    @Operation(
            summary = "Get my documents",
            description = "Returns all documents belonging to the authenticated user"
    )
    @GetMapping
    public List<Document> getMyDocuments(
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        return documentService.getUserDocuments(ownerEmail);
    }

    @Operation(
            summary = "Get document by ID",
            description = "Returns a specific document belonging to the authenticated user"
    )
    @GetMapping("/{id}")
    public Document getDocument(
            @PathVariable Long id,
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        return documentService.getDocument(id, ownerEmail);
    }

    @Operation(
            summary = "Update document",
            description = "Updates an existing document"
    )
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

    @Operation(
            summary = "Delete document",
            description = "Deletes a document belonging to the authenticated user"
    )
    @ApiResponses({
            @ApiResponse(
                    responseCode = "200",
                    description = "Document deleted successfully"
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Document not found"
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Unauthorized"
            )
    })
    @DeleteMapping("/{id}")
    public String deleteDocument(
            @PathVariable Long id,
            Authentication authentication) {

        String ownerEmail = authentication.getName();

        documentService.deleteDocument(id, ownerEmail);

        return "Document deleted successfully";
    }
}