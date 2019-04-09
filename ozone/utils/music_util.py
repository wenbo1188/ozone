# encoding=utf8
import requests
import os
import json
import time
import warnings
import platform
import urllib.request as ur
import urllib.error as ue
import urllib.parse as up
from ..config import logger

warnings.filterwarnings("ignore")

REQ_TIMEOUT = 5
URL_BASE = "http://music.163.com/api/playlist/detail?id="
DOWNLOAD_URL = "http://music.163.com/song/media/outer/url?id="
REQ_TIMEOUT = 5
TOP_NUM = 5
QUERY_INTERVAL = 3600 * 6 # 6h
CLEAR_INTERVAL = 30 # 30days

def songs_change(tracks : dict, res_path : str) -> bool:
    '''
    Detect songs change
    '''
    
    if os.path.exists(res_path) and os.path.isfile(res_path):
        # path exists
        with open(res_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            num_of_line = len(lines)
            for num in range(num_of_line):
                if (num % 3 == 1):
                    #deal with the line
                    id = int(lines[num].strip('\n'))
                    if id not in [tracks[i]["id"] for i in range(TOP_NUM)]:
                        f.close()
                        return True
    else:
        # path not exists
        print("Path not exist:{}, creating one...".format(res_path))
        try:
            with open(res_path, 'w+', encoding="utf-8") as f:
                for i in range(TOP_NUM):
                    f.write(str(tracks[i]["name"]) + '\n')
                    f.write(str(tracks[i]["id"]) + '\n')
                    f.write((DOWNLOAD_URL+"{}.mp3").format(tracks[i]["id"]) + '\n')
        except BaseException as e:
            print("BaseException: {}".format(e))
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

        playlist = [{"name":tracks[i]["name"], "id":tracks[i]["id"], "url":(DOWNLOAD_URL+"{}.mp3").format(tracks[i]["id"])} for i in range(TOP_NUM)]
        logger.debug("Playlist:\n{}".format(playlist))

        # Download the song and convert MP3 to OGG
        for i in range(len(playlist)):
            download_url = playlist[i]["url"]
            headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
            req = requests.get(url=download_url, headers=headers)
            with open("{path}/{id}.mp3".format(path=songs_path, id=playlist[i]["id"]), "wb") as f:
                f.write(req.content)
                logger.info("Success download")
            
            platform_info = platform.platform()
            if "Windows" in platform_info:
                convert_command = "ffmpeg -i {path}/{id}.mp3 -c:a libvorbis -n {path}/{id}.ogg 1>NUL 2>&1".format(path=songs_path, id=playlist[i]["id"])
            else:
                convert_command = "ffmpeg -i {path}/{id}.mp3 -c:a libvorbis -n {path}/{id}.ogg 1>/dev/null 2>&1".format(path=songs_path, id=playlist[i]["id"])
            err_code = os.system(convert_command)
            if (err_code != 0):
                logger.warning("Fail to convert mp3 to ogg or the file already exists")
            else:
                logger.info("Success convert")

        # Record the result
        with open(res_path, 'w+', encoding="utf-8") as f:
            for i in range(len(playlist)):
                f.write(str(playlist[i]["name"]) + '\n')
                f.write(str(playlist[i]["id"]) + '\n')
                f.write(str(playlist[i]["url"]) + '\n')
    
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
