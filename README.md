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
关于如何在Docker中部署InfluxDB3和InfluxDB-ui的方法见这篇文章：`https://blog.csdn.net/RudolphLiu/article/details/151001259`。  
后续会加入硬件部分
