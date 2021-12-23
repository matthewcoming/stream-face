from os import write
import sys
import subprocess as sp
import threading
import time

import ffmpeg
import cv2
import numpy as np
from PIL import Image

FFMPEG_BIN = "ffmpeg"
NODE_BIN = "node"
GET_STREAM_SCRIPT = "get_stream.js"

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

print('Getting stream for ', sys.argv[1])

get_stream_url = [ NODE_BIN, 
        GET_STREAM_SCRIPT, sys.argv[1]
        ]

get_stream_url_proc = sp.Popen(get_stream_url, stdout = sp.PIPE, bufsize=10**8)

if (get_stream_url_proc.wait() > 0):
    print('Failed to get stream url.')
    exit(1)
stream_url = get_stream_url_proc.stdout.read()

print('Using stream file: ', stream_url)

try:
    probe = ffmpeg.probe(stream_url)
except ffmpeg.Error as ex:
    print(ex.stderr)
    exit

gen = (stream for stream in probe['streams'] if stream['codec_type'] == 'video')
# _ = next(gen)
# _ = next(gen)
video_stream = next(gen)

width = int(video_stream['width'])
height = int(video_stream['height'])

out = (ffmpeg
    .input(stream_url)
    .output('-', format='rawvideo', pix_fmt='rgb24')
    .global_args("-loglevel", "warning")
    .run_async(pipe_stdout=True)
)

# buffer = np.zeros(0)
f_count = 1
bytes_in_image = width * height * 3
lock = threading.RLock()

detector = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

def write_image_func():
    global f_count
    while out.poll() is None:
        with lock:
            time_start = time.time()
            buffer = list(out.stdout.read(bytes_in_image))
            local_frame_count = f_count
            f_count += 1
        
        time_read = time.time()
        # Get Image
            # image = Image.fromarray(np.uint8(buffer).reshape(height, width, 3), "RGB")
        image = np.uint8(buffer).reshape(height, width, 3)
        # Find face, draw rectangle
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # rects = detector.detectMultiScale(grayscale, scaleFactor=1, minNeighbors=5, minSize=(30, 30))
        rects = detector.detectMultiScale(grayscale, minSize=(30, 30))
        for (i, (x, y, w, h)) in enumerate(rects):
	        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
	        cv2.putText(image, f"{sys.argv[1]}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
        time_after_draw = time.time()
        Image.fromarray(image).save(f"frames/frame {local_frame_count}.png", "PNG")
        time_end = time.time()
        print(f'time_read: {time_read - time_start}\ntime_array: {time_after_draw - time_read}\ntime_save: {time_end - time_after_draw}')

threads = []
# write_image_func()
for i in range(10):
    thread = threading.Thread(target=write_image_func)
    threads.append(thread)
    thread.start()

exit(0)
