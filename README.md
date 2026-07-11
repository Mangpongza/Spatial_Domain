# Spatial Domain Steganography

A modern desktop application for Audio-in-Video Steganography using Spatial Domain techniques with automatic algorithm detection.

## Features

- **10 Steganography Algorithms**: Standard LSB (1/2/3-bit), Random LSB, Adaptive LSB, Edge-based LSB, LSBM, LSBMR, PVD, BPCS, OPAP, PIT
- **Automatic Algorithm Detection**: Tries all algorithms during extraction, validates via CRC32 checksum
- **Audio Support**: WAV and MP3 embedding into MP4, MKV, AVI, MOV videos
- **Analysis**: PSNR, SSIM, MSE, BER, histogram comparison, noise maps
- **Benchmarking**: Compare all algorithms on speed, PSNR, SSIM, BER, capacity
- **Modern UI**: Dark theme, Material Design, sidebar navigation, drag & drop, real-time logging

## Installation

```bash
pip install -r requirements.txt
```

Requirements: Python 3.12+, PyQt6, OpenCV, NumPy, Pillow, scikit-image, matplotlib, FFmpeg

## Usage

```bash
python main.py
```

## Project Structure

```
main.py                    # Entry point
algorithms/                # 10 steganography algorithm classes
analysis/                  # PSNR, SSIM, MSE metrics
benchmark/                 # Algorithm comparison suite
models/                    # Video, Audio, Stego data models
services/                  # Video/Audio processing, embedding, extraction
ui/                        # PyQt6 UI components and pages
  components/              # Reusable widgets (log console, preview, drag-drop)
  pages/                   # Dashboard, Embed, Extract, Analysis, Benchmark pages
  styles/                  # Dark theme stylesheet
utils/                     # Header builder, CRC32, constants, logging
controllers/               # MVC controller
```

## Building Executable

```bash
pyinstaller --onefile --windowed --name "SpatialDomain" main.py
```
