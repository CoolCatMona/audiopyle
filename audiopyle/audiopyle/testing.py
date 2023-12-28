from audiopyle import audio
import json

fi = audio.Audio._from_filepath(
    "C:\\Users\\Mona\\Desktop\\Music July\\Pablo Dread & Broken Lip - Azzido Domingo feat. Anna Milman.mp3"
)

with open("test.json", "w") as f:
    json.dump(fi._finfo, f)
