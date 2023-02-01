import wave
import hashlib
from cryptography.fernet import Fernet
import cryptography


#Extracting the msg
def ex_msg(audio_file: str) -> None:
    try:
        print ("[EXTRACTING] ", end='')
        wav_audio = wave.open(audio_file, mode='rb')
        frame_bytes = bytearray(list(wav_audio.readframes(wav_audio.getnframes())))
        extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
        string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
        msg = string.split("@@@")[0]
        # print("Extracted Message : "+msg)
        print ("Done")
        print("Extracted Message : "+"\033[1;34m"+msg+"\033[0m")
    except Exception as e:
        print('Failed')
    finally:
        wav_audio.close()


#Receiving prep
def find_index(n: int) -> int:
    return n//2


def extract_key(implanted_sign: bytes):
    sign_len = len(implanted_sign)-44;      #len(key) is always 44
    implanted_sign = implanted_sign.decode('utf-8')
    index = find_index(sign_len)
    key = implanted_sign[index+1: index+45]
    parts = [implanted_sign[:index+1], implanted_sign[index+45:]]
    return ''.join(parts).encode(), key


# receiver's side
def extract_components(audio: str) -> tuple[tuple, bytes, bytes]:
    contents = None
    params = None
    with wave.open(audio, 'rb') as file:
        params = file.getparams()
        contents = file.readframes(file.getnframes())

    encrypted_contents, implanted_key = contents.rsplit(b'$')    
    with open('receiver.txt', 'wb') as file2:
        file2.write(contents)
    return params, encrypted_contents, implanted_key

#
def decrypt_audio(encrypted_audio: bytes, key: bytes, params: tuple) -> None:
    '''Decrypt audio'''
    fernet = Fernet(key)
    decrypted_audio = fernet.decrypt(encrypted_audio)
    with wave.open('decrypted_aud.wav', 'wb') as file:
        file.setparams(params)
        file.writeframes(decrypted_audio)


#verify digi-sign
def hash_audio(input: str) -> bytes:
    '''Digest generation'''

    with wave.open(input, 'rb') as file:
      contents = file.readframes(file.getnframes())
    hash_object = hashlib.sha256(contents)
    return hash_object.hexdigest().encode()


def generate_sign(digest: bytes, key: bytes) -> bytes:
    '''Digital signature'''
    #object creation
    fer = Fernet(key)
    sign = fer.encrypt(digest)
    return sign


def verify_signature(file: str, sign: bytes, key: bytes) -> None:
    fernet = Fernet(key)
    sign += b'='
    old_digest = fernet.decrypt(sign)

    with wave.open(file, 'rb') as file:
        contents = file.readframes(file.getnframes())
    
    new_digest = hashlib.sha256(contents)
    if(new_digest.hexdigest() == old_digest.decode('utf-8')):
        print("\033[1;32;40m Received the Original content. Signature is verified \033[0m \n")



try:
    params, encrypted_contents, implanted_key = extract_components('./tampered_aud.wav') #encrypted_aud.wav
    sign, key = extract_key(implanted_key)
    key = key.encode()
    decrypt_audio(encrypted_contents, key, params)
    ex_msg('decrypted_aud.wav')
    verify_signature('./decrypted_aud.wav', sign, key)
except cryptography.fernet.InvalidToken as invalidToken:
    print("\033[1;91m"+"Content tampered!"+"\033[0m")
except wave.Error as notWave:
    print("\033[1;91m"+"Format change detected"+"\033[0m")
except FileNotFoundError as notFound:
    print("\033[1;91m"+"File not found"+"\033[0m")
    
