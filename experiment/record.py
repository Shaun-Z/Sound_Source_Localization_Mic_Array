import pyaudio
import wave

# %%
RESPEAKER_RATE = 16000 # sampling rate
RESPEAKER_CHANNELS = 6 # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2 # sample width (Byte)

# %%
RESPEAKER_INDEX = 0  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# %% creates a pyaudio.PyAudio instance to manage the audio stream.
p = pyaudio.PyAudio()

# %% open an audio input stream ready for recording. p.get_format_from_width(RESPEAKER_WIDTH) determines the data format based on the sample width.
stream = p.open(
            rate=RESPEAKER_RATE,
            format=p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,
            input_device_index=RESPEAKER_INDEX,)

print("* recording") # type: ignore

# %% The number of loops is calculated based on the length of the recording and the size of the data block read each time. 
# In each loop, it reads a block of data from the audio stream and appends these blocks to the frames list. When the recording is complete, an end message is printed.
frames = []

for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)): # type: ignore
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording") # type: ignore

# %% When the recording is finished, close the audio stream and terminates the PyAudio instance, freeing up resources.
stream.stop_stream()
stream.close()
p.terminate()

# %% Finally, create a new WAV file using the wave module and set its parameters such as the number of channels, sample width, frame rate, etc.
# Then, write the previously recorded audio data to the file and close it.
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(RESPEAKER_CHANNELS)
wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
wf.setframerate(RESPEAKER_RATE)
wf.writeframes(b''.join(frames))
wf.close()