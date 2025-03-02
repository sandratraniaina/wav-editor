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

def read_8bit_audio_data(raw_data):
    """Process 8-bit audio data."""
    fmt = 'B'  # unsigned char
    samples_count = len(raw_data)
    # Convert to signed for consistent processing
    return [sample - 128 for sample in struct.unpack(f'{samples_count}{fmt}', raw_data)]

def read_24bit_audio_data(raw_data, bytes_per_sample):
    """Process 24-bit audio data."""
    samples_count = len(raw_data) // bytes_per_sample
    audio_data = []
    for i in range(samples_count):
        start = i * bytes_per_sample
        # Convert 3 bytes (24-bit) to a signed int
        value = int.from_bytes(raw_data[start:start+3], byteorder='little', signed=True)
        audio_data.append(value)
    return audio_data

def read_standard_audio_data(raw_data, bits_per_sample, bytes_per_sample):
    """Process 16-bit or 32-bit audio data."""
    if bits_per_sample == 16:
        fmt = '<h'  # signed short
    elif bits_per_sample == 32:
        fmt = '<i'  # signed int
    else:
        raise ValueError(f"Unexpected bit depth in standard reader: {bits_per_sample}")
    
    samples_count = len(raw_data) // bytes_per_sample
    return list(struct.unpack(f'{samples_count}{fmt}', raw_data))

def read_wav_file(file_path):
    """
    Manually read a WAV file without using audio libraries.
    Returns a tuple of (header_info, audio_data)
    """
    with open(file_path, 'rb') as file:
        # Read header sections
        riff_chunk_id, chunk_size, format_id = read_wav_header(file)
        
        fmt_data = read_fmt_chunk(file)
        (fmt_chunk_id, fmt_chunk_size, audio_format, num_channels, 
         sample_rate, byte_rate, block_align, bits_per_sample) = fmt_data
        
        data_chunk_id, data_size = find_data_chunk(file)
        
        # Construct header information
        header = {
            'chunk_id': riff_chunk_id,
            'chunk_size': chunk_size,
            'format': format_id,
            'fmt_chunk_id': fmt_chunk_id,
            'fmt_chunk_size': fmt_chunk_size,
            'audio_format': audio_format,
            'num_channels': num_channels,
            'sample_rate': sample_rate,
            'byte_rate': byte_rate,
            'block_align': block_align,
            'bits_per_sample': bits_per_sample,
            'data_chunk_id': data_chunk_id,
            'data_size': data_size
        }
        
        # Read the actual audio data
        raw_data = file.read(data_size)
        bytes_per_sample = bits_per_sample // 8
        
        # Process audio data based on bit depth
        if bits_per_sample == 8:
            audio_data = read_8bit_audio_data(raw_data)
        elif bits_per_sample == 24:
            audio_data = read_24bit_audio_data(raw_data, bytes_per_sample)
        else:
            audio_data = read_standard_audio_data(raw_data, bits_per_sample, bytes_per_sample)
        
        return header, audio_data