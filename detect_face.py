from os import write
import sys
import subprocess as sp

import ffmpeg
import cv2
import numpy as np

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

if stream_url == b'':
    print("Stream not available.")
    exit()

print('Using stream file: ', stream_url)

try:
    probe = ffmpeg.probe(stream_url)
except ffmpeg.Error as ex:
    print(ex.stderr)
    exit()

# print(probe)
gen = (stream for stream in probe['streams'] if stream['codec_type'] == 'video')
# _ = next(gen)
# _ = next(gen)
video_stream = next(gen)

width = int(video_stream['width'])
height = int(video_stream['height'])

stream = (ffmpeg
    .input(stream_url)
    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    # .output(format="mp4", filename="output.mp4")
    .global_args("-loglevel", "warning")
    .run_async(pipe_stdout=True)
)

to_file = (ffmpeg
    .input(stream_url)
    .output(format="mp4", filename="output.mp4")
    .global_args("-loglevel", "warning")
    .run_async()
)


out = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}')
    .output(filename="udp://239.1.1.1:1234", format="mpegts", pix_fmt='yuv420p')
    .run_async(pipe_stdin=True)
)

while stream:
    # buffer = np.zeros(0)
    bytes_in_image = width * height * 3

    detector = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

    buffer = list(stream.stdout.read(bytes_in_image))
    image: np.ndarray = np.uint8(buffer).reshape(height, width, 3)

    # Find face, draw rectangle
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # rects = detector.detectMultiScale(grayscale, scaleFactor=1, minNeighbors=5, minSize=(30, 30))
    rects = detector.detectMultiScale(grayscale, minSize=(30, 30))

    for (i, (x, y, w, h)) in enumerate(rects):
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(image, f"{sys.argv[1]}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

    out.stdin.write(
        image.tobytes()
    )
