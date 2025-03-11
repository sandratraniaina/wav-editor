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
    
    def _stft(self, x, fft_size, hop_size):
        """
        Short-time Fourier transform.
        Transforms a time domain signal into the frequency domain.
        
        Args:
            x: Input audio data
            fft_size: Size of FFT window
            hop_size: Number of samples between successive frames
        
        Returns:
            Complex STFT matrix
        """
        # Create Hanning window
        window = np.hanning(fft_size)
        
        # Calculate number of frames
        num_frames = 1 + (len(x) - fft_size) // hop_size
        
        # Initialize STFT matrix
        stft_matrix = np.zeros((fft_size//2 + 1, num_frames), dtype=complex)
        
        # Process each frame
        for i in range(num_frames):
            # Extract frame
            start = i * hop_size
            frame = x[start:start+fft_size]
            
            # Pad frame if needed
            if len(frame) < fft_size:
                frame = np.pad(frame, (0, fft_size - len(frame)))
            
            # Apply window
            windowed_frame = frame * window
            
            # Compute FFT
            spectrum = np.fft.rfft(windowed_frame)
            
            # Store in matrix
            stft_matrix[:, i] = spectrum
            
        return stft_matrix
    
    def _istft(self, stft_matrix, fft_size, hop_size, original_length=None):
        """
        Inverse short-time Fourier transform.
        Transforms frequency domain signal back to time domain.
        
        Args:
            stft_matrix: STFT matrix
            fft_size: Size of FFT window
            hop_size: Number of samples between successive frames
            original_length: Length of original signal (optional)
        
        Returns:
            Time domain signal
        """
        # Create Hanning window
        window = np.hanning(fft_size)
        
        # Get number of frames
        num_frames = stft_matrix.shape[1]
        
        # Calculate expected output length
        expected_length = (num_frames - 1) * hop_size + fft_size
        if original_length is not None:
            expected_length = min(expected_length, original_length)
        
        # Initialize output and normalization arrays
        output = np.zeros(expected_length)
        normalization = np.zeros(expected_length)
        
        # Process each frame
        for i in range(num_frames):
            # Compute inverse FFT
            frame = np.fft.irfft(stft_matrix[:, i], n=fft_size)
            
            # Apply window
            windowed_frame = frame * window
            
            # Add to output with overlap
            start = i * hop_size
            end = start + fft_size
            if end > len(output):
                end = len(output)
                windowed_frame = windowed_frame[:end-start]
            
            output[start:end] += windowed_frame
            normalization[start:end] += window[:end-start]
        
        # Normalize to account for overlap
        nonzero_indices = normalization > 1e-10
        output[nonzero_indices] /= normalization[nonzero_indices]
        
        return output
    
    def _convert_to_float(self, audio_data):
        """
        Convert integer audio data to float in range [-1.0, 1.0].
        
        Args:
            audio_data: Integer audio samples
            
        Returns:
            Float audio samples in range [-1.0, 1.0]
        """
        return np.array(audio_data, dtype=np.float64) / self.max_value
    
    def _convert_from_float(self, float_data):
        """
        Convert float audio data in range [-1.0, 1.0] back to integer.
        
        Args:
            float_data: Float audio samples in range [-1.0, 1.0]
            
        Returns:
            Integer audio samples
        """
        # Clip to valid range
        float_data = np.clip(float_data, -1.0, 1.0)
        
        # Scale and convert to integers
        int_data = (float_data * self.max_value).astype(np.int32).tolist()
        
        return int_data
    
    def remove_noise(self, noise_data, method='spectral_subtraction', alpha=2.0, beta=0.01, fft_size=2048, hop_size=512):
        """
        Remove noise from audio using spectral subtraction.
        
        Args:
            noise_data: Noise pattern audio samples
            method: Noise removal method ('spectral_subtraction')
            alpha: Oversubtraction factor (higher = more noise reduction)
            beta: Spectral floor (higher = less musical noise)
            fft_size: Size of FFT window
            hop_size: Number of samples between successive frames
            
        Returns:
            List of processed audio samples with noise removed
        """
        self.check_data()
        
        # Convert to float
        original_float = self._convert_to_float(self.audio_data)
        noise_float = self._convert_to_float(noise_data)
        
        if method == 'spectral_subtraction':
            # Compute STFTs
            original_stft = self._stft(original_float, fft_size, hop_size)
            noise_stft = self._stft(noise_float, fft_size, hop_size)
            
            # Get magnitude of spectra
            original_mag = np.abs(original_stft)
            
            # Compute average noise spectrum
            noise_mag = np.mean(np.abs(noise_stft), axis=1).reshape(-1, 1)
            
            # Subtract noise spectrum
            subtracted_mag = np.maximum(original_mag - alpha * noise_mag, beta * original_mag)
            
            # Reconstruct complex spectrum
            processed_stft = subtracted_mag * np.exp(1j * np.angle(original_stft))
            
            # Inverse STFT
            processed_float = self._istft(processed_stft, fft_size, hop_size, original_length=len(original_float))
            
            # Convert back to int
            processed_data = self._convert_from_float(processed_float)
            
            return processed_data
        else:
            raise ValueError(f"Unsupported noise removal method: {method}")