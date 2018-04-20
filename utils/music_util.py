# encoding=utf8
import requests
import os, json
import base64
from Crypto.Cipher import AES
import warnings
from codecs import encode

warnings.filterwarnings("ignore")

BASE_URL = 'http://music.163.com/'
REQ_TIMEOUT = 5

class Song(object):
    def __lt__(self, other):
        return self.commentCount > other.commentCount

    def aesEncrypt(self, text, secKey):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(secKey, 2, '0102030405060708')
        ciphertext = encryptor.encrypt(text)
        ciphertext = base64.b64encode(ciphertext)
        ciphertext = str(ciphertext, encoding="utf-8")
        return ciphertext

    def rsaEncrypt(self, text, pubKey, modulus):
        text = text[::-1].encode("utf-8")
        rs = int(encode(text, 'hex'), 16) ** int(pubKey, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def createSecretKey(self, size):
        return (''.join(map(lambda xx: (hex(xx)[2:]), os.urandom(size))))[0:16]

    def getUrlSong(self, song_id : int) -> str:
        """
        get play url of songs certained by its id,
        using music.163.com api
        """
        # url = 'http://music.163.com/weapi/v1/play/record?csrf_token='
        url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
        headers = {'Accept-Encoding':'gzip, deflate', 'Host':'music.163.com', 'Origin':'http://music.163.com', 'Referer': 'http://music.163.com/', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'}
        # text = "{\"uid\":\"93159006\",\"type\":\"-1\",\"limit\":\"1000\",\"offset\":\"0\",\"total\":\"true\",\"csrf_token\":\"\"}"
        text = '{\"ids\":\"[' + str(song_id) + ']\",\"br\":128000,\"csrf_token\":\"\"}'
        modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        nonce = '0CoJUm6Qyw8W8jud'
        pubKey = '010001'
        secKey = self.createSecretKey(16)
        encText = self.aesEncrypt(self.aesEncrypt(text, nonce), secKey)
        encSecKey = self.rsaEncrypt(secKey, pubKey, modulus)
        data = {'params': encText, 
                'encSecKey': encSecKey
                }
        req = requests.post(url, headers=headers, data = data)
        # print(req.content.decode())

        try:
            data = json.loads(req.content.decode())
        except:
            print("Invalid json result")
            return None

        # print(data["data"][0]["url"])
        try:
            song_url = data["data"][0]["url"]
        except:
            print("Fail to get url from json returned")
            return None

        return song_url

def main():
    song = Song()
    song.getUrlSong("493093412")

if __name__ == '__main__':
    main()
