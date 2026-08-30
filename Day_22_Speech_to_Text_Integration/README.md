# Day 22 â€” Speech-to-Text Integration



## Overview



Day 22 extends the AI Learning Companion application by adding **speech-to-text (STT)** functionality.



The existing AI Learning Companion supports text-based interaction with Google Gemini, personas, streaming responses, prompt experiments, session management, moderation, and other AI features.



In this task, voice input was integrated into the existing application without changing the overall frontend architecture or user experience.



The user can record speech through the browser microphone. The recorded audio is sent to the FastAPI backend, where **Faster-Whisper** performs local speech recognition. The resulting transcript can then be used as normal text input for the AI application.



\---



## Objectives



The main objectives of Day 22 were:



* Integrate speech-to-text into the existing AI Learning Companion.

* Capture microphone audio in the React frontend.

* Send recorded audio to the FastAPI backend.

* Implement a dedicated `/api/transcribe` endpoint.

* Use Faster-Whisper for local speech recognition.

* Keep STT separate from the existing LLM/RAG processing.

* Maintain the existing Day 14 frontend design.

* Support local/offline speech recognition after the model is downloaded.

* Document STT architecture and model alternatives.



\---



## Project Structure



```text

Day\_22\_Speech\_to\_Text\_Integration/

â”‚

â”œâ”€â”€ backend/

â”‚   â”œâ”€â”€ main.py

â”‚   â”œâ”€â”€ main\_day14\_backup.py

â”‚   â”œâ”€â”€ moderation.py

â”‚   â”œâ”€â”€ prompts.py

â”‚   â”œâ”€â”€ requirements.txt

â”‚   â””â”€â”€ .env.example

â”‚

â”œâ”€â”€ client/

â”‚   â”œâ”€â”€ src/

â”‚   â”‚   â”œâ”€â”€ components/

â”‚   â”‚   â”‚   â”œâ”€â”€ ChatMessage.jsx

â”‚   â”‚   â”‚   â”œâ”€â”€ MessageInput.jsx

â”‚   â”‚   â”‚   â”œâ”€â”€ PersonaSelector.jsx

â”‚   â”‚   â”‚   â”œâ”€â”€ PromptLab.jsx

â”‚   â”‚   â”‚   â”œâ”€â”€ Sidebar.jsx

â”‚   â”‚   â”‚   â”œâ”€â”€ SpeechRecorder.jsx

â”‚   â”‚   â”‚   â”œâ”€â”€ StatsBar.jsx

â”‚   â”‚   â”‚   â””â”€â”€ TypingIndicator.jsx

â”‚   â”‚   â”œâ”€â”€ App.jsx

â”‚   â”‚   â”œâ”€â”€ api.js

â”‚   â”‚   â”œâ”€â”€ index.css

â”‚   â”‚   â””â”€â”€ main.jsx

â”‚   â”œâ”€â”€ package.json

â”‚   â”œâ”€â”€ package-lock.json

â”‚   â”œâ”€â”€ tailwind.config.js

â”‚   â””â”€â”€ vite.config.js

â”‚

â”œâ”€â”€ docs/

â”‚   â””â”€â”€ STT\_PIPELINE\_AND\_MODEL\_COMPARISON.md

â”‚

â””â”€â”€ README.md

```



\---



## Technology Stack



### Backend



* Python

* FastAPI

* Uvicorn

* Google Gemini API

* Faster-Whisper

* Pydantic

* python-dotenv

* python-multipart



### Frontend



* React

* Vite

* JavaScript

* Tailwind CSS

* Browser MediaRecorder API



### Speech Recognition



The project uses:



**Faster-Whisper**



Faster-Whisper is an optimized implementation of the Whisper model using CTranslate2. It provides efficient local inference and supports CPU and GPU execution.



\---



## Speech-to-Text Architecture



The implemented architecture is:



```text

User

&#x20; â”‚

&#x20; â–¼

Browser Microphone

&#x20; â”‚

&#x20; â–¼

MediaRecorder API

&#x20; â”‚

&#x20; â–¼

Audio Blob

&#x20; â”‚

&#x20; â–¼

React SpeechRecorder

&#x20; â”‚

&#x20; â”‚ POST /api/transcribe

&#x20; â–¼

FastAPI Backend

&#x20; â”‚

&#x20; â–¼

Faster-Whisper

&#x20; â”‚

&#x20; â–¼

Transcript

&#x20; â”‚

&#x20; â–¼

React Application

&#x20; â”‚

&#x20; â–¼

Existing Text/AI Pipeline

```



The important design principle is that speech recognition only converts speech into text.



```text

Speech â†’ STT â†’ Text

```



The resulting text can then follow the existing application flow.



\---



## Why Faster-Whisper?



Faster-Whisper was selected for the backend because it provides:



* Local inference

* Offline capability after model download

* Whisper model compatibility

* CPU and GPU support

* Quantization support

* Efficient inference

* Multilingual speech recognition

* No per-request third-party STT API cost



For this implementation, the default configuration is:



