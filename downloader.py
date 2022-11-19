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

stashstar = StashInterface({
    "Scheme": "http",
    "Host": os.environ.get("STASH_STAR_DOMAIN"),
    "Port": os.environ.get("STASH_STAR_PORT"),
})

ydl_opts_normal = {
    'outtmpl': '/media/%(webpage_url_domain)s/%(title)s.%(ext)s',
    'external_downloader': 'aria2c',
    'writeinfojson': True,
    'quiet': True,
}
ydl_opts_phprofile = {
    'outtmpl': '/media/'+os.environ.get("STASH_STAR_LIB")+'/%(webpage_url_domain)s/%(uploader)s/%(title)s.%(ext)s',
    'external_downloader': 'aria2c',
    'writeinfojson': True,
    'quiet': True,
    'max-downloads': 1,
}
mediapath = os.environ.get("STASH_MEDIA_PATH")


def test(urls):
    for line in urls:
        with YoutubeDL(ydl_opts_phprofile) as ydl:
            info = ydl.extract_info(line, download=False)
            perfid = stashstar.findPerformerIdWithName(
                info['entries'][0]['uploader'])
            if perfid == None:
                perfid = stashstar.createPerformerByName(
                    info['entries'][0]['uploader'])
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" created with ID: "+perfid)
            else:
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" found with ID: "+perfid)
            return perfid


def phprofile(urls):
    for line in urls:
        with YoutubeDL(ydl_opts_phprofile) as ydl:
            info = ydl.extract_info(line, download=False)
            perfid = stashstar.findPerformerIdWithName(
                info['entries'][0]['uploader'])
            if perfid == None:
                perfid = stashstar.createPerformerByName(
                    info['entries'][0]['uploader'])
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" created with ID: "+perfid)
            else:
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" found with ID: "+perfid)
            for video in info['entries']:
                error_code = ydl.download(video['webpage_url'])
                if(error_code != 0):
                    log.LogError(
                        "Download of Video: "+video['title']+" from profile "+video['uploader']+" failed ")
                else:
                    log.LogInfo(
                        "Download of Video: "+video['title']+" from profile "+video['uploader']+" successful")
            stashpath = mediapath + "stars/" + \
                info['entries'][0]['webpage_url_domain'] + "/" + \
                info['entries'][0]['uploader']+"/"
            stashstar.metadata_scan(stashpath)
            log.LogInfo("waiting 3 Minutes")
            sleep(int(os.environ.get("STASH_SCAN_TIMEOUT")))
            scenes = stashstar.findScenesByPathRegex(
                r'.*\.(?:[mM][pP]4|[wW][mM][vV])$')
            for video in info['entries']:
                for scene in scenes:
                    namefrompath = scene['path'].split("/")[-1]
                    log.LogDebug("Name from Path: "+namefrompath +
                                 "\nName from Video: "+video['title']+"."+video['ext'])
                    if scene['title'] == video['title']+"."+video['ext'] or video['title']+"."+video['ext'] == namefrompath:
                        log.LogInfo("Found Scne with ID: " +
                                    scene['id']+" and Title: "+scene['title'])
                        updatescene = {}
                        updatescene['id'] = scene['id']
                        updatescene['url'] = video['webpage_url']
                        updatescene['title'] = video['title']
                        updatescene['tag_ids'] = [
                            stashstar.findTagIdWithName("scrape")]
                        updatescene['performer_ids'] = perfid
                        if scene.get('rating'):
                            updatescene['rating'] = scene.get('rating')
                        log.LogInfo("Updating Scene with ID: " +
                                    updatescene['id']+" with video: "+video['title'])
                        stashstar.updateScene(updatescene)

    return scenes


def videoslist(urls):
    for line in urls:
        with YoutubeDL(ydl_opts_normal) as ydl:
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
