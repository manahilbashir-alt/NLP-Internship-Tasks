# STT Pipeline and Model Comparison

## 1. Purpose

This document studies the Speech-to-Text (STT) pipeline required for the
AI Tutor application and establishes the technical basis for integrating
voice input into the existing React + FastAPI + RAG system.

The study covers:

-   The complete STT processing pipeline
-   Audio features including spectrograms, Mel spectrograms, and MFCCs
-   Whisper's encoder-decoder Transformer architecture
-   Comparison with open-source alternatives: faster-whisper, wav2vec2,
    and Vosk
-   Comparison with cloud/paid STT services: Deepgram, Google
    Speech-to-Text, Azure Speech, and AssemblyAI
-   Accuracy, latency, cost, offline capability, privacy, and deployment
    considerations
-   The engineering rationale for selecting an STT approach for the
    application

------------------------------------------------------------------------

## 2. What is Speech-to-Text?

Speech-to-Text (STT), also called Automatic Speech Recognition (ASR),
converts human speech represented as an audio signal into written text.

A high-level STT pipeline can be represented as:

``` text
Human Speech
    ↓
Microphone
    ↓
Raw Audio Signal
    ↓
Audio Preprocessing
    ↓
Feature Extraction
    ↓
Acoustic/Speech Representation
    ↓
ASR Model
    ↓
Decoder / Token Generation
    ↓
Text Transcript
```

The exact architecture depends on the ASR system.

Traditional ASR systems commonly separate acoustic modeling, language
modeling, and decoding. Modern end-to-end systems can combine much of
this functionality into a neural architecture.

------------------------------------------------------------------------

## 3. Raw Audio

A microphone converts sound waves into an electrical signal and then
into digital samples.

A digital audio signal is represented as a sequence of amplitude values:

``` text
x[0], x[1], x[2], ..., x[n]
```

Each value represents the measured signal amplitude at a particular
sampling instant.

### Sampling Rate

The sampling rate specifies how many samples are recorded per second.

Common rates include:

-   8 kHz
-   16 kHz
-   44.1 kHz
-   48 kHz

For speech recognition, 16 kHz is commonly used because it provides
sufficient information for the speech frequency range while keeping
computation manageable.

Whisper internally processes audio using a standardized audio
representation, so incoming browser recordings may require
decoding/resampling before inference.

------------------------------------------------------------------------

## 4. Audio Preprocessing

Before an ASR model receives audio, the recording may need
preprocessing.

Typical operations include:

1.  Decode the uploaded audio format.
2.  Convert to a supported numeric representation.
3.  Convert to mono when required.
4.  Resample to the model's expected sample rate.
5.  Optionally normalize or perform noise/VAD processing.

For the web application:

``` text
Browser Microphone
       ↓
MediaRecorder
       ↓
Audio Blob
       ↓
HTTP Upload
       ↓
FastAPI
       ↓
Audio Decode / Preprocess
       ↓
ASR Model
```

The browser recording format should therefore be handled carefully by
the backend rather than assuming that every browser will produce
identical audio.

------------------------------------------------------------------------

# 5. Spectrogram

A raw waveform shows amplitude over time. An STFT-based spectrogram
represents how frequency content changes over time.

Conceptually:

``` text
Waveform
Amplitude
   │     /\       /\
   │ /\ /  \  /\ /  \
   └────────────────────→ Time

              ↓

Spectrogram
Frequency
   │ ░▒▓▒░
   │  ░▓██▓░
   │ ░▒▓███▒░
   └────────────────────→ Time
```

The signal is divided into short overlapping frames. A Fourier transform
is applied to each frame to estimate the frequency content.

This gives a time-frequency representation.

------------------------------------------------------------------------

# 6. Mel Spectrogram

Human hearing does not perceive frequency linearly. The Mel scale
represents frequency in a way that is closer to human auditory
perception.

A Mel spectrogram is produced by:

``` text
Raw Audio
   ↓
Framing / Windowing
   ↓
Short-Time Fourier Transform
   ↓
Power Spectrum
   ↓
Mel Filter Bank
   ↓
Mel Spectrogram
```

