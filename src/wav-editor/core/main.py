# main.py
import argparse
import os
from ..utils.wav_reader import read_wav_file
from ..utils.wav_writer import write_wav_file
from ..utils.plotter import plot_audio  # New import
from .wav_processors import AudioProcessor

def main():
    parser = argparse.ArgumentParser(description='WAV File Editor CLI')
    parser.add_argument('input', help='Input WAV file path')
    parser.add_argument('output', help='Output WAV file path')
    
    # Processing options
    processing_group = parser.add_argument_group('Processing Options')
    processing_group.add_argument('--amplify', type=float, default=None,
                        help='Amplification factor (e.g., 1.5 for 50%% louder)')
    processing_group.add_argument('--normalize', action='store_true',
                        help='Normalize audio to use full dynamic range')
    processing_group.add_argument('--anti-distort', type=float, default=None,
                        help='Apply amplification with anti-distortion (e.g., 2.0)')
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--smoothing', type=float, default=0.3,
                        help='Smoothing factor for anti-distortion (0.0-1.0)')
    advanced_group.add_argument('--multi-band', action='store_true',
                        help='Use multi-band processing with anti-distortion')
    advanced_group.add_argument('--bands', type=int, default=3,
                        help='Number of frequency bands for multi-band processing')
    
    # Plotting option
    parser.add_argument('--plot', action='store_true',
                        help='Plot original and processed audio waveforms')

    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        return
    
    # Check for processing option
    if args.amplify is None and not args.normalize and args.anti_distort is None:
        print("Error: No processing option selected. Use --amplify, --normalize, or --anti-distort.")
        return
    
    # Validate smoothing factor
    if args.smoothing < 0.0 or args.smoothing > 1.0:
        print("Error: Smoothing factor must be between 0.0 and 1.0")
        return
        
    # Validate bands count
    if args.bands < 1:
        print("Error: Number of bands must be at least 1")
        return
    
    try:
        print(f"Reading WAV file: {args.input}")
        header, audio_data = read_wav_file(args.input)
        
        # Process audio
        processor = AudioProcessor().load_data(header, audio_data)
        processed_data = audio_data
        
        # Track if we've applied any processing
        processing_applied = False
        
        if args.amplify is not None:
            print(f"Amplifying by factor: {args.amplify}")
            processed_data = processor.amplify(args.amplify)
            processing_applied = True
        
        if args.anti_distort is not None:
            print(f"Anti-distortion amplification: {args.anti_distort}")
            print(f"Using smoothing factor: {args.smoothing}")
            processed_data = processor.anti_distortion(
                args.anti_distort, 
                args.smoothing
            )
            processing_applied = True
        
        if args.normalize:
            print("Normalizing audio...")
            processed_data = processor.normalize()
            processing_applied = True
        
        if not processing_applied:
            print("Warning: No processing was applied. Output will be identical to input.")
        
        print(f"Writing to: {args.output}")
        write_wav_file(args.output, header, processed_data)
        print("Processing complete!")
        
        # Print some stats about the processed audio
        orig_max = max(abs(sample) for sample in audio_data)
        proc_max = max(abs(sample) for sample in processed_data)
        
        print("\nAudio Statistics:")
        print(f"Original max amplitude: {orig_max}")
        print(f"Processed max amplitude: {proc_max}")
        print(f"Bit depth: {header['bits_per_sample']} bits")
        print(f"Sample rate: {header['sample_rate']} Hz")
        print(f"Number of channels: {header['num_channels']}")
        print(f"Duration: {len(audio_data) / header['sample_rate']:.2f} seconds")
        
        # Plot if requested
        if args.plot:
            plot_output = f"{args.output.rsplit('.', 1)[0]}_plot.png"  # e.g., output_plot.png
            plot_audio(audio_data, processed_data, header['sample_rate'], plot_output)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()