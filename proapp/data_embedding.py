import numpy as np
import PIL as Image
import cv2
import bitstring

def calculate_embedding_capacity(dct_blocks):
    # Each DCT block has 64 coefficients, so each block can hold 64 bits
    return len(dct_blocks) * 64  # Total number of bits

def calculate_number_of_characters(embedding_capacity):
    # Calculate the number of characters that can be embedded based on number of blocks
    return embedding_capacity // 8  # Each block can store 1 byte (8 bits), which is 1 character


def get_dct_blocks(image_path):
    # Load image and convert to grayscale (or use RGB for more complex cases)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Check if image was loaded
    if image is None:
        return None

    # Resize the image to a suitable size if needed
    height, width = image.shape
    block_size = 8  # DCT block size

    dct_blocks = []

    # Process the image in 8x8 blocks
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            block = image[i:i+block_size, j:j+block_size]
            if block.shape == (block_size, block_size):
                dct_block = cv2.dct(np.float32(block))
                dct_blocks.append(dct_block)

    return dct_blocks, len(dct_blocks)

def extract_encoded_data_from_DCT(dct_blocks):
    """
    Extracts encoded data from DCT coefficient blocks.
    
    Parameters:
    - dct_blocks: List of 1D arrays, where each array contains DCT coefficients of an 8x8 block.
    
    Returns:
    - extracted_data: A bitstring containing the extracted binary data.
    """
    extracted_data = ""
    # Loop through each DCT block
    for current_dct_block in dct_blocks:
        # Skip DC coefficient and iterate over AC coefficients (1 to end)
        for i in range(1, len(current_dct_block)):
            curr_coeff = np.int32(current_dct_block[i])
            
            # Only consider coefficients greater than 1 for data embedding/extraction
            if curr_coeff > 1:
                # Extract the least significant bit of the current coefficient
                extracted_data += bitstring.pack('uint:1', np.uint8(current_dct_block[i]) & 0x01)
    
    return extracted_data


def embed_encoded_data_into_DCT(encoded_bits, dct_blocks):
    """
    Embeds binary data into DCT coefficient blocks.
    
    Parameters:
    - encoded_bits: A bitstring containing the binary data to embed.
    - dct_blocks: List of 1D arrays, where each array contains DCT coefficients of an 8x8 block.
    
    Returns:
    - converted_blocks: List of modified DCT blocks with embedded data.
    
    Raises:
    - ValueError: If data couldn't fully embed into the cover image.
    """
    
    data_complete = False
    encoded_bits.pos = 0  # Reset the position to the beginning of the bitstring
    encoded_data_len = bitstring.pack('uint:32', len(encoded_bits))  # Pack length of data into 32 bits
    
    converted_blocks = []
    
    # Iterate over each DCT block
    for current_dct_block in dct_blocks:
        # Iterate over AC coefficients (skip DC at index 0)
        for i in range(1, len(current_dct_block)):
            curr_coeff = np.int32(current_dct_block[i])
            
            # Only modify coefficients greater than 1 to minimize image distortion
            if curr_coeff > 1:
                curr_coeff = np.uint8(current_dct_block[i])  # Convert coefficient to 8-bit unsigned integer
                
                # Check if all data has been embedded
                if encoded_bits.pos == len(encoded_bits) - 1:
                    data_complete = True
                    break
                
                # Pack coefficient as an 8-bit integer to modify its least significant bit
                pack_coeff = bitstring.pack('uint:8', curr_coeff)
                
                # Embed data length bits first, then the actual message bits
                if encoded_data_len.pos <= len(encoded_data_len) - 1:
                    pack_coeff[-1] = encoded_data_len.read(1)  # Set LSB of coefficient to data length bit
                else:
                    pack_coeff[-1] = encoded_bits.read(1)  # Set LSB to message bit
                
                # Replace the current coefficient with the modified one
                current_dct_block[i] = np.float32(pack_coeff.read('uint:8'))
        
        # Append modified DCT block to the result
        converted_blocks.append(current_dct_block)
    
    # Check if the entire data has been embedded
    if not data_complete:
        raise ValueError("Data didn't fully embed into cover image!")
    
    return converted_blocks