The Mel filter bank groups frequency information into perceptually
motivated frequency bands.

------------------------------------------------------------------------

# 7. Log-Mel Spectrogram

Whisper uses a log-Mel spectrogram as its audio input representation.

Conceptually:

``` text
Audio waveform
      ↓
STFT
      ↓
Mel filter bank
      ↓
Mel spectrogram
      ↓
Log scaling
      ↓
Log-Mel spectrogram
      ↓
Whisper Encoder
```

Log scaling compresses the dynamic range of the acoustic representation
and makes the representation more suitable for neural processing.

------------------------------------------------------------------------

# 8. MFCC vs Mel Spectrogram

MFCC (Mel-Frequency Cepstral Coefficients) and Mel spectrograms are
related but are not the same representation.

### MFCC pipeline

``` text
Audio
 ↓
Pre-emphasis
 ↓
Framing
 ↓
Windowing
 ↓
FFT
 ↓
Mel Filter Bank
 ↓
Log
 ↓
DCT
 ↓
MFCC coefficients
```

### Mel spectrogram pipeline

``` text
Audio
 ↓
STFT
 ↓
Mel Filter Bank
 ↓
Log
 ↓
Log-Mel Spectrogram
```

MFCCs are widely used in classical and some neural ASR systems. Whisper
uses a log-Mel spectrogram rather than an MFCC representation.

Therefore, documentation should not incorrectly state:

> "Whisper converts audio into MFCCs."

The technically appropriate statement is:

> "Whisper converts the input waveform into a log-Mel spectrogram
> representation before processing it with its Transformer encoder."

------------------------------------------------------------------------

# 9. Traditional ASR Architecture

A conventional ASR system can be represented as:

``` text
Audio
  ↓
Feature Extraction
(MFCC / Filterbanks)
  ↓
Acoustic Model
  ↓
Pronunciation / Lexical Model
  ↓
Language Model
  ↓
Decoder
  ↓
Text
```

The acoustic model estimates relationships between acoustic observations
and speech units. The language model helps determine plausible word
sequences, while the decoder searches for a likely transcription.

Modern neural systems often simplify or replace these separate
components.

------------------------------------------------------------------------

# 10. Whisper Architecture

Whisper is an end-to-end multilingual ASR model based on an
encoder-decoder Transformer architecture.

Its high-level architecture is:

``` text
Raw Audio
    ↓
Log-Mel Spectrogram
    ↓
Transformer Encoder
    ↓
Encoded Audio Representation
    ↓
Transformer Decoder
    ↓
Autoregressive Token Prediction
    ↓
Text Tokens
    ↓
Transcript
```

## 10.1 Encoder

The encoder receives the audio representation.

Its job is to transform the log-Mel spectrogram into contextual
representations that capture information about the speech.

Conceptually:

``` text
Log-Mel Spectrogram
        ↓
Input Projection / Embedding
        ↓
Transformer Encoder Layers
        ↓
Contextual Audio Representation
```

Self-attention allows the encoder to model relationships across the
audio representation.

## 10.2 Decoder

The decoder generates output tokens autoregressively.

At each generation step, the decoder considers:

-   previously generated tokens
-   encoded audio information

and predicts the next token.

Conceptually:

``` text
Audio Representation ─────┐
                          ↓
Previous Tokens → Decoder → Next Token
                          ↓
                    Repeat until
                    transcription ends
```

## 10.3 Tokens

The decoder does not directly generate an entire sentence in one
operation. It generates a sequence of tokens.

For example:

``` text
Audio
 ↓
Token 1
 ↓
Token 2
 ↓
Token 3
 ↓
...
 ↓
End
```

The resulting token sequence is decoded into human-readable text.

## 10.4 Multitask Nature

Whisper was trained to handle multiple speech-related tasks and supports
multilingual transcription and translation behavior.

Special tokens can provide information such as:

-   language
-   task
-   timestamps
-   other decoding/control information

This is particularly useful for multilingual applications.

------------------------------------------------------------------------

# 11. Whisper in This Project

