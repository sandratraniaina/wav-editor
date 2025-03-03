# wav_writer.py
import struct
import numpy as np

def write_wav_file(file_path, header, audio_data):
    """
    Manually write a WAV file using NumPy for audio data.
    """
    with open(file_path, 'wb') as file:
        # Write RIFF header
        file.write(header['chunk_id'])
        file.write(struct.pack('<I', header['chunk_size']))
        file.write(header['format'])
        
        # Write fmt subchunk
        file.write(header['fmt_chunk_id'])
        file.write(struct.pack('<I', header['fmt_chunk_size']))
        file.write(struct.pack('<H', header['audio_format']))
        file.write(struct.pack('<H', header['num_channels']))
        file.write(struct.pack('<I', header['sample_rate']))
        file.write(struct.pack('<I', header['byte_rate']))
        file.write(struct.pack('<H', header['block_align']))
        file.write(struct.pack('<H', header['bits_per_sample']))
        
        # Write data subchunk header
        file.write(header['data_chunk_id'])
        file.write(struct.pack('<I', header['data_size']))
        
        # Write audio data with NumPy
        bits_per_sample = header['bits_per_sample']
        audio_array = np.array(audio_data, dtype={
            8: np.uint8,   # 8-bit unsigned (after conversion)
            16: np.int16,  # 16-bit signed
            32: np.int32,  # 32-bit signed
            24: np.int32   # 24-bit stored as int32, truncated later
        }[bits_per_sample])
        
        if bits_per_sample == 8:
            # Convert signed to unsigned
            audio_array = audio_array + 128
            file.write(audio_array.tobytes())
        elif bits_per_sample in (16, 32):
            file.write(audio_array.tobytes())
        elif bits_per_sample == 24:
            # Write 24-bit data (3 bytes per sample)
            for sample in audio_array:
                file.write(sample.to_bytes(3, byteorder='little', signed=True))
        else:
            raise ValueError(f"Unsupported bits_per_sample: {bits_per_sample}")