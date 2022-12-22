SPEAKER_SRC = "https://peersuma-album-media.s3.amazonaws.com/58/video_low_res_e16706e902d849d4885a0cce8506be86_00041.mp4"SPEAKER_START = 2SPEAKER_LEN = 10NAME = "ALAN RUDT"x=3y=3SPEAKER_START = (x+y)*2if SPEAKER_START > SPEAKER_LEN: SPEAKER_START = SPEAKER_START NAME_START = 3TITLE_START = 4LT_START = 3LTFONT_SRC = "https://templates.shotstack.io/basic/asset/font/manrope-extrabold.ttf"
data = {"SPEAKER_SRC": SPEAKER_SRC, "x": x, "NAME_START": NAME_START, "SPEAKER_LEN": SPEAKER_LEN, "NAME": NAME, "LT_START": LT_START, "TITLE_START": TITLE_START, "y": y, "LTFONT_SRC": LTFONT_SRC, "SPEAKER_START": SPEAKER_START, }

import json
print(json.dumps(data))
