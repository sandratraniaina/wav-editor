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
    
    def amplify(self, factor):
        """
        Amplify audio data by the given factor.
        
        Args:
            factor: Amplification factor (1.0 = no change, 2.0 = twice as loud)
            
        Returns:
            List of amplified audio samples
        """
        if self.audio_data is None or self.header is None:
            raise ValueError("No audio data loaded. Call load_data() first.")
        
        amplified_data = []
        for sample in self.audio_data:
            new_sample = int(sample * factor)
            
            # Clipping protection
            if new_sample > self.max_value:
                new_sample = self.max_value
            elif new_sample < self.min_value:
                new_sample = self.min_value
                
            amplified_data.append(new_sample)
        
        return amplified_data
    
    def normalize(self):
        """
        Normalize audio data to use the full dynamic range.
        
        Returns:
            List of normalized audio samples
        """
        if self.audio_data is None or self.header is None:
            raise ValueError("No audio data loaded. Call load_data() first.")
        
        # Find the maximum absolute value in the audio data
        max_abs = max(abs(sample) for sample in self.audio_data)
        if max_abs == 0:  # Avoid division by zero
            return self.audio_data.copy()
        
        # Calculate normalization factor
        norm_factor = self.max_value / max_abs
        
        # Apply normalization
        normalized_data = []
        for sample in self.audio_data:
            new_sample = int(sample * norm_factor)
            normalized_data.append(new_sample)
        
        return normalized_data