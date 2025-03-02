import math
import struct
import os
import argparse

def generate_test_audio(filename="input.wav", duration=5, sample_rate=44100):
    """
    Generate a test WAV audio file with a mixture of tones using only built-in Python libraries.
    
    Parameters:
    - filename: output filename (default: "test_audio.wav")
    - duration: length of audio in seconds (default: 5)
    - sample_rate: sample rate in Hz (default: 44100)
    """
    # Calculate number of frames
    num_frames = int(duration * sample_rate)
    
    # WAV file header constants
    WAVE_FORMAT_PCM = 0x0001
    
    # Open file for binary writing
    with open(filename, 'wb') as wav_file:
        # Write the WAV header manually
        # ------------------------
        # RIFF header
        wav_file.write(b'RIFF')
        # Size placeholder (will be filled later)
        wav_file.write(struct.pack('<I', 0))
        wav_file.write(b'WAVE')
        
        # Format chunk
        wav_file.write(b'fmt ')
        wav_file.write(struct.pack('<I', 16))  # Chunk size (16 for PCM)
        wav_file.write(struct.pack('<H', WAVE_FORMAT_PCM))  # Format (1 for PCM)
        wav_file.write(struct.pack('<H', 1))  # Channels (1 for mono)
        wav_file.write(struct.pack('<I', sample_rate))  # Sample rate
        wav_file.write(struct.pack('<I', sample_rate * 2))  # Byte rate (SampleRate * NumChannels * BitsPerSample/8)
        wav_file.write(struct.pack('<H', 2))  # Block align (NumChannels * BitsPerSample/8)
        wav_file.write(struct.pack('<H', 16))  # Bits per sample
        
        # Data chunk header
        wav_file.write(b'data')
        wav_file.write(struct.pack('<I', num_frames * 2))  # Chunk size (NumFrames * NumChannels * BitsPerSample/8)
        
        # Generate audio data manually
        max_amplitude = 0
        audio_data = []
        
        # Generate raw audio data (without any normalization yet)
        for i in range(num_frames):
            t = i / sample_rate
            
            # Generate a combination of sine waves at different frequencies
            # 440 Hz (A4 note)
            tone1 = 0.5 * math.sin(2 * math.pi * 440 * t)
            # 523.25 Hz (C5 note)
            tone2 = 0.3 * math.sin(2 * math.pi * 523.25 * t)
            # 659.25 Hz (E5 note)
            tone3 = 0.2 * math.sin(2 * math.pi * 659.25 * t)
            
            # Combine tones
            sample = tone1 + tone2 + tone3
            
            # Apply fade in
            fade_duration = min(0.1 * duration, 0.5)  # 10% of total duration or 0.5s
            fade_samples = int(fade_duration * sample_rate)
            if i < fade_samples:
                sample *= (i / fade_samples)
            
            # Apply fade out
            if i >= num_frames - fade_samples:
                sample *= (num_frames - i) / fade_samples
            
            audio_data.append(sample)
            # Track maximum amplitude for normalization
            max_amplitude = max(max_amplitude, abs(sample))
        
        # Normalize and write the audio data
        scaling_factor = 32000 / max_amplitude * 0.9  # Scale to 90% of max to avoid clipping
        
        for sample in audio_data:
            # Scale, convert to 16-bit integer, and write
            sample_16bit = int(sample * scaling_factor)
            wav_file.write(struct.pack('<h', sample_16bit))
        
        # Go back and update the file size in the header
        file_size = wav_file.tell()
        wav_file.seek(4)
        wav_file.write(struct.pack('<I', file_size - 8))  # File size - 8 bytes for RIFF and size field
    
    print(f"Successfully created {filename}")
    print(f"Duration: {duration} seconds")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"File size: {os.path.getsize(filename)/1024:.2f} KB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a test WAV audio file")
    parser.add_argument("--filename", default="input.wav", help="Output filename")
    parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    parser.add_argument("--sample_rate", type=int, default=44100, help="Sample rate in Hz")
    
    args = parser.parse_args()
    
    generate_test_audio(args.filename, args.duration, args.sample_rate)