The application's STT stage will conceptually operate as:

``` text
User Speech
     ↓
Browser Microphone
     ↓
MediaRecorder API
     ↓
Recorded Audio Blob
     ↓
FastAPI /api/transcribe
     ↓
Audio Preprocessing
     ↓
Whisper / faster-whisper
     ↓
Transcript
     ↓
Existing RAG Query
     ↓
LLM
     ↓
Answer
```

This separation is important:

-   STT converts speech to text.
-   RAG retrieves relevant knowledge.
-   The LLM generates the final response.

The STT component should not be responsible for answering the user's
question.

------------------------------------------------------------------------

# 12. Open-Source STT Alternatives

## 12.1 Whisper

Whisper is an end-to-end encoder-decoder Transformer ASR model.

### Strengths

-   Strong general-purpose transcription
-   Multilingual
-   Handles varied speech and accents reasonably well
-   Supports offline/local inference
-   Open-source model weights
-   Suitable for research and local deployment

### Limitations

-   Larger models require substantial compute
-   Standard implementations may have higher latency than optimized
    inference engines
-   Accuracy can vary by language, accent, recording quality, and
    code-switching
-   Real-time performance depends strongly on hardware and model size

Previous project evaluation showed strong English transcription but more
errors for Urdu, Punjabi, and Urdu-English mixed speech. Forced language
specification improved Urdu results. The evaluation also identified CPU
latency as a limitation for real-time use.

------------------------------------------------------------------------

## 12.2 faster-whisper

faster-whisper is an optimized implementation of Whisper inference based
on CTranslate2.

It is designed to provide faster and more memory-efficient inference
than the original Whisper implementation in many deployment scenarios.

### Strengths

-   Uses the Whisper model family
-   Optimized inference
-   Good choice for server-side deployment
-   Supports CPU and GPU execution
-   Can use quantization
-   Local/offline capable

### Limitations

-   Still requires model computation locally
-   Large models require significant memory
-   Actual speed depends on hardware, model size, precision, and
    workload

### Relevance to this application

Because the application requires a FastAPI server to process uploaded
recordings, faster-whisper is a strong candidate for the backend
inference layer.

------------------------------------------------------------------------

# 13. wav2vec2

wav2vec 2.0 is a self-supervised speech representation learning approach
commonly used with CTC-based ASR models.

A simplified pipeline is:

``` text
Raw Audio
   ↓
Feature Encoder
   ↓
Contextual Transformer
   ↓
CTC / Prediction Layer
   ↓
Text
```

### Strengths

-   Strong speech representation learning
-   Many language/domain-specific checkpoints exist
-   Efficient models are available
-   Suitable for custom ASR research

### Limitations

-   Model quality depends heavily on the selected checkpoint and
    language
-   Some checkpoints have limited language coverage
-   CTC decoding can provide less contextual generation behavior than
    encoder-decoder systems
-   Punctuation/capitalization may require additional processing
    depending on the model

In previous testing, wav2vec2 showed very fast transcription but lacked
some formatting and contextual advantages of Whisper.

------------------------------------------------------------------------

# 14. Vosk

Vosk is an offline speech recognition toolkit designed for lightweight
applications.

### Strengths

-   Offline
-   Lightweight
-   Works on relatively modest hardware
-   Suitable for embedded and edge applications
-   Streaming recognition support

### Limitations

-   Recognition quality depends strongly on the available model
-   Generally less capable than large modern Transformer ASR models for
    difficult multilingual/general-purpose speech
-   Model selection and language coverage are important

Vosk can be attractive when low resource usage is more important than
maximum recognition quality.

------------------------------------------------------------------------

