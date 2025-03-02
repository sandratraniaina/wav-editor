from ..utils.wav_utils import get_bit_depth_range

class AudioProcessor:
    """
    Class for processing WAV audio data with various effects.
    """
    
    def __init__(self):
        self.header = None
        self.audio_data = None
        self.min_value = None
        self.max_value = None
    
    def load_data(self, header, audio_data):
        """
        Load audio data and header for processing.
        
        Args:
            header: Dictionary containing WAV file header information
            audio_data: List of audio samples
        """
        self.header = header
        self.audio_data = audio_data
        self.min_value, self.max_value = get_bit_depth_range(header['bits_per_sample'])
        return self