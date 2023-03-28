from time import sleep
from stash_interface import StashInterface
import os
from yt_dlp import YoutubeDL
import log as log


def controller(urls, stashurl, method):
    mediapath = os.environ.get("STASH_MEDIA_PATH")+stashurl.split(':')[0]+"/"
    ydl_opts = {
        'outtmpl': mediapath+'/%(webpage_url_domain)s/%(uploader)s/%(title)s.%(ext)s',
        'external_downloader': 'aria2c',
        'writeinfojson': True,
        'quiet': True,
    }
    stash = StashInterface({
        "Scheme": "http",
        "Host": stashurl.split(':')[0],
        "Port": stashurl.split(':')[1],
    })
    if method == 'videos':
        return videoslist(urls, stash, ydl_opts, mediapath)
    elif method == 'phprofile':
        return phprofile(urls, stash, ydl_opts, mediapath)
    elif method == 'test':
        return test(urls, stash, ydl_opts, mediapath)
    else:
        return "uknown method"


def test(urls, stash, ydl_opts, mediapath):
    videos = stash.findScenesByPathRegex(r'.*\.(?:[mM][pP]4|[wW][mM][vV])$')
    for video in videos:
        return video['path'].split('/')[-1]


def phprofile(urls, stash, ydl_opts, mediapath):
    for line in urls:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(line, download=False)
            perfid = stash.findPerformerIdWithName(
                info['entries'][0]['uploader'])
            if perfid == None:
                perfid = stash.createPerformerByName(
                    info['entries'][0]['uploader'])
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" created with ID: "+perfid)
            else:
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" found with ID: "+perfid)
            for video in info['entries']:
                error_code = ydl.download(video['webpage_url'])
                if (error_code != 0):
                    log.LogError(
                        "Download of Video: "+video['title']+" from profile "+video['uploader']+" failed ")
                else:
                    log.LogInfo(
                        "Download of Video: "+video['title']+" from profile "+video['uploader']+" successful")
            stashpath = mediapath + "stars/" + \
                info['entries'][0]['webpage_url_domain'] + "/" + \
                info['entries'][0]['uploader']+"/"
            stash.metadata_scan(stashpath)
            log.LogInfo("waiting 3 Minutes")
            sleep(int(os.environ.get("STASH_SCAN_TIMEOUT")))
            scenes = stash.findScenesByPathRegex(
                r'.*\.(?:[mM][pP]4|[wW][mM][vV])$')
            for video in info['entries']:
                for scene in scenes:
                    if scene['title'] == video['title']+"."+video['ext'] or video['title']+"."+video['ext'] == scene['path'].split("/")[-1]:
                        log.LogInfo("Found Scne with ID: " +
                                    scene['id']+" and Title: "+scene['title'])
                        updatescene = {}
                        updatescene['id'] = scene['id']
                        updatescene['url'] = video['webpage_url']
                        updatescene['title'] = video['title']
                        updatescene['tag_ids'] = [
                            stash.findTagIdWithName("scrape")]
                        updatescene['performer_ids'] = perfid
                        if scene.get('rating'):
                            updatescene['rating'] = scene.get('rating')
                        log.LogInfo("Updating Scene with ID: " +
                                    updatescene['id']+" with video: "+video['title'])
                        stash.updateScene(updatescene)
    return scenes


def videoslist(urls, stash, ydl_opts, mediapath):
    for line in urls:
        updatescenes = []
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(line, download=False)
            log.LogInfo("Identified Video as: "+info.get('title'))
            error_code = ydl.download(line)
            if (error_code != 0):
                log.LogError("Download of Video: "+info.get('title')+" failed")
                return "Download of Video: "+info.get('title')+" failed"
            else:
                log.LogInfo("Download of Video: " +
                            info.get('title')+" successful")
                stashpath = mediapath + \
                    info.get('webpage_url_domain')+"/"+info.get('uploader')+"/"
                stash.metadata_scan(stashpath)
                sleep(10)
                scenes = stash.findScenesByPathRegex(
                    r'.*\.(?:[mM][pP]4|[wW][mM][vV])$')
                for scene in scenes:
                    if scene['path'].split('/')[-1] == info['title']+"."+info['ext'] or scene['title'] == info['title']+"."+info['ext']:
                        pathstrip = scene['path'].split("/")
                        titel = pathstrip[len(pathstrip)-1].split(".")[0]
                        updatescene = {}
                        updatescene['id'] = scene['id']
                        updatescene['url'] = info.get('webpage_url')
                        updatescene['title'] = titel
                        updatescene['tag_ids'] = [
                            stash.findTagIdWithName("scrape")]
                        if scene.get('rating'):
                            updatescene['rating'] = scene.get('rating')
                        log.LogInfo("Updating Scene with ID: " +
                                    updatescene['id']+" with URL: "+line)
                        stash.updateScene(updatescene)
                        updatescenes += updatescene
        return updatescenes
