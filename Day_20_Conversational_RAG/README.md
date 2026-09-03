# Day 20 - Conversational RAG

## Objective

The objective of Day 20 is to build a Conversational Retrieval-Augmented Generation (RAG) system using LangChain and ChromaDB.

The system extends a traditional RAG pipeline by adding conversation memory, follow-up question handling, contextual compression, source citation, and a FastAPI interface.

The system can:

* Retrieve relevant documents using LangChain's ChromaDB retriever.
* Maintain conversation history using session-based memory.
* Understand follow-up questions.
* Rewrite follow-up questions into standalone questions.
* Use contextual compression to reduce irrelevant retrieved content.
* Generate answers using Google Gemini.
* Provide source information with each response.
* Expose the complete Conversational RAG pipeline through a FastAPI endpoint.
* Test multiple independent multi-turn conversations.

---

## Project Structure

```text
Day_20_Conversational_RAG/
│
├── langchain_retriever.py
├── conversational_chain.py
├── api.py
├── test_conversations.py
├── conversation_test_results.json
└── README.md
```

---

## Technologies Used

* Python
* LangChain
* LangChain Chroma
* ChromaDB
* Hugging Face Sentence Transformers
* Google Gemini
* FastAPI
* Pydantic
* Requests
* python-dotenv

---

## Existing Vector Database

The Conversational RAG system uses the ChromaDB created during Day 17.

### ChromaDB Configuration

```text
Collection:
document_chunks

Embedding Model:
sentence-transformers/all-MiniLM-L6-v2

Vector Database:
ChromaDB
```

The Day 17 ChromaDB contains the document chunks used by the LangChain retriever.

---

# 1. LangChain Chroma Retriever

The first component connects LangChain with the existing ChromaDB vector database.

The system creates a LangChain `Chroma` vector store and converts it into a retriever.

```text
User Question
      ↓
LangChain Chroma Retriever
      ↓
Relevant Documents
```

Similarity search is used to retrieve the most relevant document chunks.

The retriever uses a configurable `top_k` value to control the number of documents retrieved.

The implementation also provides a direct vectorstore test and a LangChain retriever test to verify that the existing ChromaDB can be successfully accessed through LangChain.

---

# 2. Conversational RAG

A traditional RAG system normally treats each question independently.

Conversational RAG is different because it uses previous conversation turns to understand the current question.

For example:

```text
User:
Who is Mr. Darcy?

Assistant:
[Answer about Mr. Darcy]

User:
What about his relationship with Elizabeth?
```

The second question contains the reference `"his"`.

The system uses the conversation history to understand that `"his"` refers to Mr. Darcy.

It rewrites the question as:

```text
What is Mr. Darcy's relationship with Elizabeth?
```

The rewritten question is then passed to the retrieval pipeline.

---

# 3. Question Rewriting

Follow-up questions are converted into standalone questions before document retrieval.

The rewriting process is:

```text
Original Follow-up Question
          ↓
Conversation History
          ↓
Google Gemini
          ↓
Standalone Question
          ↓
Retriever
```

The question rewriting component helps resolve references such as:

* he
* she
* his
* her
* it
* they
* this
* that
* previous point
* second point

For example:

```text
Previous Question:
Who is Mr. Bingley?

Follow-up:
What is his relationship with Jane Bennet?

Rewritten:
What is Mr. Bingley's relationship with Jane Bennet?
```

The original user question is preserved in the conversation history.

---

# 4. Contextual Compression

The system uses a Contextual Compression Retriever to reduce irrelevant retrieved content.

The basic retrieval pipeline is:

```text
Query
  ↓
Retrieve Documents
  ↓
Return Documents
```

The compression pipeline is:

```text
Query
  ↓
Retrieve Documents
  ↓
Embedding-Based Compression Filter
  ↓
Relevant Documents
```

An embedding-based `EmbeddingsFilter` is used as the compressor.

The compressor compares the relevance of retrieved documents using the same embedding model and removes documents that do not meet the configured similarity threshold.

Current configuration:

```text
Base Retriever:
top_k = 4

Compression:
k = 3

Similarity Threshold:
0.3
```

This helps reduce irrelevant context before the retrieved information is passed to the LLM.

---

# 5. Answer Generation

After question rewriting, retrieval, and contextual compression, the relevant document context is passed to Google Gemini.

The complete generation process is:

```text
User Question
      ↓
Question Rewriting
      ↓
Chroma Retrieval
      ↓
Contextual Compression
      ↓
Retrieved Context
      ↓
Google Gemini
      ↓
Final Answer
```

The LLM is instructed to:

* Use the retrieved document context as the main source.
* Use conversation history to understand conversational references.
* Avoid inventing information.
* State when the required information is not available.
* Provide a clear and concise answer.

This helps reduce unsupported answers when the knowledge base does not contain the required information.

---

# 6. Source Citation

The system provides source information for every generated response.

The citation contains:

```text
Filename
Page Number
Chunk Index
```

