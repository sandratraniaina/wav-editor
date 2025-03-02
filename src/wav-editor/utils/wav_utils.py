def get_bit_depth_range(bits_per_sample):
    """
    Calculate the maximum and minimum values based on bit depth.
    
    Args:
        bits_per_sample: Integer representing the number of bits per sample
        
    Returns:
        Tuple of (min_value, max_value)
    """
    if bits_per_sample == 8:
        max_value = 127  # 8-bit signed range is -128 to 127
    elif bits_per_sample == 16:
        max_value = 32767  # 16-bit signed range is -32768 to 32767
    elif bits_per_sample == 24:
        max_value = 8388607  # 24-bit signed range is -8388608 to 8388607
    elif bits_per_sample == 32:
        max_value = 2147483647  # 32-bit signed range is -2147483648 to 2147483647
    else:
        raise ValueError(f"Unsupported bit depth: {bits_per_sample}")
    
    min_value = -max_value - 1
    return min_value, max_value
