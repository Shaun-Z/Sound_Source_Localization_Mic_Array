import pyaudio
import wave

from get_index import get_mic_index

# %% get mics' index
list = get_mic_index()
for i in range(len(list)):
    print(list[i])

if len(list) == 2:
    print("\033[92mThere are 2 mics connected to the device.\033[0m")
else:
    print("\033[91mThere are not 2 mics connected to the device.\033[0m")
    exit()

# %%
RESPEAKER_RATE = int(list[0]['defaultSampleRate']) # sampling rate
RESPEAKER_CHANNELS = list[0]['maxInputChannels'] # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2 # sample width (Byte)

# %% Record configuration
RESPEAKER_INDEX_1 = int(list[0]['index']) 
RESPEAKER_INDEX_2 = int(list[1]['index']) 
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME_1 = "output1.wav"
WAVE_OUTPUT_FILENAME_2 = "output2.wav"

# %% creates a pyaudio.PyAudio instance to manage the audio stream.
p = pyaudio.PyAudio()

# %% open an audio input stream ready for recording.
stream1 = p.open(
    rate=RESPEAKER_RATE,
    format=p.get_format_from_width(RESPEAKER_WIDTH),
    channels=RESPEAKER_CHANNELS,
    input=True,
    input_device_index=RESPEAKER_INDEX_1,)

print("* recording")

# %% The number of loops is calculated based on the length of the recording and the size of the data block read each time. 
# In each loop, it reads a block of data from the audio stream and appends these blocks to the frames list. When the recording is complete, an end message is printed.
frames1 = []

for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data1 = stream1.read(CHUNK)
    frames1.append(data1)

print("Mic 1 done recording")

# %% When the recording is finished, close the audio stream, freeing up resources.
stream1.stop_stream()
stream1.close()

stream2 = p.open(
    rate=RESPEAKER_RATE,
    format=p.get_format_from_width(RESPEAKER_WIDTH),
    channels=RESPEAKER_CHANNELS,
    input=True,
    input_device_index=RESPEAKER_INDEX_2,)

frames2 = []

for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data2 = stream2.read(CHUNK)
    frames2.append(data2)

print("Mic 2 done recording")            

stream2.stop_stream()
stream2.close()

# %% When the recording is finished terminates the PyAudio instance, freeing up resources.
p.terminate()

# %% Finally, create a new WAV file using the wave module and set its parameters such as the number of channels, sample width, frame rate, etc.
# Then, write the previously recorded audio data to the file and close it.
wf1 = wave.open(WAVE_OUTPUT_FILENAME_1, 'wb')
wf1.setnchannels(RESPEAKER_CHANNELS)
wf1.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
wf1.setframerate(RESPEAKER_RATE)
wf1.writeframes(b''.join(frames1))
wf1.close()

wf2 = wave.open(WAVE_OUTPUT_FILENAME_2, 'wb')
wf2.setnchannels(RESPEAKER_CHANNELS)
wf2.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
wf2.setframerate(RESPEAKER_RATE)
wf2.writeframes(b''.join(frames2))
wf2.close()