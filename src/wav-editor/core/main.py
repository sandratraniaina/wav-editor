# main.py
import argparse
import os
from ..utils.wav_reader import read_wav_file
from ..utils.wav_writer import write_wav_file
from .wav_processors import AudioProcessor

def main():
    parser = argparse.ArgumentParser(description='WAV File Editor CLI')
    parser.add_argument('input', help='Input WAV file path')
    parser.add_argument('output', help='Output WAV file path')
    parser.add_argument('--amplify', type=float, default=None,
                        help='Amplification factor (e.g., 1.5 for 50%% louder)')
    parser.add_argument('--normalize', action='store_true',
                        help='Normalize audio to use full dynamic range')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        return
    
    # Check if at least one processing option is selected
    if args.amplify is None and not args.normalize:
        print("Error: No processing option selected. Use --amplify or --normalize.")
        return
    
    try:
        print(f"Reading WAV file: {args.input}")
        header, audio_data = read_wav_file(args.input)
        
        # Initialize the audio processor
        processor = AudioProcessor()
        processor.load_data(header, audio_data)
        
        processed_data = audio_data
        
        # Apply selected processing operations
        if args.amplify is not None:
            print(f"Applying amplification factor: {args.amplify}")
            processed_data = processor.amplify(args.amplify)
        
        if args.normalize:
            print("Normalizing audio...")
            processed_data = processor.normalize()
        
        print(f"Writing to output file: {args.output}")
        write_wav_file(args.output, header, processed_data)
        
        print("Processing complete!")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()