# 🎭 MuseTalk 1.5 — AI Talking Avatar

> **Audio-Driven Lip Synchronization using MuseTalk 1.5**

MuseTalk 1.5 is an AI-powered lip-sync system that generates a talking avatar from a **single face image and an audio file**. The system analyzes the input speech and synchronizes the avatar's mouth movements with the audio to produce a realistic talking-head video.

This project is implemented using **MuseTalk 1.5** and configured to run in a Python 3.10 environment with GPU acceleration.

---

## ✨ Features

* 🎭 Generate a talking avatar from a **single image**
* 🎙️ Synchronize facial movements with speech audio
* 🤖 Powered by **MuseTalk 1.5**
* 🗣️ Supports audio-driven lip synchronization
* ⚡ GPU-accelerated inference
* 🎬 Automatically generates an MP4 video
* 🔊 Combines generated video with the original audio
* 🖼️ Supports image-based avatar input
* 📁 Organized input and output directories

---

## 🧠 How It Works

The system follows this pipeline:

```text
                ┌─────────────────────┐
                │    Avatar Image     │
                │       PNG/JPG       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Face Detection    │
                │      DWPose         │
                └──────────┬──────────┘
                           │
                           │
┌──────────────────┐       ▼
│   Audio Input    │ ──► Whisper Audio
│   MP3 / WAV      │       Features
└──────────────────┘          │
                              ▼
                    ┌──────────────────┐
                    │  MuseTalk 1.5    │
                    │   UNet Model     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Generated Frames │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      FFmpeg      │
                    │ Video + Audio    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Talking Avatar  │
                    │       MP4        │
                    └──────────────────┘
```

MuseTalk uses a frozen **Whisper-tiny** model to encode audio and operates in the latent space of an `ft-mse-vae`. MuseTalk is an audio-driven inpainting system rather than a conventional diffusion model.

---

# 📂 Project Structure

```text
MuseTalk/
│
├── configs/
│   └── inference/
│       └── test.yaml
│
├── inputs/
│   ├── avatar/
│   │   └── avatar.png
│   │
│   └── audio/
│       └── speech.mp3
│
├── models/
│   ├── musetalkV15/
│   │   ├── musetalk.json
│   │   └── unet.pth
│   │
│   ├── dwpose/
│   │   └── dw-ll_ucoco_384.pth
│   │
│   ├── face-parse-bisent/
│   │   ├── 79999_iter.pth
│   │   └── resnet18-5c106cde.pth
│   │
│   ├── sd-vae/
│   │   ├── config.json
│   │   └── diffusion_pytorch_model.bin
│   │
│   └── whisper/
│       ├── config.json
│       ├── pytorch_model.bin
│       └── preprocessor_config.json
│
├── output/
│   └── talking_avatar.mp4
│
├── results/
│   └── v15/
│
├── musetalk/
├── scripts/
├── requirements.txt
├── inference.sh
└── README.md
```

---

# 🛠️ Requirements

Recommended environment:

| Component   | Version |
| ----------- | ------- |
| Python      | 3.10    |
| PyTorch     | 2.0.1   |
| TorchVision | 0.15.2  |
| TorchAudio  | 2.0.2   |
| CUDA        | 11.8    |
| MMCV        | 2.0.1   |
| MMDetection | 3.1.0   |
| MMPose      | 1.1.0   |
| MuseTalk    | 1.5     |

These versions align with the environment recommended by the MuseTalk project.

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk
```

## 2. Create Python Environment

```bash
python3.10 -m venv musetalk_env
source musetalk_env/bin/activate
```

On Windows:

```bash
musetalk_env\Scripts\activate
```

---

## 3. Install PyTorch

For CUDA 11.8:

```bash
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 \
--index-url https://download.pytorch.org/whl/cu118
```

---

## 4. Install MuseTalk Dependencies

```bash
pip install -r requirements.txt
```

Install the MMLab packages:

```bash
pip install --no-cache-dir -U openmim

mim install mmengine
mim install "mmcv==2.0.1"
mim install "mmdet==3.1.0"
mim install "mmpose==1.1.0"
```

The MuseTalk documentation specifies these MMLab versions for the supported environment.

---

# 📦 Model Files

MuseTalk 1.5 requires several pretrained models.

The important model components are:

### MuseTalk 1.5

```text
models/musetalkV15/
├── musetalk.json
└── unet.pth
```

### DWPose

```text
models/dwpose/
└── dw-ll_ucoco_384.pth
```

### SD VAE

```text
models/sd-vae/
├── config.json
└── diffusion_pytorch_model.bin
```

### Whisper

```text
models/whisper/
├── config.json
├── pytorch_model.bin
└── preprocessor_config.json
```

The official MuseTalk repository documents the same v1.5 model structure and dependencies.

> **Important:** Model files must be downloaded completely. Empty or incomplete model files will cause inference errors.

---

# 🖼️ Add Your Avatar

Place your face image inside:

```text
inputs/avatar/
```

Example:

```text
inputs/avatar/1000297286.png
```

MuseTalk supports an image file as the `video_path` input in the inference configuration.

---

# 🎙️ Add Your Audio

Place your audio inside:

```text
inputs/audio/
```

Example:

```text
inputs/audio/tts_input.mp3
```

---

# ⚙️ Configure Inference

Edit:

```text
configs/inference/test.yaml
```

Example:

```yaml
task_1:
    video_path: avatar_path
    audio_path: audio_path
