# utils/plotter.py
import matplotlib.pyplot as plt

def plot_audio(original_data, processed_data, sample_rate, output_path="audio_plot.png"):
    """
    Plot original and processed audio waveforms side by side.

    Args:
        original_data: List of original audio samples
        processed_data: List of processed audio samples
        sample_rate: Sample rate of the audio (in Hz)
        output_path: Path to save the plot (default: "audio_plot.png")
    """
    # Calculate time axis
    time = [i / sample_rate for i in range(len(original_data))]

    # Create a figure with two subplots side by side
    plt.figure(figsize=(12, 6))

    # Plot original audio
    plt.subplot(1, 2, 1)
    plt.plot(time, original_data, label="Original", color="blue")
    plt.title("Original Audio")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()

    # Plot processed audio
    plt.subplot(1, 2, 2)
    plt.plot(time, processed_data, label="Processed", color="orange")
    plt.title("Processed Audio")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()  # Close the figure to free memory

    print(f"Plot saved to: {output_path}")