# ComputerNetWorkAssignment

## Alpha 1.1 versions:
Following the instruction of Alpha 1.0, except when running Server:
```
  python Server.py
 ```
However, if you strickly follow the Alpha 1.0, it still works!

## Alpha 1.0:
How to run: 
1. Open 2 separate tabs of terminal. 
2. Change directory to the folder containing the code.
3. For the first tab, type: 
```
  python Server.py 8000
```
 For the second one, type
 ```
  python ClientLauncher.py
 ```
5. Enjoy!

## PT_HA: 
How to run: \
python Server.py 5540 \
python ClientLauncher.py localhost 5540 5541 movie.Mjpeg \

## Thinh_Huy: 
**Notice**: require opencv \
Install opencv: pip install opencv-contrib-python \
Default File Name: movie.Mjpeg \
Prepared Command Line:
```
  sudo kill -9 $(lsof -t -i:<server port>) | sudo kill -9 $(lsof -t -i:<rtp port>)
```

Running Application:
```
 python Server.py <server port>
```
Server Main Thread is an RTSP socket listening for request
```
 python ClientLauncher.py <host address> <server port> <rtp port> <filename>
```
**Switch**\
Choosing old file brings client back to READY state\
Choosing new file triggers TEARDOWN event to close rtp,videoplayer threads. Reclick setup button for new connection with new filename
**Note**: Currently not applicable for mjpeg from internet

