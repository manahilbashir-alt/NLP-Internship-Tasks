package smart.document.backend.repository;

import smart.document.backend.entity.Document;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface DocumentRepository extends JpaRepository<Document, Long> {

    List<Document> findByOwnerEmail(String ownerEmail);

    Optional<Document> findByIdAndOwnerEmail(Long id, String ownerEmail);
}