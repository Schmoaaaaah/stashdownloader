from time import sleep
from stash_interface import StashInterface
import os
from yt_dlp import YoutubeDL
import log as log

stash = StashInterface({
    "Scheme": "http",
    "Host": os.environ.get("STASH_DOMAIN"),
    "Port": os.environ.get("STASH_PORT"),
})

ydl_opts = {
    'outtmpl': '/media/%(webpage_url_domain)s/%(title)s.%(ext)s',
    'external_downloader': 'aria2c',
    'writeinfojson': True,
    'quiet': True,
}
mediapath=os.environ.get("STASH_MEDIA_PATH")


def main():
    f = open("./links.txt", "r")
    for line in f:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(line, download=False)
            log.LogInfo("Identified Video as: "+info.get('title'))
            error_code = ydl.download(line)
            if(error_code != 0):
                log.LogError("Download of Video: "+info.get('title')+" failed")
            else:
                log.LogInfo("Download of Video: " +
                            info.get('title')+" successful")
                stashpath = mediapath + \
                    info.get('webpage_url_domain')+"/"
                stash.metadata_scan(stashpath)
                sleep(10)
                scenes = stash.findScenesByPathRegex(
                    r'.*\.(?:[mM][pP]4|[wW][mM][vV])$')
                for scene in scenes:
                    if scene['title'] == "":
                        pathstrip = scene['path'].split("/")
                        titel = pathstrip[len(pathstrip)-1].split(".")[0]
                        updatescene = {}
                        updatescene['id'] = scene['id']
                        updatescene['url'] = line[:-1]
                        updatescene['title'] = titel
                        updatescene['tag_ids'] = [
                            stash.findTagIdWithName("scrape")]
                        if scene.get('rating'):
                            updatescene['rating'] = scene.get('rating')
                        log.LogInfo("Updating Scene with ID: " +
                                    updatescene['id']+" with URL: "+line)
                        stash.updateScene(updatescene)
                    elif scene['title'] == info['title']:
                        pathstrip = scene['path'].split("/")
                        titel = pathstrip[len(pathstrip)-1].split(".")[0]
                        updatescene = {}
                        updatescene['id'] = scene['id']
                        updatescene['url'] = line[:-1]
                        updatescene['title'] = scene['title']
                        updatescene['tag_ids'] = [
                            stash.findTagIdWithName("scrape")]
                        if scene.get('rating'):
                            updatescene['rating'] = scene.get('rating')
                        log.LogInfo("Updating Scene with ID: " +
                                    updatescene['id']+" with URL: "+line)
                        stash.updateScene(updatescene)
    f.close()


main()