```

The configuration specifies the avatar input and audio input used during inference.

---

# ▶️ Run MuseTalk 1.5

Activate the environment:

```bash
source /content/musetalk_env/bin/activate
```

Move to the project:

```bash
cd /content/MuseTalk
```

Run:

```bash
MPLBACKEND=Agg python -m scripts.inference \
    --inference_config configs/inference/test.yaml \
    --result_dir results \
    --unet_model_path models/musetalkV15/unet.pth \
    --unet_config models/musetalkV15/musetalk.json \
    --version v15
```

The official inference configuration for MuseTalk 1.5 uses `musetalkV15/unet.pth`, `musetalkV15/musetalk.json`, and version `v15`.

---

# 🎬 Output

After successful inference, the generated video will be available under:

```text
results/v15/
```

For example:

```text
results/v15/1000297286_tts_input.mp4
```

The final video can then be copied to the project's output directory:

```text
output/talking_avatar.mp4
```

---

# 📁 Final Output

```text
output/
└── talking_avatar.mp4
```

The resulting MP4 contains:

* 👤 Avatar face
* 👄 Lip movements synchronized with speech
* 🔊 Original audio
* 🎬 Final rendered video

---

# ⚡ Performance

MuseTalk is designed as a real-time/high-performance lip-sync system. The project reports 30+ FPS performance on an NVIDIA Tesla V100 under suitable conditions. Actual speed depends on GPU, video resolution, input type, and configuration.

---

# 🐛 Troubleshooting

### `JSONDecodeError`

Example:

```text
JSONDecodeError: Expecting value
```

Usually means a required JSON model file is empty or corrupted.

Check:

```bash
ls -lh models/musetalkV15/musetalk.json
```

The file should not be `0 bytes`.

---

### `Ran out of input`

Example:

```text
EOFError: Ran out of input
```

This commonly indicates an incomplete/corrupted PyTorch model file.

Check:

```bash
ls -lh models/dwpose/dw-ll_ucoco_384.pth
```

---

### Whisper Error

Example:

```text
OSError: It looks like the config file...
```

Check:

```text
models/whisper/
├── config.json
├── pytorch_model.bin
└── preprocessor_config.json
```

None of these files should be empty.

---

### Matplotlib Backend Error

If Colab reports a backend error involving:

```text
matplotlib_inline
```

use:

```bash
MPLBACKEND=Agg
```

before the inference command.

---

### FFmpeg Error

Check FFmpeg:

```bash
ffmpeg -version
```

MuseTalk requires FFmpeg for video generation and audio/video combination.

---

# 🔒 Input & Output

### Input

```text
Avatar Image → PNG/JPG
Audio → MP3/WAV
```

### Output

```text
Talking Avatar → MP4
```

---

# 🎯 Example

Input:

```text
inputs/avatar/1000297286.png
inputs/audio/tts_input.mp3
```

Processing:

```text
Avatar Image
      +
Speech Audio
      ↓
   MuseTalk 1.5
      ↓
Lip-Synchronized Frames
      ↓
     FFmpeg
      ↓
talking_avatar.mp4
```

---

# 🌟 Project Goal

The goal of this project is to demonstrate how **AI-based audio-driven facial animation** can transform a static face image into a talking avatar whose lip movements are synchronized with speech.

This project can be extended for:

* 🧑‍🏫 AI teachers
* 🗣️ Virtual assistants
* 📚 Educational content
* 🎥 Digital presenters
* 🌐 Multilingual avatars
* 🎭 Virtual characters
* 💬 AI-generated video content

---

# 📚 Technology Stack

* **Python 3.10**
* **PyTorch**
* **MuseTalk 1.5**
* **Whisper-tiny**
* **DWPose**
* **MMPose**
* **MMDetection**
* **MMCV**
* **Diffusers**
* **OpenCV**
* **FFmpeg**
* **CUDA**

---

# 🙏 Credits

This project is based on **MuseTalk**, developed by the Lyra Lab / Tencent Music Entertainment team.

Original project:

[MuseTalk on GitHub](https://github.com/TMElyralab/MuseTalk?utm_source=chatgpt.com)

Please refer to the original repository for the official model licenses, technical report, updates, and full documentation.

---

# ⚠️ Disclaimer

This project is intended for research, education, and responsible creative use.

When generating or publishing AI-generated videos of real people, obtain appropriate permission and clearly disclose synthetic/manipulated media where appropriate.

---

## ⭐ Summary

**MuseTalk 1.5 converts:**

```text
🖼️ Image + 🎙️ Audio
        ↓
   🤖 AI Processing
        ↓
🎬 Talking Avatar Video
```

**Status: ✅ Working**
