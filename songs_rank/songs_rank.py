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

url_base = "http://music.163.com/api/playlist/detail?id="
REQ_TIMEOUT = 5
TOP_NUM = 5
QUERY_INTERNAL = 3600 * 6 # 6h

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
    song = Song()
    playlist = [{"name":tracks[i]["name"], "id":tracks[i]["id"], "url":song.getUrlSong(tracks[i]["id"])} for i in range(TOP_NUM)]
    # print(playlist)
    
    with open(res_path, 'w+') as f:
        for i in range(len(playlist)):
            f.write(str(playlist[i]["name"]) + '\n')
            f.write(str(playlist[i]["id"]) + '\n')
            f.write(str(playlist[i]["url"]) + '\n')
    
    f.close()

    return

def query_loop() -> None:
    while (1):
        get_songs_rank(ProdConfig.USER1_PLAYLIST_ID, ProdConfig.USERNAME1)
        get_songs_rank(ProdConfig.USER2_PLAYLIST_ID, ProdConfig.USERNAME2)
        time.sleep(QUERY_INTERNAL)

if __name__ == '__main__':
    query_loop()
