import wave

from certifi import contents

file_name = './encrypted_aud.wav'
file = wave.open(file_name, 'rb')
parameters = file.getparams()
contents = bytearray(file.readframes(file.getnframes()))
contents[6969] = 83
contents[6970] = 72
contents[6971] = 65
contents[6972] = 82
contents[6973] = 65
contents[6974] = 78
file.close()
print("Audio Tampered")

outputfile = wave.open('tampered_aud.wav', 'wb')
outputfile.setparams(parameters)
outputfile.writeframes(contents)
outputfile.close()
