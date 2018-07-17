'''
Songs-rank scrapy
Provide data for ozone display
'''

import urllib.request as ur
import urllib.error as ue
import urllib.parse as up
import json
import time
from config import ProdConfig, logger
from music_util import Song
import os

url_base = "http://music.163.com/api/playlist/detail?id="
REQ_TIMEOUT = 5
TOP_NUM = 5
QUERY_INTERVAL = 3600 * 6 # 6h

def songs_change(tracks : dict, res_path : str) -> bool:
    num_of_line = 0
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
    return False

def get_songs_rank(user_id : str, name : str) -> None:
    '''
    Get songs rank from api and save result to certain txt
    '''

    url = url_base + user_id
    res_path = "{}/{}.txt".format(ProdConfig.PLAYLIST_PATH, name)

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
    logger.debug("Tracks:\n{}".format(tracks))
    if (songs_change(tracks, res_path)):
        logger.info("Songs change detected")

        song = Song()
        playlist = [{"name":tracks[i]["name"], "id":tracks[i]["id"], "url":song.getUrlSong(tracks[i]["id"])} for i in range(TOP_NUM)]
        logger.debug("Playlist:\n{}".format(playlist))

        # Download the song and convert MP3 to OGG
        for i in range(len(playlist)):
            download_command = "wget -nc -O {path}/{id}.mp3 {url}".format(path=ProdConfig.SONGS_PATH, id=playlist[i]["id"], url=playlist[i]["url"])
            err_code = os.system(download_command)
            if (err_code != 0):
                logger.warning("Fail to download or the file already exists")
            else:
                logger.info("Success download")
            
            convert_command = "ffmpeg -i {path}/{id}.mp3 -c:a libvorbis -n {path}/{id}.ogg 1>/dev/null 2>&1".format(path=ProdConfig.SONGS_PATH, id=playlist[i]["id"])
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

def query_loop() -> None:
    while (1):
        get_songs_rank(ProdConfig.USER1_PLAYLIST_ID, ProdConfig.USERNAME1)
        get_songs_rank(ProdConfig.USER2_PLAYLIST_ID, ProdConfig.USERNAME2)
        logger.info("Wake up in {} seconds".format(QUERY_INTERVAL))
        time.sleep(QUERY_INTERVAL)

if __name__ == '__main__':
    query_loop()
