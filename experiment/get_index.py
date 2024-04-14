import pyaudio

def get_input_device_index():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    list = []
    for i in range(0, numdevices): # type: ignore
        device = p.get_device_info_by_host_api_device_index(0, i)
        device_name = device.get('name')
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print ("Input Device id ", i, " - ", device_name) # type: ignore
            list.append(device)
    return list

def get_mic_index():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    list = []
    for i in range(0, numdevices): # type: ignore
        device = p.get_device_info_by_host_api_device_index(0, i)
        device_name = device.get('name')
        if ('Mic' in device_name):
            list.append(device)
    return list

if __name__ == '__main__':
    list = get_mic_index()
    for i in range(len(list)): # type: ignore
        print(list[i]) # type: ignore
