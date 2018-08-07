# encoding=utf8
import requests
import os
import json
import time
import base64
from Crypto.Cipher import AES
import warnings
from codecs import encode
import urllib.request as ur
import urllib.error as ue
import urllib.parse as up
from ..config import logger

warnings.filterwarnings("ignore")

REQ_TIMEOUT = 5
URL_BASE = "http://music.163.com/api/playlist/detail?id="
REQ_TIMEOUT = 5
TOP_NUM = 5
QUERY_INTERVAL = 3600 * 6 # 6h
CLEAR_INTERVAL = 30 # 30days

class Song(object):
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
        Get play url of songs certained by its id,
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

def songs_change(tracks : dict, res_path : str) -> bool:
    '''
    Detect songs change
    '''

    num_of_line = 0
    if os.path.exists(res_path) and os.path.isfile(res_path):
        # path exists
        with open(res_path, 'r') as f:
            try:
                line = f.readline()
                num_of_line += 1
            except:
                logger.error("Fail to read oneline")

            while line:
                if (num_of_line % 3) == 2:
                    #deal with the line
                    id = int(line.strip('\n'))
                    if id not in [tracks[i]["id"] for i in range(TOP_NUM)]:
                        f.close()
                        return True

                try:
                    line = f.readline()
                    num_of_line += 1
                except:
                    logger.error("Fail to read oneline")

        f.close()
    else:
        return True
        
    return False

def get_songs_rank(user_id : str, name : str, playlist_path : str, songs_path : str) -> None:
    '''
    Get songs rank from api and save result to certain txt
    '''

    url = URL_BASE + user_id
    res_path = "{}/{}.txt".format(playlist_path, name)

    req = ur.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36)")
    try:
        with ur.urlopen(req, timeout = REQ_TIMEOUT) as response:
            data = response.read().decode()
            # print(data)
    except:
        logger.warning("Request timeout")
        return

    try:
        json_data = json.loads(data)
    except:
        logger.error("Get json data failed")
        return

    tracks = json_data["result"]["tracks"]
    # logger.debug("Tracks:\n{}".format(tracks))
    if (songs_change(tracks, res_path)):
        logger.info("Songs change detected")

        song = Song()
        playlist = [{"name":tracks[i]["name"], "id":tracks[i]["id"], "url":song.getUrlSong(tracks[i]["id"])} for i in range(TOP_NUM)]
        logger.debug("Playlist:\n{}".format(playlist))

        # Download the song and convert MP3 to OGG
        for i in range(len(playlist)):
            download_command = "wget -nc -O {path}/{id}.mp3 {url}".format(path=songs_path, id=playlist[i]["id"], url=playlist[i]["url"])
            err_code = os.system(download_command)
            if (err_code != 0):
                logger.warning("Fail to download or the file already exists")
            else:
                logger.info("Success download")
            
            convert_command = "ffmpeg -i {path}/{id}.mp3 -c:a libvorbis -n {path}/{id}.ogg 1>/dev/null 2>&1".format(path=songs_path, id=playlist[i]["id"])
            err_code = os.system(convert_command)
            if (err_code != 0):
                logger.warning("Fail to convert mp3 to ogg or the file already exists")
            else:
                logger.info("Success convert")

        # Record the result
        with open(res_path, 'w+') as f:
            for i in range(len(playlist)):
                f.write(str(playlist[i]["name"]) + '\n')
                f.write(str(playlist[i]["id"]) + '\n')
                f.write(str(playlist[i]["url"]) + '\n')
    
        f.close()

    else:
        logger.info("No song change")

    return

def clear_old_song(songs_path, platform):
    '''
    Clear the old song which is too old
    '''

    if platform == "windows":
        for file in os.listdir(songs_path):
            if file != ".gitkeep":
                mtime = int(os.path.getmtime("{}/{}".format(songs_path, file)))
                if time.time() - mtime >= CLEAR_INTERVAL * 86400:
                    logger.debug("last modified time: {} {}".format(file, mtime))
                    try:
                        os.remove("{}/{}".format(songs_path, file))
                        logger.info("Success clear old songs")
                    except:
                        logger.info("No old songs deleted")
    else:
        clear_command = "find {} -mtime +{} | xargs rm -f".format(songs_path, CLEAR_INTERVAL)
        err_code = os.system(clear_command)
        if (err_code != 0):
            logger.info("No old songs deleted")
        else:
            logger.info("Success clear old songs")

    return

def query_loop(config) -> None:
    while (1):
        clear_old_song(config.SONGS_PATH, config.PLATFORM)
        get_songs_rank(config.USER1_PLAYLIST_ID, config.USERNAME1, config.PLAYLIST_PATH, config.SONGS_PATH)
        get_songs_rank(config.USER2_PLAYLIST_ID, config.USERNAME2, config.PLAYLIST_PATH, config.SONGS_PATH)
        logger.info("Wake up in {} seconds".format(QUERY_INTERVAL))
        time.sleep(QUERY_INTERVAL)