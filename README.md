# Wav Editor

A Python-based WAV audio processing tool that provides various audio manipulation capabilities with a focus on noise reduction and audio quality improvement.

## Features

- **Audio File Support**

  - Reads and writes WAV files (8-bit, 16-bit, 24-bit, and 32-bit)
  - Preserves original audio metadata
  - Handles mono audio files
- **Audio Processing**

  - **Amplification**: Adjust audio volume with clipping protection
  - **Normalization**: Optimize audio levels to use full dynamic range
  - **Anti-Distortion**: Apply soft clipping using tanh-like function
  - **Noise Removal**: Remove background noise using spectral subtraction
- **Visualization**

  - Side-by-side waveform comparison of original and processed audio
  - Visual feedback for audio modifications

## Installation

```bash
git clone https://github.com/sandratraniaina/wav-editor.git
cd wav-editor
```

## Dependencies

- NumPy: For efficient audio data processing
- Matplotlib: For audio visualization

Install dependencies:

```bash
pip install numpy matplotlib
```

## Usage

### Command Line Interface

```bash
python -m wav_editor.core.main input.wav output.wav [options]
```

### Options

```
Processing Options:
  --amplify FACTOR     Amplification factor (e.g., 1.5 for 50% louder)
  --normalize          Normalize audio to use full dynamic range
  --anti-distort VAL   Apply amplification with anti-distortion (e.g., 2.0)

Noise Removal Options:
  --noise-pattern FILE WAV file containing noise pattern to remove
  --noise-method TYPE  Noise removal method (default: spectral_subtraction)
  --alpha FLOAT       Oversubtraction factor (default: 2.0)
  --beta FLOAT        Spectral floor (default: 0.01)

Advanced Options:
  --smoothing FLOAT   Smoothing factor for anti-distortion (0.0-1.0)
  --fft-size INT     FFT size for spectral processing
  --hop-size INT     Hop size for spectral processing

Visualization:
  --plot             Generate waveform plot of original vs processed audio
```

### Examples

1. Basic amplification:

```bash
python -m wav_editor.core.main input.wav output.wav --amplify 1.5
```

2. Noise removal:

```bash
python -m wav_editor.core.main input.wav output.wav --noise-pattern noise.wav --alpha 2.0
```

3. Anti-distortion with normalization:

```bash
python -m wav_editor.core.main input.wav output.wav --anti-distort 2.0 --normalize
```

## Project Structure

```
wav-editor/
├── src/
│   └── wav-editor/
│       ├── core/
│       │   ├── main.py           # CLI implementation
│       │   └── wav_processors.py # Audio processing logic
│       └── utils/
│           ├── wav_reader.py     # WAV file reading
│           ├── wav_writer.py     # WAV file writing
│           ├── wav_utils.py      # Utility functions
│           └── plotter.py        # Visualization tools
├── test/
│   └── test_data/               # Test audio files
└── docs/                        # Documentation
```

## Advanced Usage

### Custom Audio Processing Chain

You can chain multiple processing steps:

```python
from wav_editor.core.wav_processors import AudioProcessor
from wav_editor.utils.wav_reader import read_wav_file
from wav_editor.utils.wav_writer import write_wav_file

# Read audio
header, audio_data = read_wav_file("input.wav")

# Initialize processor
processor = AudioProcessor().load_data(header, audio_data)

# Apply processing chain
processed = processor.normalize()
processed = processor.anti_distortion(threshold=0.8)
processed = processor.amplify(1.2)

# Write result
write_wav_file("output.wav", header, processed)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
