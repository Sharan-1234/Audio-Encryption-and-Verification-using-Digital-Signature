import hashlib
from cryptography.fernet import Fernet


#Digital signature
def hash_audio(input: bytes) -> bytes:
    '''Digest generation'''
    hash_object = hashlib.sha256(input)
    return hash_object.hexdigest()


def generate_sign(digest: bytes) -> tuple[bytes, bytes]:
    '''Digital signature'''
    key = Fernet.generate_key() #is in binary format
    #object creation
    fer = Fernet(key)
    sign = fer.encrypt(digest)
    return sign, key


def decrypt_sign(sign: bytes, key: bytes) -> bytes:
    '''D_sign decryption'''
    fer = Fernet(key)
    return fer.decrypt(sign)

#


#Sending prep
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


#Receiving prep
def find_index(n: int) -> int:
    return n//2


def extract_key(implanted_sign: bytes):
    sign_len = len(implanted_sign)-44;      #len(key) is always 44
    implanted_sign = implanted_sign.decode('utf-8')
    index = find_index(sign_len)
    key = implanted_sign[index: index+44]
    parts = [implanted_sign[:index], implanted_sign[index+44:]]
    return ''.join(parts).encode(), key

#


#main
def main() -> None:
    aud = 'sampil.wav'
    with open(aud, 'rb') as file:
        contents = file.read()      # binary contents of the audio file
        # print(contents)
    digest = hash_audio(contents).encode()      # binary digest (hash)
    sign, key = generate_sign(digest)       # sign->binary (encrypted stuff), key->binary
    decrypted_contents = decrypt_sign(sign, key)        # binary decrypted contents
    send_content = implant_key(sign, key)
    extracted_sign, e_key = extract_key(send_content)

    # print('digest:', digest)
    # print()
    # print('sign:', sign)
    # print()
    # print('key:', key)
    # print()
    # print('decr_stuff:', decrypted_contents)
    # # print(hash_audio.__doc__)
    # print()
    # print('implanted:', send_content)
    # print()
    # print('extracted:', extracted_sign)
    # print()
    # print("Is the Digital sign and the extracted sign(from implant_key) is same?:"+str(sign.decode('utf-8') == extracted_sign.decode('utf-8')))
    


if __name__ == '__main__':
    main()