# 15. Comparison of Open-Source Options

  -------------------------------------------------------------------------------------------
  Criterion      Whisper           faster-whisper         wav2vec2        Vosk
  -------------- ----------------- ---------------------- --------------- -------------------
  Architecture   Encoder-decoder   Optimized Whisper      Transformer +   Lightweight ASR
                 Transformer       inference              CTC-style ASR   toolkit

  Accuracy       Strong general    Similar Whisper model  Checkpoint      Generally lower for
                 performance       quality                dependent       difficult/general
                                                                          speech

  Latency        Moderate to high  Typically improved     Often fast      Low
                 depending on      inference efficiency                   
                 model/hardware                                           

  Offline        Yes               Yes                    Yes             Yes

  Multilingual   Strong            Strong, inherited from Depends on      Depends on model
                                   Whisper checkpoint     checkpoint      

  Hardware       Small to large    Flexible;              Model dependent Lightweight
                 depending on      CPU/GPU/quantization                   
                 model             options                                

  Best fit       General           Production/local       Custom/domain   Lightweight offline
                 multilingual ASR  Whisper deployment     ASR             ASR
  -------------------------------------------------------------------------------------------

The table should be interpreted as a deployment-level comparison rather
than a universal ranking. Actual accuracy and latency must be measured
on the application's own audio and hardware.

------------------------------------------------------------------------

# 16. Cloud / Paid STT Alternatives

Cloud STT services offer managed speech recognition through APIs.

The major alternatives considered are:

-   Deepgram
-   Google Cloud Speech-to-Text
-   Microsoft Azure Speech
-   AssemblyAI

These services generally require an internet connection and charge
according to usage and/or selected features.

------------------------------------------------------------------------

# 17. Deepgram

Deepgram provides cloud-based speech recognition APIs with an emphasis
on fast transcription and developer-oriented integration.

### Strengths

-   Cloud API
-   Low-latency use cases
-   Streaming capabilities
-   Production-oriented infrastructure
-   No local model management

### Limitations

-   Internet dependency
-   Usage-based cost
-   External service dependency
-   Audio/data leaves the local machine for processing according to the
    service's terms and configuration

------------------------------------------------------------------------

# 18. Google Cloud Speech-to-Text

Google Cloud Speech-to-Text provides managed speech recognition through
Google Cloud APIs.

### Strengths

-   Mature cloud platform
-   Broad language and feature support
-   Streaming and batch capabilities
-   Scalable infrastructure

### Limitations

-   Requires network access
-   Usage costs
-   Cloud/vendor dependency
-   Requires cloud credentials and configuration

------------------------------------------------------------------------

# 19. Microsoft Azure Speech

Azure Speech provides speech recognition through Microsoft's Azure cloud
platform.

### Strengths

-   Enterprise-oriented infrastructure
-   Speech recognition APIs
-   Streaming support
-   Broad language and customization capabilities

### Limitations

-   Internet required
-   Usage-based pricing
-   Azure account/configuration required
-   Vendor dependency

------------------------------------------------------------------------

# 20. AssemblyAI

AssemblyAI provides speech-to-text APIs and additional speech
intelligence features.

### Strengths

-   Developer-friendly API
-   Managed infrastructure
-   Transcription and additional speech processing capabilities
-   No local model deployment required

### Limitations

-   Internet dependency
-   Usage-based cost
-   External service dependency
-   Less control than hosting an open-source model locally

------------------------------------------------------------------------

# 21. Local vs Cloud STT

  ------------------------------------------------------------------------
  Criterion               Local                    Cloud STT
                          Whisper/faster-whisper   
  ----------------------- ------------------------ -----------------------
  Internet                Not required after model Required
                          setup                    

  Per-request API cost    No third-party STT fee   Usually usage-based

  Model control           High                     Lower

  Privacy/control         High when processed      Depends on provider and
                          locally                  configuration

  Deployment effort       Higher                   Lower initially

  Scaling                 Managed by application   Provider-managed
                          owner                    

  Hardware                Application owner        Provider provides
                          provides compute         compute

  Vendor lock-in          Low                      Higher

  Offline operation       Yes                      No

  Custom deployment       High                     Service-dependent
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# 22. Accuracy Considerations

Accuracy should not be treated as a single universal property.

It depends on:

-   Language
-   Accent
-   Dialect
-   Background noise
-   Microphone quality
-   Speaking speed
-   Domain vocabulary
-   Code-switching
-   Audio duration
-   Model size
-   Decoding configuration

