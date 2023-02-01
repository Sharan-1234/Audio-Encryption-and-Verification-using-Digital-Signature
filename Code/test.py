import wave
import hashlib
from cryptography.fernet import Fernet
from ast import literal_eval as make_tuple


def add_msg(audio_file, string, output):
  print ("Starting Encoding...")
  wav_audio = wave.open(audio_file, mode='rb')
  frame_bytes = bytearray(list(wav_audio.readframes(wav_audio.getnframes())))
  string = string + int((len(frame_bytes)-(len(string)*8*8))/8) *'#'
  # print(string)
  bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in string])))
  for i, bit in enumerate(bits):
    frame_bytes[i] = (frame_bytes[i] & 254) | bit
  frame_modified = bytes(frame_bytes)
  with wave.open(output, 'wb') as fd:
    fd.setparams(wav_audio.getparams())
    fd.writeframes(frame_modified)
  wav_audio.close()
  print ("Done Encoding...")

####################################################

def hash_audio(in_aud) -> bytes:
  '''Digest generation'''

  aud = wave.open(in_aud, mode='rb')
  contents = aud.readframes(aud.getnframes())
  hash_object = hashlib.sha256(contents)
  return hash_object.hexdigest()


def generate_sign(digest: bytes) -> tuple[bytes, bytes]:
    '''Digital signature'''
    key = Fernet.generate_key() #is in binary format
    #object creation
    fer = Fernet(key)
    digest = digest.encode('utf-8')
    sign = fer.encrypt(digest)
    return sign, key


#Sending prep
def generate_index(n: int) -> int:
    return n//2


def implant(sign: bytes, key: bytes):
    sign = sign.decode('utf-8')
    key = key.decode('utf-8')
    n = len(sign) # =184
    index = generate_index(n)
    #implantation
    parts = [sign[:index], sign[index:]]
    parts.insert(1, key)
    return ''.join(parts).encode()

#

# def embbed_implant(audio_file, implant_key):
#   aud = wave.open(audio_file, mode='rb')
#   content = aud.readframes(aud.getnframes())
#   # print(len(content))
#   content += implant_key
  

#   aud.close()
  

#audio encryption
def audio_encrypt(audio_file, key, output, implant_key):
  print("Start encrypting...")
  aud = wave.open(audio_file, mode='rb')
  frames = aud.readframes(aud.getnframes())
  fer = Fernet(key)
  encrypt_aud = fer.encrypt(frames)
  encrypt_aud += b'$' + implant_key

  with open('temp.txt', 'wb') as file:
    file.write(encrypt_aud)
  with wave.open(output, 'wb') as fd:
    fd.setparams(aud.getparams())
    fd.writeframes(encrypt_aud)
  aud.close()

def temp_decrypt(audio_file):
  print('start extracting key and sign')
  aud = wave.open(audio_file, mode='rb')
  frames = aud.readframes(aud.getnframes())


# receiver's ass
def extract_components(audio):
  contents = None
  params = None
  with wave.open(audio, 'rb') as file:
    params = file.getparams()
    contents = file.readframes(file.getnframes())
  
  encrypted_contents, implanted_key = contents.rsplit(b'$')

  return params, encrypted_contents, implanted_key
  

def find_index(n: int) -> int:
    return n//2



def extract_key(implanted_sign):
  sign_len = len(implanted_sign)-44;      #len(key) is always 44
  # implanted_sign = implanted_sign.decode('utf-8')
  index = find_index(sign_len)
  key = implanted_sign[index + 1: index+45]
  parts = [implanted_sign[:index], implanted_sign[index+44:]]
  return b''.join(parts), key


def decrypt_audio(encrypted_audio, key, params):
  '''Decrypt audio'''

  fernet = Fernet(key)
  decrypted_audio = fernet.decrypt(encrypted_audio)
  with wave.open('final.wav', 'wb') as file:
    file.setparams(params)
    file.writeframes(decrypted_audio)


def main() -> None:
    # in_aud = 'sampil.wav'
    out_aud = 'sampil.wav'
    temp_aud = 'temp.wav'

    
    params, ec, ik = extract_components(temp_aud)
    # print(ec)
    # print()
    print(type(ik))
    sign, key = extract_key(ik)
    print(key)
    decrypt_audio(ec, key, params)


    



if __name__ == '__main__':
    main()

#gAAAAABiflM3fwxF41RvJelerMxQIGxd_ovTEJ4MAlDATHHRxhP7x5wGtv92uwQ87jttZnaXAsGH83EMLKpdHacGroWIWB1UXAGomgK4WRVmugQiZc1TMy0leDDGjQIDUxieCko=j4DXBZ5Gw4vl1EDC_VNPLEphnjuZyewE0hwtCHcwzQiPFA6PHF6ngwICqbduPLv2iLOFo6-26O5fc2negEbUvCv2ifU=