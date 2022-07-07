
import requests
from bs4 import BeautifulSoup
import re
from qbittorrent import Client
import time
import os
import easygui
import subprocess
from pathlib import Path


class Nyaa:

    def __init__(self):

        self.search()

    def search(self):
        nyaa_search = input("Nyaa.si search: ")
        print("\nWhich release do you want to grab subtitles from?\n")
        r = requests.get('https://nyaa.si/?f=0&c=0_0&q={}'.format(nyaa_search))
        soup = BeautifulSoup(r.content, 'html.parser')
        search_links = soup.find_all("a")
        self.results = []
        regex_releases = re.findall(r'(<a href=\"\/view\/[0-9].*\">)', str(search_links))
        for result in regex_releases:
            regex_filename = re.search(r'(?:title\=.{1})(.*?)(?:.{1}>)(?:.*<i class=\"fa fa-fw fa-magnet\">)', result)
            regex_url = re.search(r'(?:<a href=.{1})(/view/[0-9]*.)(?:\" title=.{1})', result)

            self.results.append([regex_filename.group(1), regex_url.group(1)])
            print("[{}]".format(self.results.index([regex_filename.group(1), regex_url.group(1)])), self.results[-1][0])
        
        self.release_id = input("")
        if self.release_id == "cancel":
            self.search()
        else:
            qbit.download(self)

class qbit(Nyaa):
    
    def __init__(self):

        self.results = Nyaa.results
        self.release_id = Nyaa.release_id



    def download(self):
        clear = lambda: os.system('cls') #on Windows System

        qb = Client('http://127.0.0.1:8080/')
        link = "https://nyaa.si/{0}.torrent".format(self.results[int(self.release_id)][1]).replace("view", "download")
        torrents = qb.torrents(category="riko")
        if not torrents:
            print("Starting download...")
            qb.download_from_link(link=link, category="riko")
            time.sleep(2)      

            def get_size_format(b, factor=1024, suffix="B"):
                """
                Scale bytes to its proper byte format
                e.g:
                    1253656 => '1.20MB'
                    1253656678 => '1.17GB'
                """
                for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
                    if b < factor:
                        return f"{b:.2f}{unit}{suffix}"
                    b /= factor
                return f"{b:.2f}Y{suffix}"

            # return list of torrents

            torrents = qb.torrents(category="riko", filter="downloading")
            self.src_filepath = torrents[0]["save_path"] + torrents[0]["name"]

            while torrents: 
                torrents = qb.torrents(category="riko", filter="downloading")
                if torrents:
                    for torrent in torrents:
                        print("Filename:    ", torrents[0]["name"])
                        print("Completed:    {0} / {1}".format(get_size_format(torrents[0]["completed"]), get_size_format(torrents[0]["total_size"])))
                        print("DL Speed:    ", get_size_format(torrents[0]["dlspeed"]) + "/s")
                        time.sleep(2)
                        clear() 
                
                else:
                    qb.remove_category("riko")
                    print("Download completed.")
                    Sushi.run(self)
                    break

        if torrents:
            print(torrents[0])
            self.src_filepath = torrents[0]["save_path"] + torrents[0]["name"]
            print(self.src_filepath)
            #qb.remove_category("riko")
            print("Torrent already completed.")
            Sushi.run(self)

class Sushi(qbit):

    def __init__(self):
        self.src_filepath = qbit.src_filepath

    def run(self):
        src_filepath = Path(self.src_filepath)
        dst_filename = Path(easygui.fileopenbox(title="Which file subs should be shifted to?"))
        output_filename = Path(dst_filename.name)
        if "Erai" not in str(src_filepath): 
            subprocess.run(["sushi.exe", "--src", src_filepath, "--dst", dst_filename, "-o", output_filename.with_suffix('.ass')])
            subprocess.run(["ffmpeg.exe", "-i", dst_filename, "-i", output_filename.with_suffix('.ass'), "-map", "0", "-map", "1", 
                            "-c", "copy", src_filepath.with_suffix('.sushi.mkv')])
        else:
            subprocess.run(["ffmpeg.exe", "-i", src_filepath, "-c", "copy", "-map", "0:s:m:language:por", src_filepath.with_suffix('.ass')])
            subprocess.run(["sushi.exe", "--src", src_filepath, "--dst", dst_filename, "--script", src_filepath.with_suffix('.ass'),
                           "-o", output_filename.with_suffix('.ass')])
            subprocess.run(["ffmpeg.exe", "-i", dst_filename, "-i", output_filename.with_suffix('.ass'), "-map", "0", "-map", "1", 
                            "-c", "copy", src_filepath.with_suffix('.sushi.mkv')])
Nyaa()

#ffmpeg -i "D:\Anime trash\Releases\[Erai-raws] Kanojo Okarishimasu 2nd Season - 01 [480p][Multiple Subtitle][A164E9B4].mkv" -c copy -map 0:s:m:language:por out.ass

