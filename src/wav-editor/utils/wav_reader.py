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
