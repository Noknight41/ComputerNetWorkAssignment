# ComputerNetWorkAssignment

## PT_HA: \
How to run: \
python Server.py 5540 \
python ClientLauncher.py localhost 5540 5541 movie.Mjpeg \

## Thinh_Huy: \
Server's RTSP Default Port: 8000 \
RTP Default Port: 25000 \
Default File Name: movie.Mjpeg \
Prepared Command Line:
```
  sudo kill -9 $(lsof -t -i:8000) | sudo kill -9 $(lsof -t -i:25000)
```

Running Application:
```
 python Server.py
```
Server Main Thread is an RTSP socket listening for request
```
 python ClientLauncher.py
```
Client Main Thread are TK() objects handling UI buttons interleaved with RTSP socket sending message

Setup event:\
Client's RTSP Socket create connection with Server's RTSP Socket

Play event:\
Client opens RTP/UDP socket thread and writing image to TK's label thread, Server opens RTP/UDP socket thread sending each frame

Pause event:\
Server stop sending frame, Client not recognize any new frame sent will hang the display thread

Teardown:\
Server close RTP socket
Client calls exit() for thread RTP and thread Display, closes TK