Example:

```text
- document.docx, page None, chunk 158
- document.docx, page None, chunk 159
```

The current ChromaDB contains some records where page metadata is unavailable.

Therefore, those records appear as:

```text
page None
```

No page number is fabricated when the original metadata does not contain one.

Some documents do contain page information. For example, one test result contained:

```text
native.pdf, page 3, chunk 11
```

---

# 7. FastAPI Integration

The complete Conversational RAG pipeline is exposed through FastAPI.

## Endpoint

```text
POST /api/rag/chat
```

## Request

```json
{
    "session_id": "test_session_1",
    "question": "Who is Mr. Darcy?"
}
```

## Response

```json
{
    "session_id": "test_session_1",
    "question": "Who is Mr. Darcy?",
    "rewritten_question": "Who is Mr. Darcy?",
    "answer": "...",
    "sources": "..."
}
```

The endpoint accepts a session ID so that multiple requests can belong to the same conversation.

---

# 8. Session Memory

Conversation history is maintained using a session ID.

Each session has its own conversation history.

```text
Session A
 ├── Question 1
 ├── Answer 1
 ├── Question 2
 └── Answer 2

Session B
 ├── Question 1
 └── Answer 1
```

This prevents conversations from different sessions from being mixed together.

The current implementation stores session histories in a Python dictionary.

When a new question arrives:

```text
Session ID
     ↓
Retrieve Existing History
     ↓
Question Rewriting
     ↓
RAG Pipeline
     ↓
New Answer
     ↓
Update Session History
```

The updated history is stored for subsequent requests.

---

# 9. API Flow

The complete API flow is:

```text
Client
  ↓
FastAPI
  ↓
Session History
  ↓
Question Rewriting
  ↓
LangChain Chroma Retriever
  ↓
Contextual Compression
  ↓
Retrieved Context
  ↓
Google Gemini
  ↓
Answer + Sources
  ↓
FastAPI Response
```

---

# 10. Running the Application

Navigate to the project directory:

```powershell
cd D:\NLP-Internship\Day_20_Conversational_RAG
```

Start the FastAPI server:

```powershell
uvicorn api:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface can be used to manually test the `/api/rag/chat` endpoint.

---

# 11. Testing

The project includes a testing script:

```text
test_conversations.py
```

The script sends 10 independent multi-turn conversations to the FastAPI endpoint.

Each conversation contains three turns.

Therefore:

```text
10 conversations × 3 turns = 30 requests
```

Each conversation uses a separate session ID.

The testing script records:

* Session ID
* Original question
* Rewritten question
* Generated answer
* Retrieved sources
* Errors, if any

The results are saved in:

```text
conversation_test_results.json
```

---

# 12. Multi-Turn Conversation Testing

The tests contain independent questions about different characters, relationships, events, and locations from the indexed documents.

The purpose is to verify whether the system can maintain context across multiple turns.

For example:

```text
Turn 1:
Who is Mr. Bingley?

Turn 2:
What is his relationship with Jane Bennet?

Turn 3:
How does his friendship with Mr. Darcy affect this?
```

The system successfully rewrites the follow-up questions using previous conversation context.

For example:

```text
Original:
What is his relationship with Jane Bennet?

Rewritten:
What is Mr. Bingley's relationship with Jane Bennet?
```

Another example:

```text
Original:
How does his friendship with Mr. Darcy affect this?

Rewritten:
How does Mr. Bingley's friendship with Mr. Darcy affect his relationship with Jane Bennet?
```

---

# 13. Test Results

The 10 multi-turn conversations were successfully executed.

The test produced:

```text
10 Conversations
30 Total Turns
30 API Requests
```

The FastAPI endpoint successfully processed the conversations and generated responses with rewritten questions and source information.

The results were saved to:

```text
conversation_test_results.json
```

---

# 14. Memory Evaluation

The multi-turn tests were used to evaluate whether session memory improves conversational understanding and retrieval.

## 14.1 Where Memory Helped

Conversation memory successfully helped resolve references in follow-up questions.

Examples include:

### Conversation 1

```text
Question:
What is his relationship with Jane Bennet?

Rewritten:
What is Mr. Bingley's relationship with Jane Bennet?
```

Here, `"his"` was correctly resolved to Mr. Bingley.

Another follow-up:

```text
Question:
How does his friendship with Mr. Darcy affect this?

Rewritten:
How does Mr. Bingley's friendship with Mr. Darcy affect his relationship with Jane Bennet?
```

Both `"his"` and `"this"` were resolved using the previous conversation context.

### Conversation 3

```text
Question:
What does he claim about Mr. Darcy?

Rewritten:
What does Mr. Wickham claim about Mr. Darcy?
```

The reference `"he"` was correctly resolved to Mr. Wickham.

### Conversation 6

```text
Question:
What is his connection to the Bennet family?

Rewritten:
What is Mr. Collins's connection to the Bennet family?
```

The reference `"his"` was correctly resolved to Mr. Collins.

### Conversation 7

```text
Question:
What is her relationship with Elizabeth?

