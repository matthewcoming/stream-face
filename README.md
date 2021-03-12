# stream-face

Stream Face is an application I'm building right now to capture a twitch m3u8 stream, use OpenCV to find any faces in the stream, and perform a "moving crop" on that face in real time.

In its current phase, it is able to capture the stream from twitch and subsequently write out a new image with a bounding box on any faces it detects.
