# wav_reader.py
import struct

def read_wav_header(file):
    """Read and validate the WAV file header."""
    # Read RIFF header
    riff_chunk_id = file.read(4)
    if riff_chunk_id != b'RIFF':
        raise ValueError("Not a valid WAV file: RIFF header missing")
    
    chunk_size = struct.unpack('<I', file.read(4))[0]
    
    format_id = file.read(4)
    if format_id != b'WAVE':
        raise ValueError("Not a valid WAV file: WAVE format missing")
    
    return riff_chunk_id, chunk_size, format_id

def read_fmt_chunk(file):
    """Read the format chunk of the WAV file."""
    fmt_chunk_id = file.read(4)
    if fmt_chunk_id != b'fmt ':
        raise ValueError("Not a valid WAV file: fmt subchunk missing")
    
    fmt_chunk_size = struct.unpack('<I', file.read(4))[0]
    audio_format = struct.unpack('<H', file.read(2))[0]
    num_channels = struct.unpack('<H', file.read(2))[0]
    sample_rate = struct.unpack('<I', file.read(4))[0]
    byte_rate = struct.unpack('<I', file.read(4))[0]
    block_align = struct.unpack('<H', file.read(2))[0]
    bits_per_sample = struct.unpack('<H', file.read(2))[0]
    
    # Skip any extra fmt bytes
    if fmt_chunk_size > 16:
        file.read(fmt_chunk_size - 16)
    
    return (fmt_chunk_id, fmt_chunk_size, audio_format, num_channels, 
            sample_rate, byte_rate, block_align, bits_per_sample)

def find_data_chunk(file):
    """Find the data chunk in the WAV file."""
    data_chunk_id = file.read(4)
    while data_chunk_id != b'data':
        # Skip this chunk
        chunk_size = struct.unpack('<I', file.read(4))[0]
        file.read(chunk_size)
        data_chunk_id = file.read(4)
        
        if len(data_chunk_id) < 4:  # EOF
            raise ValueError("Not a valid WAV file: data chunk missing")
    
    data_size = struct.unpack('<I', file.read(4))[0]
    return data_chunk_id, data_size