Rewritten:
What is Charlotte Lucas's relationship with Elizabeth Bennet?
```

The reference `"her"` was correctly resolved to Charlotte Lucas.

These examples demonstrate that session memory is helping the system transform ambiguous follow-up questions into meaningful standalone retrieval queries.

---

# 15. Memory and Retrieval Noise

The tests also demonstrated an important limitation.

Correct question rewriting does not always guarantee that the required information will be retrieved.

For example, in Conversation 10:

```text
Original:
What problem does her relationship with Mr. Wickham create?

Rewritten:
What problem does Lydia Bennet's relationship with Mr. Wickham create in the story?
```

The rewriting was correct.

However, the retrieved documents did not contain enough information to answer the question.

The system therefore returned that the information was not available in the provided documents.

Similar cases occurred in other conversations where the question was correctly rewritten but the required information was not present in the retrieved document chunks.

This shows that the limitation was mainly related to knowledge-base coverage and retrieval rather than failure of conversational memory.

---

# 16. Overall Memory Evaluation

The testing demonstrates that session memory is useful when a follow-up question depends on previous context.

The overall flow is:

```text
Conversation History
        ↓
Resolve References
        ↓
Standalone Question
        ↓
Better Retrieval Query
        ↓
Relevant Context
        ↓
Answer
```

However:

```text
Good Conversation Memory
          +
Missing Information in Knowledge Base
          ↓
Relevant Answer Cannot Be Generated
```

Therefore, memory improves conversational understanding, but it cannot create information that does not exist in the indexed documents.

---

# 17. Files Description

## `langchain_retriever.py`

Responsible for:

* Connecting to ChromaDB.
* Creating Hugging Face embeddings.
* Creating the LangChain Chroma vector store.
* Creating the basic LangChain retriever.
* Creating the contextual compression retriever.
* Testing the vectorstore.
* Testing basic retrieval.
* Testing contextual compression.

---

## `conversational_chain.py`

Responsible for:

* Creating the Google Gemini LLM.
* Formatting conversation history.
* Rewriting follow-up questions.
* Retrieving documents.
* Building retrieved context.
* Generating answers.
* Formatting source citations.
* Updating conversation history.
* Running a local conversational RAG test.

---

## `api.py`

Responsible for:

* Creating the FastAPI application.
* Defining the chat request and response models.
* Managing session histories.
* Calling the Conversational RAG chain.
* Returning generated answers and source information.
* Clearing session history when required.

---

## `test_conversations.py`

Responsible for:

* Running 10 independent multi-turn conversations.
* Creating separate sessions for each conversation.
* Testing follow-up question rewriting.
* Testing session memory.
* Sending requests to the FastAPI endpoint.
* Saving test results.

---

## `conversation_test_results.json`

Contains the results generated during the 10 multi-turn conversation tests.

The file stores the original questions, rewritten questions, answers, sources, and session information.

---

# 18. Current Implementation Result

The Conversational RAG pipeline was successfully implemented and tested.

The system successfully demonstrated:

* ChromaDB retrieval through LangChain.
* LangChain-based Chroma retriever.
* Contextual compression using `EmbeddingsFilter`.
* Google Gemini answer generation.
* Follow-up question rewriting.
* Conversation history.
* Session-based memory.
* Source information in responses.
* FastAPI integration.
* Multi-turn conversation testing.

The FastAPI endpoint was successfully tested using multiple turns within the same session.

The 10-conversation test was also successfully completed.

---

# 19. Limitations

1. The current session memory is stored in a Python dictionary, so conversation history is lost when the FastAPI server restarts.

2. The in-memory session store is primarily suitable for development and testing rather than production-scale deployment.

3. Some existing ChromaDB records have missing page metadata, represented as `None`.

4. The quality of question rewriting depends on the LLM.

5. Contextual compression depends on the selected embedding model and similarity threshold.

6. Retrieval quality depends on the coverage and quality of the indexed documents.

7. A correctly rewritten question may still fail to retrieve the required information if the relevant content is not present in the knowledge base.

8. The evaluation was performed using a limited set of 10 multi-turn conversations.

---

# 20. Conclusion

Day 20 implements a complete Conversational RAG system using LangChain, ChromaDB, contextual compression, Google Gemini, and FastAPI.

The system extends traditional RAG by introducing conversation memory and follow-up question handling.

The final architecture combines:

```text
LangChain
    +
ChromaDB
    +
Contextual Compression
    +
Question Rewriting
    +
Conversation Memory
    +
Google Gemini
    +
FastAPI
```

The resulting system can maintain session-based conversation history, understand references in follow-up questions, retrieve relevant document chunks, compress retrieved content, generate document-grounded answers, and provide source information.

The multi-turn evaluation confirms that conversation memory successfully improves the understanding of follow-up questions, while retrieval performance remains dependent on the information available in the underlying knowledge base.