# Speech-to-Text: Pipeline, Whisper Architecture, and Engine Comparison

This note documents the research behind the voice-input feature: how a generic
STT pipeline works, how Whisper (used here via `faster-whisper`) differs from
that classic pipeline, and how it stacks up against other open-source and
paid/cloud STT engines on accuracy, latency, cost, and offline capability.

## 1. The classic STT pipeline

```
raw audio → mel-spectrogram / MFCC → acoustic model → decoder → text
```

- **Raw audio** — a waveform sampled at some rate (commonly 16 kHz for speech
  models). This is just amplitude over time and is too high-dimensional and
  noisy for a model to map directly to words.
- **Mel-spectrogram / MFCC** — the waveform is chopped into short overlapping
  frames (e.g. 25 ms windows every 10 ms) and converted to the frequency
  domain (STFT), then warped onto the mel scale, which approximates how the
  human ear perceives pitch. MFCCs go a step further and apply a discrete
  cosine transform to decorrelate the mel bands into a compact set of
  coefficients. This turns "sound" into a 2D time-by-frequency feature map
  that emphasizes the parts of the signal that carry phonetic information.
- **Acoustic model** — historically a GMM-HMM, later a DNN/RNN, and now a
  transformer or conformer — maps the spectrogram frames to phoneme or
  sub-word probabilities.
- **Decoder** — combines the acoustic model's output with a language model
  and a lexicon (classically via a WFST or beam search) to produce the most
  probable sequence of words, resolving ambiguities like "recognize speech"
  vs. "wreck a nice beach."

Classic pipelines (e.g. Kaldi, and Vosk which is built on Kaldi) keep these
stages as separate, independently-trained components: an acoustic model, a
pronunciation lexicon, and an n-gram or small neural language model, glued
together by a WFST decoder.

## 2. Whisper's architecture

Whisper (OpenAI) collapses the pipeline into a single **encoder-decoder
transformer**, trained end-to-end on 680k hours of weakly-labeled, multilingual
web audio:

- **Front end**: audio is resampled to 16 kHz and converted to an 80-channel
  log-mel spectrogram over 30-second windows — this is the only
  "classic pipeline" step Whisper keeps.
- **Encoder**: a stack of transformer blocks (with a couple of initial conv
  layers) turns the spectrogram into a sequence of contextual audio
  embeddings. This replaces the separate acoustic model.
- **Decoder**: an autoregressive transformer decoder cross-attends to the
  encoder output and generates text tokens directly (a byte-pair encoding
  vocabulary), conditioned on special task tokens (language ID, `transcribe`
  vs `translate`, timestamps). This replaces the separate language model +
  WFST decoder — Whisper has an implicit language model baked into the
  decoder weights instead of a bolt-on n-gram model.
- Because it was trained on such a large, diverse, weakly-supervised dataset
  (lots of real-world noise, accents, and multiple languages), Whisper
  generalizes well without needing per-domain acoustic adaptation, at the
  cost of being a much bigger model than a traditional pipeline component.

`faster-whisper` (used in this project's `speech/transcription.py`) is a
re-implementation of Whisper's inference on top of CTranslate2. Same weights
and architecture, but int8/float16 quantization and a faster runtime — roughly
4x faster and using less memory than the reference `openai-whisper` package on
CPU, which is why it's the practical choice for a self-hosted `/api/transcribe`
endpoint.

## 3. Comparison

### Open-source options

| Engine | Architecture | Accuracy | Latency (CPU) | Offline | Notes |
|---|---|---|---|---|---|
| **faster-whisper** (this project) | Whisper encoder-decoder transformer, CTranslate2 runtime | High, best-in-class on noisy/accented/multilingual audio | Moderate — `base`/`small` run near real-time on CPU with int8; `large-v3` needs a GPU for real-time | Yes, fully | Easiest accuracy-per-effort trade-off; large model sizes (up to ~3 GB for `large-v3`) |
| **openai-whisper** (reference impl.) | Same as above, PyTorch | Same as faster-whisper | Slower — no quantized runtime, higher memory | Yes | Same model, worse inference engine; superseded by faster-whisper/whisper.cpp for production |
| **wav2vec2** (Meta/HF) | Encoder-only transformer, CTC decoding (self-supervised pretraining, fine-tuned per language) | Good on clean, in-domain audio; weaker than Whisper on noisy/accented/out-of-domain audio | Fast — smaller models, CTC decoding is cheap | Yes | Needs a language-specific fine-tuned checkpoint; no built-in punctuation/casing without extra post-processing |
| **Vosk** | Classic Kaldi-style pipeline (DNN acoustic model + WFST decoder + n-gram LM) | Lower than Whisper, especially on accents/noise; decent on clean read speech | Very fast, low memory — designed for embedded/edge devices | Yes | Small footprint (tens of MB per language model), good for resource-constrained or streaming use cases; not this project's need |

### Paid / cloud APIs

| Service | Accuracy | Latency | Cost (approx., pay-as-you-go) | Offline |
|---|---|---|---|---|
| **Deepgram** | High, tuned for streaming/real-time and telephony audio | Very low — built for live streaming | ~$0.0043–0.0059/min (Nova-tier models) | No |
| **Google Speech-to-Text** | High, strong multilingual coverage | Low, especially for streaming API | ~$0.016/min standard (varies by model/tier) | No (on-prem/edge variants exist but are a separate, enterprise product) |
| **Azure Speech** | High, strong for enterprise/telephony scenarios | Low | ~$1/audio hour on the pay-as-you-go tier (~$0.0167/min) | No |
| **AssemblyAI** | High, plus built-in extras (summarization, sentiment, PII redaction) | Low-moderate; async and streaming both available | ~$0.12–0.15/hour depending on model/tier | No |

*(Cloud pricing changes frequently — treat these as directional, not quoted
guarantees; check each vendor's current pricing page before budgeting.)*

## 4. Why faster-whisper for this project

- **Offline / self-hosted**: the RAG backend already runs entirely
  locally (FAISS, local embeddings); adding a cloud STT dependency would
  introduce a new network dependency, API key, and per-minute cost for what
  is otherwise a fully offline-capable app.
- **Accuracy**: Whisper's accuracy is competitive with or better than the
  cloud options on this project's likely audio (spoken questions recorded
  from a laptop mic, possibly with background noise or accented English),
  and clearly ahead of Vosk and stock wav2vec2 in that setting.
- **Latency is acceptable for this use case**: this is a "record a short
  question, then transcribe" flow, not live captioning, so faster-whisper's
  near-real-time (not sub-second-streaming) latency on CPU with the `base`
  model is an acceptable trade-off. If this became a live-dictation feature,
  Deepgram or Vosk (streaming, very low latency) would be worth
  reconsidering.
- **Cost**: zero marginal cost per request beyond the server's own compute,
  versus a per-minute bill on every cloud option.

The trade-off accepted: no cloud-grade streaming, and larger Whisper models
need a GPU to feel instant. For this project's "record → transcribe → fill
the chat input" flow, that trade-off favors faster-whisper on CPU with the
`base` model, matching what `speech/transcription.py` already ships with.
