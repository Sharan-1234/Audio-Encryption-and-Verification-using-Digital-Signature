import wave
import hashlib
from cryptography.fernet import Fernet


#Hiding msg in audio file using Steganography
def add_msg(audio_file: str, string: str, output: str) -> None: #attaining the audio file and the string to be hidden.
  try:
    print ("[HIDING] ", end='')
    wav_audio = wave.open(audio_file, mode='rb') #opening the AUDIO  file in "READBINARY"
    frame_bytes = bytearray(list(wav_audio.readframes(wav_audio.getnframes())))
    string = string + int((len(frame_bytes)-(len(string)*8*8))/8) *'@' 
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in string])))
    for i, bit in enumerate(bits):
      frame_bytes[i] = (frame_bytes[i] & 254) | bit
    frame_modified = bytes(frame_bytes)
    with wave.open(output, 'wb') as fd:
      fd.setparams(wav_audio.getparams())
      fd.writeframes(frame_modified)
    print ("Done")
  except Exception as e:
    print('Failed')
  else:
    wav_audio.close()


#Digital signature
def hash_audio(input: str) -> bytes:
    '''Digest generation'''

    with wave.open(input, 'rb') as file:
      contents = file.readframes(file.getnframes())
    hash_object = hashlib.sha256(contents)
    return hash_object.hexdigest().encode()


def generate_sign(digest: bytes) -> tuple[bytes, bytes]:
    '''Digital signature'''
    key = Fernet.generate_key() #is in binary format
    #object creation
    fer = Fernet(key) #fernet encryption gurantees that encrypted message cannot be manipulated without the key generated
    sign = fer.encrypt(digest) #encrypt the digest produced from audio file to attain the DIGITAL SIGNATURE
    return sign, key


#Implpantation key
def generate_index(n: int) -> int:
    return n//2


def implant_key(sign: bytes, key: bytes):
    sign = sign.decode('utf-8')
    key = key.decode('utf-8')
    n = len(sign) # =184
    index = generate_index(n)
    #implantation
    parts = [sign[:index], sign[index:]]
    parts.insert(1, key)
    return ''.join(parts).encode()

#



#encrypt the modified file
#audio encryption
def audio_encrypt(audio_file: str, key: bytes, output: str, implant_key: bytes) -> None:
  try:
    print("[ENCRYPTING AUDIO] ", end='')
    aud = wave.open(audio_file, mode='rb')
    frames = aud.readframes(aud.getnframes())
    fer = Fernet(key)
    encrypt_aud = fer.encrypt(frames)
    #embbed the implanted sign in the encrypted audio file
    encrypt_aud += b'$' + implant_key
    # with open('temp.txt', 'wb') as file:
    #   file.write(encrypt_aud)
    with wave.open(output, 'wb') as fd:
      fd.setparams(aud.getparams())
      fd.writeframes(encrypt_aud)
    print("Done")
  except Exception as e:
    print('Failed')
  else:
    aud.close()




#Sending preparation
try:
  secret_msg = 'To whoever receiving this message, we\'re sending this message to inform that we have been hiding in a cave inside the enemy territory for the past 3 days. The situation is very tense here, food and resources running out. Send Help. [LOC: N36.699923"; CODE: RED]'
  add_msg('./Final.wav', secret_msg, 'audio_with_message.wav')
  sign, key = generate_sign(hash_audio("audio_with_message.wav"))
  # print(sign)
  implanted_key = implant_key(sign, key)
  # print(implanted_key)
  audio_encrypt('audio_with_message.wav', key, 'encrypted_aud.wav', implanted_key)
except Exception:
  print('Critical Error!')