For this application, multilingual and potentially mixed-language speech
are especially important.

A model that performs extremely well on English may not provide the same
word-level accuracy for Urdu, Punjabi, or mixed Urdu-English speech.

Therefore, the project should evaluate STT on representative application
audio rather than selecting a model only from generic benchmark claims.

------------------------------------------------------------------------

# 23. Latency Considerations

Latency consists of more than model inference time.

For a browser-to-backend STT request:

``` text
Recording Time
     +
Upload Time
     +
Audio Decode Time
     +
Preprocessing
     +
Model Inference
     +
Postprocessing
     =
User-perceived STT latency
```

For a recorded-audio workflow, transcription cannot begin until enough
audio has been captured and submitted.

For real-time streaming, the architecture would be different and would
require streaming audio transport and incremental transcription.

The current task specifies browser recording followed by sending the
recorded blob to the backend, so the initial implementation should use a
request/response transcription workflow.

------------------------------------------------------------------------

# 24. Cost Considerations

### Local open-source model

The application does not pay a per-minute third-party STT API charge,
but it must provide compute resources.

Costs can include:

-   GPU/CPU hardware
-   electricity
-   hosting
-   storage
-   maintenance

### Cloud STT

Cloud services typically reduce infrastructure management but introduce:

-   usage charges
-   API/service dependency
-   network requirements

For a development and research project, local inference can provide
greater control and reproducibility.

------------------------------------------------------------------------

# 25. Offline Capability

Offline capability means the application can perform speech recognition
without sending audio to an external cloud service.

### Local options

-   Whisper
-   faster-whisper
-   wav2vec2
-   Vosk

can be deployed locally, subject to model and hardware requirements.

### Cloud options

-   Deepgram
-   Google Speech-to-Text
-   Azure Speech
-   AssemblyAI

depend on network connectivity to their services.

For applications involving sensitive or private audio, local processing
can also provide stronger control over where the audio is processed.

------------------------------------------------------------------------

# 26. Recommended Architecture for This Project

The preferred architecture is:

``` text
                  FRONTEND
┌──────────────────────────────────────────┐
│ React                                     │
│                                          │
│ Text Mode       Voice Mode               │
│    │                │                    │
│    │          MediaRecorder               │
│    │                │                    │
│    │           Audio Blob                 │
└────┼────────────────┼────────────────────┘
     │                │
     │                │ POST /api/transcribe
     │                ↓
     │          ┌───────────────┐
     │          │ FastAPI       │
     │          │ STT Endpoint  │
     │          └───────┬───────┘
     │                  ↓
     │          faster-whisper
     │                  ↓
     │             Transcript
     │                  │
     └──────────────────┤
                        ↓
                 RAG Query Flow
                        ↓
                    Retriever
                        ↓
                 Relevant Context
                        ↓
                       LLM
                        ↓
                 Final Response
                        ↓
                     React UI
```

------------------------------------------------------------------------

# 27. Why Server-Side STT?

The STT model should run on the FastAPI backend rather than directly
inside the browser.

Reasons:

1.  Large ASR models are not ideal for browser execution.
2.  Backend hardware can provide GPU acceleration.
3.  The model can be loaded once at server startup.
4.  Model inference logic remains centralized.
5.  The React application remains lightweight.
6.  The same API can later support different frontend clients.
7.  The existing RAG and LLM pipeline already belongs on the backend.

The backend should therefore expose a dedicated transcription endpoint.

------------------------------------------------------------------------

# 28. Proposed API Contract

The next implementation task will introduce:

``` http
POST /api/transcribe
```

### Request

A multipart/form-data request containing the recorded audio file.

Conceptually:

``` text
POST /api/transcribe

Content-Type: multipart/form-data

audio = <recorded audio blob>
```

### Response

A successful response should contain the transcript in a predictable
JSON structure, for example:

``` json
{
  "text": "What is machine learning?"
}
```

The exact response structure should remain consistent with the frontend
implementation.

------------------------------------------------------------------------

# 29. Integration with RAG

The STT output should become the same text input used by the existing
RAG pipeline.

