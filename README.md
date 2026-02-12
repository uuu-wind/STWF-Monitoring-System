# STWF Monitoring System
A monitoring system suitable for solar thermal wind fields, developed using Vue3, incorporates ECharts, Three.js, and other technologies.

# 20260126修改
这是一个基于浙江大学（ZJU）节能减排竞赛而开发的网上平台，开发了一款适用于光热电站多用途挡风墙用于风力发电时的硬件-软件联合监测平台。
本平台通过STM32F103C8T6芯片和CH395Q芯片作为风机处理器获取信息并通过以太网UDP协议进行信息传递，在终端获取到信息后存入InfluxDB3时序数据库。通过Python的Flask库和Vue3分别构建后端服务器和前端服务器，实现了整体化的监测系统。

# 使用教程
1.将源码下载到本地  
2.使用VS Code或Trae在项目根目录打开项目，在项目根目录启用cmd  
3.输入：`cd backend`和`python app.py`启用后端  
4.新建一个cmd窗口，在新建的cmd窗口中输入`cd frontend`，`npm install`，待安装完成后输入`npm run dev`启用前端  
5.在浏览器输入前端地址（前端cmd窗口中会显示），即可使用本平台

# 20260126修改-2
关于如何在Docker中部署InfluxDB3和InfluxDB3-ui的方法见这篇文章：`https://blog.csdn.net/RudolphLiu/article/details/151001259`。  
后续会加入硬件部分

# 20260127修改
需要下载InfluxDB3-ui，可以使用这行代码：`docker pull influxdata/influxdb3-ui`。
在安装InfluxDB3-ui时，需要在本机上先创建一个文件夹，并在其中包含config，db，ssl三个文件夹。
关于在docker中安装InfluxDB3和InfluxDB3-ui的方法补充，在安装时，如果需要在cmd中安装容器（container），可以使用一下这两行代码（Windows和Linux的程序不同）  
`docker run -d ^
  --name influxdb3-core ^
  --network influx-network ^
  -p 8181:8181 ^
  -v ~/.influxdb3/data:/var/lib/influxdb3/data ^
  -v ~/.influxdb3/plugins:/var/lib/influxdb3/plugins ^
  influxdb:3-core ^
  influxdb3 serve ^
  --node-id=node0 ^
  --object-store=file ^
  --data-dir=/var/lib/influxdb3/data ^
  --plugin-dir=/var/lib/influxdb3/plugins
`  
`docker run --detach ^
  --name influxdb3-explorer ^
  --network influx-network ^
  --publish 8888:80 ^
  --publish 8889:8888 ^
  --volume (Windows本地绝对地址)\config:/app-root/config:ro ^
  --volume (Windows本地绝对地址)\InfluxDB\db:/db:rw ^
  --volume (Windows本地绝对地址)\InfluxDB\ssl:/etc/nginx/ssl:ro ^
  influxdata/influxdb3-ui ^
  --mode=admin
`

# 20260212修改  
新增了启动文件，直接运行.bat文件或.sh文件即可启动  
对于STM32部分，仍然需要验证
