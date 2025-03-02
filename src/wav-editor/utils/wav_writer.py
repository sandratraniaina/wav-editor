# wav_writer.py
import struct

def write_wav_file(file_path, header, audio_data):
    """
    Manually write a WAV file without using audio libraries.
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
        
        # Write audio data
        bits_per_sample = header['bits_per_sample']
                
        if bits_per_sample == 8:
            # 8-bit audio is unsigned
            # Convert from signed back to unsigned
            converted_data = [sample + 128 for sample in audio_data]
            file.write(struct.pack(f'{len(converted_data)}B', *converted_data))
        elif bits_per_sample == 16:
            # 16-bit audio is signed
            file.write(struct.pack(f'{len(audio_data)}<h', *audio_data))
        elif bits_per_sample == 32:
            # 32-bit audio is signed
            file.write(struct.pack(f'{len(audio_data)}<i', *audio_data))
        elif bits_per_sample == 24:
            # Special handling for 24-bit since Python doesn't have a built-in type
            for sample in audio_data:
                # Convert signed int to 3 bytes (24-bit)
                file.write(sample.to_bytes(3, byteorder='little', signed=True))