``` text
Voice
 ↓
STT
 ↓
"What is machine learning?"
 ↓
Existing RAG Query
 ↓
Retrieval
 ↓
Context
 ↓
LLM
 ↓
Answer
```

This is preferable to creating a separate voice-specific RAG
implementation.

The principle is:

> Voice input changes how the query enters the system; it should not
> change how the RAG system processes the resulting text.

This keeps the architecture modular.

------------------------------------------------------------------------

# 30. Known Project-Specific STT Findings

Previous project evaluation of Whisper-small identified:

-   Strong performance on clear English speech
-   Good handling of technical vocabulary
-   Good handling of numbers and dates
-   Reduced accuracy for Urdu
-   Difficulties with Punjabi/regional dialects
-   Errors with Urdu-English code-switching
-   Automatic language detection can confuse Urdu and Hindi
-   Explicit Urdu language selection improved transcription
-   CPU inference can create high latency for real-time scenarios

These findings should guide testing and should not be presented as
universal benchmark results.

------------------------------------------------------------------------

# 31. Selection Rationale

For the current application, the recommended implementation direction is
**Whisper-family local inference, preferably using faster-whisper for
the backend inference layer if its measured behavior on the target
hardware is satisfactory**.

The rationale is:

1.  The project already has Whisper experience and evaluation.
2.  Whisper provides multilingual ASR.
3.  Local inference supports offline operation.
4.  It avoids third-party per-request STT charges.
5.  Server-side inference fits the FastAPI architecture.
6.  faster-whisper provides an optimized path for practical deployment.
7.  The architecture keeps STT independent from the existing RAG
    pipeline.

The final choice should be validated through actual latency and
transcription tests on the application's target environment.

------------------------------------------------------------------------

# 32. Limitations of the Comparison

The comparison in this document is architectural and
deployment-oriented.

It should not be interpreted as a claim that one model is universally
more accurate than every other model.

A rigorous benchmark would require:

-   The same audio dataset
-   The same languages
-   Multiple speakers
-   Multiple accents/dialects
-   Noise conditions
-   Standardized hardware
-   Multiple inference runs
-   Word Error Rate (WER)
-   Character Error Rate (CER), where appropriate
-   Latency measurements
-   Resource utilization measurements
-   Cloud pricing measured against a defined usage volume

This project can use representative application-level tests before
finalizing the deployment configuration.

------------------------------------------------------------------------

# 33. Conclusion

The STT component is responsible for converting spoken language into a
text query. In the proposed application, the browser captures speech,
the FastAPI backend performs server-side transcription, and the
resulting text is passed into the existing RAG pipeline.

Whisper uses a log-Mel spectrogram followed by an encoder-decoder
Transformer architecture rather than a traditional separated
acoustic-model/language-model pipeline.

Among local alternatives, Whisper/faster-whisper provides a strong
combination of multilingual capability, model quality, and offline
operation. wav2vec2 can be attractive for specialized or lightweight
ASR, while Vosk is appropriate for resource-constrained offline
applications.

Cloud services such as Deepgram, Google Speech-to-Text, Azure Speech,
and AssemblyAI can provide convenient managed infrastructure and
scalable APIs, but they require network access and introduce usage costs
and external service dependency.

For this project, local server-side Whisper-family inference is the most
suitable starting point. The next implementation stage is to build
browser audio capture with the MediaRecorder API and connect it to a
dedicated FastAPI `/api/transcribe` endpoint.

------------------------------------------------------------------------

## 34. References

1.  Radford, A. et al. (2022). *Robust Speech Recognition via
    Large-Scale Weak Supervision*. OpenAI.
2.  Baevski, A. et al. (2020). *wav2vec 2.0: A Framework for
    Self-Supervised Learning of Speech Representations*. arXiv.
3.  CTranslate2 documentation and faster-whisper project documentation.
4.  Vosk speech recognition toolkit documentation.
5.  Official documentation for Deepgram Speech-to-Text.
6.  Official Google Cloud Speech-to-Text documentation.
7.  Official Microsoft Azure Speech documentation.
8.  Official AssemblyAI documentation.