```text

Model: base

Device: CPU

Compute type: int8

```



The configuration can be changed through environment variables.



\---



## Whisper Configuration



The backend supports the following environment variables:



```text

WHISPER\_MODEL\_SIZE

WHISPER\_DEVICE

WHISPER\_COMPUTE\_TYPE

```



Default values:



```text

WHISPER\_MODEL\_SIZE=base

WHISPER\_DEVICE=cpu

WHISPER\_COMPUTE\_TYPE=int8

```



The Whisper model is loaded lazily.



This means the model is not downloaded and loaded when FastAPI starts. It is loaded when the transcription endpoint is used for the first time.



This reduces initial server startup time and unnecessary resource usage.



\---



## Frontend Speech Recording



The React application uses the browser's:



```text

MediaRecorder API

```



The `SpeechRecorder.jsx` component:



1\. Requests microphone permission.

2\. Starts recording.

3\. Collects audio chunks.

4\. Stops recording when requested.

5\. Creates an audio Blob.

6\. Sends the Blob to the backend.

7\. Receives the transcript.

8\. Passes the transcript back to the application.



The audio is sent as:



```text

multipart/form-data

```



with the recorded file.



\---



## Backend API



### POST `/api/transcribe`



Transcribes an uploaded audio file using Faster-Whisper.



Request:



```text

POST /api/transcribe

Content-Type: multipart/form-data

```



The request contains the recorded audio file.



Example response:



```json

{

&#x20; "text": "What is machine learning?"

}

```



\---



### POST `/api/speech-to-text`



An additional speech-to-text route is available for compatibility with the application.



It uses the same underlying transcription functionality.



\---



## Existing AI Endpoints



The Day 22 backend retains the existing AI Learning Companion functionality.



Important endpoints include:



```text

GET    /

POST   /api/chat

POST   /api/chat/stream

POST   /api/chat/regenerate



GET    /api/sessions

GET    /api/sessions/{session\_id}

DELETE /api/sessions/{session\_id}



POST   /api/sessions/{session\_id}/title



GET    /api/personas



POST   /api/prompts/structured-json

POST   /api/prompts/{prompt\_type}



POST   /api/experiment/sampling



POST   /api/transcribe

POST   /api/speech-to-text

```



\---



## Running the Backend



Navigate to the backend:



```powershell

cd Day\_22\_Speech\_to\_Text\_Integration\\backend

```



Activate the virtual environment:



```powershell

.\\.venv\\Scripts\\activate

```



Install dependencies:



```powershell

python -m pip install -r requirements.txt

```



Run FastAPI:



```powershell

python -m uvicorn main:app --reload --port 8000

```



The API documentation is available at:



```text

http://127.0.0.1:8000/docs

```



\---



## Running the Frontend



Open another terminal and navigate to the client:



```powershell

cd Day\_22\_Speech\_to\_Text\_Integration\\client

```



Install dependencies if required:



```powershell

npm install

```



Start the development server:



```powershell

npm run dev

```



Vite normally starts the application at:



```text

http://localhost:5173

```



\---



## Environment Variables



Create a `.env` file inside the backend directory.



Example:



```text

GEMINI\_API\_KEY=your\_api\_key\_here



WHISPER\_MODEL\_SIZE=base

WHISPER\_DEVICE=cpu

WHISPER\_COMPUTE\_TYPE=int8

```



The `.env` file should not be committed to Git.



A `.env.example` file is included as a safe template.



\---



## Testing the STT Feature



The speech-to-text workflow can be tested through the application or FastAPI Swagger documentation.



Open:



```text

http://127.0.0.1:8000/docs

```



Find:



```text

POST /api/transcribe

```



Upload an audio recording and execute the request.



A successful response should contain:



```json

{

&#x20; "text": "..."

}

```



The browser workflow can then be tested by:



1\. Opening the React application.

2\. Allowing microphone permission.

3\. Clicking the microphone button.

4\. Speaking a sentence.

5\. Stopping the recording.

6\. Waiting for transcription.

7\. Confirming that the transcript is returned.



\---



## Production Build Verification



The React frontend was also verified using:



```powershell

npm run build

```



The Vite production build completes successfully and generates a:



```text

client/dist/

```



directory.



The `dist` directory contains the optimized production assets generated by Vite.



It is not required for normal development because `npm run dev` serves the application directly.



\---



## STT Processing Pipeline



```text

Audio

&#x20; â†“

MediaRecorder

&#x20; â†“

Audio Blob

&#x20; â†“

HTTP multipart upload

&#x20; â†“

FastAPI

&#x20; â†“

Faster-Whisper

&#x20; â†“

Transcript

```



The transcript can then become the query for the existing AI/RAG workflow:



```text

Voice

&#x20; â†“

Speech-to-Text

&#x20; â†“

Text Query

&#x20; â†“

Existing Retrieval / AI Pipeline

&#x20; â†“

LLM

&#x20; â†“

Answer

```



\---



## Whisper Audio Representation



Whisper does not use traditional MFCC features as its primary audio representation.



