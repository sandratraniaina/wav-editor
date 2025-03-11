from ..utils.wav_utils import get_bit_depth_range
import numpy as np

class AudioProcessor:
    """
    Class for processing WAV audio data with various effects.
    """
    
    def __init__(self):
        self.header = None
        self.audio_data = None
        self.min_value = None
        self.max_value = None
    
    def check_data(self):
        if self.audio_data is None or self.header is None:
            raise ValueError("No audio data loaded. Call load_data() first.")
    
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
        self.check_data()
        
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
        self.check_data()
        
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
    
    def anti_distortion(self, factor, smoothing_factor=1):
        """
        Apply amplification with anti-distortion using soft clipping.
        
        Uses a smooth transition around threshold to prevent harsh distortion.
        This creates a more natural-sounding amplification at high levels.
        
        Args:
            factor: Amplification factor (1.0 = no change, 2.0 = twice as loud)
            smoothing_factor: Controls threshold for soft clipping (0.0-1.0)
            
        Returns:
            List of amplified audio samples with anti-distortion
        """
        self.check_data()
        
        # Set threshold based on smoothing factor
        # Higher smoothing_factor means lower threshold (more soft clipping)
        threshold = 1.0 - smoothing_factor
        threshold_value = int(self.max_value * threshold)
        print(f"Max value: {self.max_value}")
        processed_data = []
        
        for sample in self.audio_data:
            # Apply initial gain
            amplified = sample * factor
            
            # Apply soft clipping if above threshold
            abs_sample = abs(amplified)
            if abs_sample > threshold_value:
                sign = 1 if amplified > 0 else -1
                
                # Calculate how much we're over the threshold
                excess = abs_sample - threshold_value
                # Apply cubic soft-clipping formula
                # This creates a smooth transition instead of hard clipping
                # Formula: threshold + (excess - excess³/(3*threshold²))
                soft_clip = threshold_value + (excess - (excess**3) / (3 * (threshold_value**2)))
                new_sample = int(sign * soft_clip)
            else:
                new_sample = int(amplified)
            
            # Final clipping protection (in case calculations exceed bounds)
            if new_sample > self.max_value:
                new_sample = self.max_value
            elif new_sample < self.min_value:
                new_sample = self.min_value
            processed_data.append(new_sample)
        
        return processed_data
