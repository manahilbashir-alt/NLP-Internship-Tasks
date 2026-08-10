# Smart Document Intelligence Backend

A complete Spring Boot backend project demonstrating modern backend development concepts including REST APIs, database management, security, caching, reactive programming, messaging, WebSockets, microservices, Docker, testing, and CI/CD.

## Overview

The Smart Document Backend provides APIs for managing documents and users with secure authentication and multiple enterprise-level backend technologies.

The project is designed as a practical demonstration of a production-style Spring Boot backend architecture.

## Technology Stack

* Java 21
* Spring Boot
* Spring MVC / REST
* Spring Data JPA
* PostgreSQL
* Spring Security
* JWT Authentication
* Spring WebFlux
* Redis
* Spring Cache
* Apache Kafka
* Spring Batch
* WebSockets
* Server-Sent Events (SSE)
* WebClient
* Spring Actuator
* OpenAPI / Swagger
* Docker
* GitHub Actions
* Maven

## Main Features

### Authentication & Security

* User signup and login
* BCrypt password encryption
* JWT-based authentication
* Stateless Spring Security configuration

### Document Management

* Create documents
* Retrieve documents
* Update documents
* Delete documents
* User-specific document access
* JPA/PostgreSQL persistence

### Validation & Error Handling

* Request validation
* Centralized exception handling
* Appropriate HTTP responses

### Caching

* Spring Cache integration
* Redis support
* Document caching using `@Cacheable`
* Cache invalidation using `@CacheEvict`

### Reactive Programming

* Project Reactor
* `Mono`
* `Flux`
* Spring WebFlux
* Reactive WebClient

### Real-Time Communication

* Server-Sent Events (SSE)
* WebSocket communication

### Messaging

* Apache Kafka integration
* Kafka Streams support

### Batch & Scheduling

* Spring Batch job and step
* Scheduled document processing

### External API Integration

* WebClient-based REST client
* External API communication

### Microservices

The project includes a separate Notification Service.

```text
Spring Backend       :8080
       |
       | REST / WebClient
       v
Notification Service :8081
```

The Notification Service is independently deployable and provides notification-related API functionality.

## API Documentation

Swagger/OpenAPI is included for API documentation and testing.

Typical local URL:

```text
http://localhost:8080/swagger-ui/index.html
```

## Project Structure

```text
Complete_Backend_Project/
│
├── Spring-Backend/
│   ├── src/
│   ├── pom.xml
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
│
└── Notification-Service/
    ├── src/
    ├── pom.xml
    └── application.properties
```

## Running the Main Backend

From the `Spring-Backend` directory:

```powershell
.\mvnw.cmd spring-boot:run
```

The backend runs on:

```text
http://localhost:8080
```

## Running the Notification Service

From the `Notification-Service` directory:

```powershell
.\mvnw.cmd spring-boot:run
```

The Notification Service runs on:

```text
http://localhost:8081
```

## Database

PostgreSQL is used as the primary relational database.

Default development configuration:

```text
Database: smart_document_db
Port: 5432
```

## Redis

Redis is used for caching and related backend functionality.

```text
Host: localhost
Port: 6379
```

## Docker

The project includes Docker configuration for containerized execution.

```text
Dockerfile
docker-compose.yml
```

## CI/CD

GitHub Actions is configured through:

```text
.github/workflows/ci.yml
```

The workflow supports automated project build and validation.

## Testing

The project uses Spring Boot testing support and Maven for running automated tests.

```powershell
.\mvnw.cmd test
```

## Postman

A complete Postman collection is included for API testing:

```text
Postman_Complete_Backend_Collection.json
```

## Project Status

The project demonstrates the following backend concepts:

* REST API development
* CRUD operations
* PostgreSQL/JPA
* Validation
* Exception handling
* JWT Security
* Scheduling
* Batch processing
* Redis caching
* Reactive programming
* SSE
* WebSockets
* REST clients
* Kafka
* Microservices
* Docker
* Swagger/OpenAPI
* CI/CD
* Automated testing

## Author
Manahil 