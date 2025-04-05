from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import log

def generate_key_pair_and_save():
    if find_folder.find_folders_with_existence_and_create("C:\PCSMT2-key"):
        # 生成密钥对
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # 保存私钥（PEM格式，无密码）
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open('C:\PCSMT2-key\private.pem', 'wb') as f:
            f.write(pem_private)

        # 保存公钥
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open('C:\PCSMT2-key\public.pem', 'wb') as f:
            f.write(pem_public)
    else:
        log.logger.error('密钥文件夹不存在！')

def generate_key_pair():
    if find_file.find_files_with_existence("C:\PCSMT2-key\public.pem"):
        if find_file.find_files_with_existence("C:\PCSMT2-key\private.pem"):
            pass
        else:
            log.logger.error('私钥文件不存在！')
            generate_key_pair_and_save()
    else:
        log.logger.error('公钥文件不存在！')
        generate_key_pair_and_save()

def load_key_pair():
    if find_file.find_files_with_existence("C:\PCSMT2-key\public.pem"):
        if find_file.find_files_with_existence("C:\PCSMT2-key\private.pem"):
            # 加载密钥
            with open('C:\PCSMT2-key\private.pem', 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)

            with open('C:\PCSMT2-key\public.pem', 'rb') as f:
                public_key = serialization.load_pem_public_key(f.read())

            return (public_key, private_key)
        else:
            log.logger.error('私钥文件不存在！')
            generate_key_pair()
    else:
        log.logger.error('公钥文件不存在！')
        generate_key_pair()

def cipher_key(text):
    """
    加密
    :param text: 待加密文本
    :return: 加密后的文本
    """
    key = load_key_pair()[0]
    cipher_text = key.encrypt(
        text.encode(),
        padding=padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return cipher_text

def decipher_key(cipher_text):
    """
    解密
    :param cipher_text: 待解密文本
    :return: 解密后的文本
    """
    key = load_key_pair()[1]
    plain_text = key.decrypt(
        cipher_text,
        padding=padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plain_text.decode()