# ComputerNetWorkAssignment

How to run: \n
python Server.py 5540
python ClientLauncher.py localhost 5540 5541 movie.Mjpeg

Update for Thinh_Huy:
Server's RTSP Default Port: 8000
RTP Default Port: 25000
Default File Name: movie.Mjpeg
\n
Prepared Command Line:
```
  sudo kill -9 $(lsof -t -i:8000) | sudo kill -9 $(lsof -t -i:25000)
```

Running Application:
```
 python Server.py
 python ClientLauncher.py
```
