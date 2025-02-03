import numpy as np
import scipy.io.wavfile as wavfile

# Function to embed a message in the audio file
def Embedding(input_filename, output_filename, message):
    # Read the audio file
    rate, audio = wavfile.read(input_filename)
    
    # If stereo, use only the first channel
    audio = audio[:, 0] if len(audio.shape) > 1 else audio.copy()
    
    # Calculate message length in bits
    msg_len = 8 * len(message)
    
    # Calculate segment length based on message length
    seg_len = int(2 * 2**np.ceil(np.log2(2 * msg_len)))
    
    # Number of segments in the audio
    seg_num = int(np.ceil(len(audio) / seg_len))
    
    # Resize audio array to fit exact number of segments
    audio.resize(seg_num * seg_len, refcheck=False)
    
    # Convert message to binary and map to phase angles (-π/2 or π/2)
    msg_bin = np.ravel([[int(y) for y in format(ord(x), '08b')] for x in message])
    msg_pi = np.where(msg_bin == 0, -np.pi / 2, np.pi / 2)
    
    # Perform FFT on the audio and get magnitude and phase
    segs = np.fft.fft(audio.reshape((seg_num, seg_len)))
    M, P = np.abs(segs), np.angle(segs)
    
    # Middle of the segment (used for phase manipulation)
    seg_mid = seg_len // 2
    
    # Embed the message into the phase of each segment
    for i in range(seg_num):
        start = i * len(msg_pi) // seg_num
        end = (i + 1) * len(msg_pi) // seg_num
        
        # Embed phase values into the first half of the segment
        P[i, seg_mid - (end - start):seg_mid] = msg_pi[start:end]
        
        # Embed the reverse phase values into the second half of the segment
        P[i, seg_mid + 1:seg_mid + 1 + (end - start)] = -msg_pi[start:end][::-1]
    
    # Reconstruct the audio with modified phases
    audio = np.fft.ifft(M * np.exp(1j * P)).real.ravel().astype(np.int16)
    
    # Save the modified audio to the output file
    wavfile.write(output_filename, rate, audio)

# Function to extract the embedded message from the audio file
def Extracting(input_filename, msg_len):
    # Read the audio file
    rate, audio = wavfile.read(input_filename)
    
    # Calculate segment length based on message length
    seg_len = int(2 * 2**np.ceil(np.log2(2 * msg_len)))
    
    # Number of segments in the audio
    seg_num = int(np.ceil(len(audio) / seg_len))
    
    # Middle of the segment (used for phase extraction)
    seg_mid = seg_len // 2
    
    # List to store extracted message bits
    extracted_bits = []
    
    # Perform FFT and extract message bits from the phase
    for i in range(seg_num):
        # Get the current segment of audio
        segment_audio = audio[i * seg_len:(i + 1) * seg_len]
        
        # Perform FFT on the segment
        x = np.fft.fft(segment_audio)
        
        # Extract the phase of the segment
        extracted_phase = np.angle(x)
        
        # Calculate the start and end indices for the bits in this segment
        start = i * msg_len // seg_num
        end = (i + 1) * msg_len // seg_num
        
        # Extract bits by checking if the phase is negative or positive
        extracted_bits.extend((extracted_phase[seg_mid - (end - start):seg_mid] < 0).astype(np.int8))
    
    # Ensure the extracted bits match the message length
    extracted_bits = np.array(extracted_bits[:msg_len])
    
    # Convert extracted bits back to characters
    chars = extracted_bits.reshape((-1, 8)).dot(1 << np.arange(8 - 1, -1, -1)).astype(np.uint8)
    
    # Convert the character codes back to a string
    extracted_message = ''.join(chr(c) for c in chars)
    
    return extracted_message
