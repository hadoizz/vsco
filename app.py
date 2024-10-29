from flask import Flask, jsonify, request
import urllib.request as ur
import json
import re
import traceback as tb

app = Flask(__name__)

def download(vsco_media_url, get_video_thumbnails=False, save=False):
    request_header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"}
    request = ur.Request(vsco_media_url, headers=request_header)
    data = ur.urlopen(request).read()

    # Clean the data and extract JSON
    try:
        data_cleaned_1 = str(data).split("<script>window.__PRELOADED_STATE__ =")[1]
        data_cleaned_2 = str(data_cleaned_1).split("</script>")[0]
        data_cleaned_3 = str(data_cleaned_2).strip()
        data_cleaned_4 = str(data_cleaned_3).replace("\\x", "\\u00")
        data_cleaned_5 = re.sub(r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'', data_cleaned_4)

        json_data = json.loads(data_cleaned_5)
    except Exception as e:
        print("ERROR: Failed to load json data!")
        tb.print_exc()
        return {"error": "Failed to load JSON data."}

    media_urls = []
    try:
        medias = json_data["medias"]["byId"]
        for media in medias:
            info = medias[media]["media"]
            # Always include video URLs and exclude thumbnail fetching
            if bool(info["isVideo"]):
                media_url = "https://" + str(info["videoUrl"].encode().decode("unicode-escape"))
                media_urls.append({"type": "video", "url": media_url})
            elif not bool(info["isVideo"]) and not get_video_thumbnails:
                media_url = "https://" + str(info["responsiveUrl"].encode().decode("unicode-escape"))
                media_urls.append({"type": "image", "url": media_url})
    except Exception as e:
        print("ERROR: Failed to extract image/video location!")
        tb.print_exc()
        return {"error": "Failed to extract media URLs."}

    return media_urls

@app.route('/get/<path:url>', methods=['GET'])
def get_media(url):
    media_urls = download(url)
    if isinstance(media_urls, dict) and "error" in media_urls:
        return jsonify(media_urls), 500

    # Return the media URLs in JSON format
    return jsonify({"media": media_urls})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Updated to use port 8000
