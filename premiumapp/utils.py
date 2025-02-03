import wave
import os


def encrypt_audio(audio_path, message, output_path):
    """
    Embeds a message into a PCM WAV audio file.
    
    :param audio_path: Path to the input WAV file.
    :param message: The message to embed into the audio.
    :param output_path: Path to save the output WAV file with the embedded message.
    :raises Exception: If the file does not exist or an error occurs during processing.
    """
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"File {audio_path} not found.")

        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        song = wave.open(audio_path, mode='rb')

        # Check if the audio file is PCM format
        if song.getcomptype() != 'NONE':
            song.close()
            raise ValueError("Unsupported audio format. Please use a PCM WAV file.")

        frame_bytes = bytearray(list(song.readframes(song.getnframes())))

        max_message_length = len(frame_bytes) // 8
        if len(message) > max_message_length:
            song.close()
            raise ValueError(f"Message is too long to fit in the audio file. Max length: {max_message_length} characters.")

        # Pad the message with '#' to ensure it fits in the audio
        message = message + int((len(frame_bytes) - (len(message) * 8 * 8)) / 8) * '#'
        bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in message])))

        for i, bit in enumerate(bits):
            frame_bytes[i] = (frame_bytes[i] & 254) | bit

        frame_modified = bytes(frame_bytes)

        with wave.open(output_path, 'wb') as fd:
            fd.setparams(song.getparams())
            fd.writeframes(frame_modified)

        song.close()
        return f"Message successfully encoded into {output_path}"

    except wave.Error as e:
        raise Exception(f"Wave module error: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


def decrypt_audio(audio_path):
    """
    Extracts a hidden message from a PCM WAV audio file.
    
    :param audio_path: Path to the input WAV file containing the hidden message.
    :return: The decoded message.
    :raises Exception: If the file does not exist or an error occurs during processing.
    """
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"File {audio_path} not found.")

        song = wave.open(audio_path, mode='rb')

        # Check if the audio file is PCM format
        if song.getcomptype() != 'NONE':
            song.close()
            raise ValueError("Unsupported audio format. Please use a PCM WAV file.")

        frame_bytes = bytearray(list(song.readframes(song.getnframes())))

        extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
        message = "".join(chr(int("".join(map(str, extracted[i:i+8])), 2)) for i in range(0, len(extracted), 8))

        decoded_message = message.split("#")[0]
        song.close()
        return decoded_message

    except wave.Error as e:
        raise Exception(f"Wave module error: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")