The simplified Whisper pipeline is:



```text

Raw Audio

&#x20;   â†“

Log-Mel Spectrogram

&#x20;   â†“

Transformer Encoder

&#x20;   â†“

Encoded Audio Representation

&#x20;   â†“

Transformer Decoder

&#x20;   â†“

Autoregressive Token Prediction

&#x20;   â†“

Transcript

```



This distinction is important when comparing Whisper with traditional ASR systems.



\---



## Local STT Alternatives



The project documentation also evaluates several open-source alternatives:



| Model / Toolkit | Main Characteristics                          |

| --------------- | --------------------------------------------- |

| Whisper         | Multilingual encoder-decoder Transformer ASR  |

| faster-whisper  | Optimized Whisper inference using CTranslate2 |

| wav2vec2        | Transformer-based speech representation + CTC |

| Vosk            | Lightweight offline speech recognition        |



Cloud alternatives considered include:



* Deepgram

* Google Cloud Speech-to-Text

* Microsoft Azure Speech

* AssemblyAI



The complete comparison is available in:



```text

docs/STT\_PIPELINE\_AND\_MODEL\_COMPARISON.md

```



\---



## Local vs Cloud STT



### Local STT



Advantages:



* No per-request cloud STT fee

* Offline capability

* Greater control over audio processing

* Greater model/deployment control

* Suitable for research and local development



Disadvantages:



* Requires local compute

* Model downloads consume storage

* Large models require more memory

* Latency depends on hardware



### Cloud STT



Advantages:



* Managed infrastructure

* Easier initial deployment

* Provider-managed compute

* Scalable services



Disadvantages:



* Requires internet connectivity

* Usage-based costs

* External service dependency

* Less control over processing infrastructure



\---



## Important Accuracy Considerations



Speech recognition accuracy depends on:



* Language

* Accent

* Dialect

* Background noise

* Microphone quality

* Speaking speed

* Domain vocabulary

* Code-switching

* Model size

* Audio quality



For multilingual applications, English performance should not automatically be assumed to represent Urdu, Punjabi, or mixed Urdu-English performance.



Representative application-level audio should therefore be used for evaluation.



\---



## Limitations



The current implementation uses a recorded-audio workflow:



```text

Record â†’ Stop â†’ Upload â†’ Transcribe

```



It is not a true real-time streaming speech recognition system.



Real-time STT would require a different architecture involving:



* Streaming audio transport

* Incremental transcription

* Partial results

* Continuous audio processing



The current request/response design is appropriate for the initial browser-recording implementation.



\---



## Key Learning Outcomes



Day 22 demonstrates:



* Browser microphone integration

* MediaRecorder API

* React component integration

* Multipart file upload

* FastAPI file handling

* Faster-Whisper integration

* Lazy model loading

* Local speech recognition

* STT API design

* Frontend/backend integration

* Production frontend build verification

* STT model comparison

* Local versus cloud deployment considerations



\---



## Final Architecture



```text

&#x20;                AI LEARNING COMPANION

&#x20;                        â”‚

&#x20;       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”

&#x20;       â”‚                                 â”‚

&#x20;   TEXT INPUT                        VOICE INPUT

&#x20;       â”‚                                 â”‚

&#x20;       â”‚                          Browser Microphone

&#x20;       â”‚                                 â”‚

&#x20;       â”‚                           MediaRecorder

&#x20;       â”‚                                 â”‚

&#x20;       â”‚                            Audio Blob

&#x20;       â”‚                                 â”‚

&#x20;       â”‚                         POST /api/transcribe

&#x20;       â”‚                                 â”‚

&#x20;       â”‚                           FastAPI Backend

&#x20;       â”‚                                 â”‚

&#x20;       â”‚                         Faster-Whisper

&#x20;       â”‚                                 â”‚

&#x20;       â”‚                            Transcript

&#x20;       â”‚                                 â”‚

&#x20;       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

&#x20;                        â”‚

&#x20;                   Text Query

&#x20;                        â”‚

&#x20;                        â–¼

&#x20;                Existing AI Pipeline

&#x20;                        â”‚

&#x20;                        â–¼

&#x20;                   Gemini / RAG

&#x20;                        â”‚

&#x20;                        â–¼

&#x20;                   Final Answer

&#x20;                        â”‚

&#x20;                        â–¼

&#x20;                    React UI

```



\---



## Conclusion



Day 22 integrates speech-to-text into the existing AI Learning Companion without replacing its existing frontend architecture.



The browser handles audio capture, FastAPI provides the transcription API, and Faster-Whisper performs local speech recognition. The resulting transcript is treated as normal text so that the existing AI and RAG pipeline can process it.



This design keeps the system modular:



```text

Voice Input

&#x20;   â†“

STT

&#x20;   â†“

Text

&#x20;   â†“

Existing AI/RAG Pipeline

&#x20;   â†“

Answer

```



The implementation provides a practical foundation for future improvements such as language selection, better model selection, streaming transcription, voice activity detection, and full voice-based conversational interaction.




