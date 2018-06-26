'''
Songs-rank scrapy
Provide data for ozone display
'''

import urllib.request as ur
import urllib.error as ue
import urllib.parse as up
import json
import time
from config import ProdConfig
from music_util import Song
import os

url_base = "http://music.163.com/api/playlist/detail?id="
REQ_TIMEOUT = 5
TOP_NUM = 5
QUERY_INTERNAL = 3600 * 6 # 6h

def songs_change(tracks : dict, res_path : str) -> bool:
    num_of_line = 0
    with open(res_path, 'r') as f:
        try:
            line = f.readline()
            num_of_line += 1
        except:
            print("fail to read oneline")

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
                print("fail to read oneline")

    f.close()
    return False

def get_songs_rank(user_id : str, name : str) -> None:
    '''
    Get songs rank from api and save result to certain txt
    '''

    url = url_base + user_id
    res_path = "{}.txt".format(name)

    req = ur.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36)")
    try:
        with ur.urlopen(req, timeout = REQ_TIMEOUT) as response:
            data = response.read().decode()
            # print(data)
    except:
        print("request timeout")
        return

    try:
        json_data = json.loads(data)
    except:
        print("get json data failed")
        return

    tracks = json_data["result"]["tracks"]
    # print(tracks)
    if (songs_change(tracks, res_path)):
        print("songs change")

        song = Song()
        playlist = [{"name":tracks[i]["name"], "id":tracks[i]["id"], "url":song.getUrlSong(tracks[i]["id"])} for i in range(TOP_NUM)]
        # print(playlist)

        # Download the song and convert MP3 to WAV
        for i in range(len(playlist)):
            download_command = "wget -nc -O ../ozone/static/songs/{}.mp3 {}".format(playlist[i]["id"], playlist[i]["url"])
            err_code = os.system(download_command)
            if (err_code != 0):
                print("fail to download")
            else:
                print("success download")
            
            convert_command = "mpg123 -w ../ozone/static/songs/{}.wav ../ozone/static/songs/{}.mp3".format(playlist[i]["id"], playlist[i]["id"])
            err_code = os.system(convert_command)
            if (err_code != 0):
                print("fail to convert mp3 to wav")
            else:
                print("success convert")

        # Record the result
        with open(res_path, 'w+') as f:
            for i in range(len(playlist)):
                f.write(str(playlist[i]["name"]) + '\n')
                f.write(str(playlist[i]["id"]) + '\n')
                f.write(str(playlist[i]["url"]) + '\n')
    
        f.close()

    else:
        print("no change")

    return

def query_loop() -> None:
    while (1):
        get_songs_rank(ProdConfig.USER1_PLAYLIST_ID, ProdConfig.USERNAME1)
        get_songs_rank(ProdConfig.USER2_PLAYLIST_ID, ProdConfig.USERNAME2)
        time.sleep(QUERY_INTERNAL)

if __name__ == '__main__':
    query_loop()
