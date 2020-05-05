# Tcp Chat App

![python:3.8](https://img.shields.io/badge/python-3.8-blue)
![tornado:6.0.4](https://img.shields.io/badge/tornado-6.0.4-orange)
![asyncio:3.4.3](https://img.shields.io/badge/asyncio-3.4.3-blueviolet)
![build:passing](https://img.shields.io/badge/build-passing-green)

A simple Tcp chat app for multiple humans(or robots, depending on where your priorities are) that uses ```tornado.web.RequestHandler``` without invoking the ```tornado.web.WebsocketHandler``` module


Tornado is a Python web framework and asynchronous networking library. 
By using non-blocking network I/O, Tornado can scale to tens of thousands of open connections, 
making it ideal for long polling, WebSockets, and other applications that require a long-lived connection to each user.
Read the [docs](https://www.tornadoweb.org/en/stable/)

## Requirements

- Python 3.7+ 

    - [download](https://www.python.org/downloads/)
    
    - [documentation](https://docs.python.org/3/)

- Tornado 
   ```
   pip install Tornado
   ```
    - [documentation](https://www.tornadoweb.org/en/stable/)
- Asyncio
  ```
  pip install asyncio
  ```
    - [documentation](https://pypi.org/project/asyncio/)


## Demo

 Here's a screen recording showing multiple clients(2 clients chatting with each other inreal time). I made it so that the server can handle 30 connections.
 
![demo2](https://user-images.githubusercontent.com/39020723/80954532-3a764980-8e06-11ea-8427-af721225031f.gif)

