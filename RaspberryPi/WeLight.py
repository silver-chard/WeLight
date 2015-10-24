#!/usr/bin/python
# coding=utf-8

import RPi.GPIO as GPIO
import time
import atexit
import urllib
import urllib2


def openlight(N):
    GPIO.output(N, GPIO.LOW)
    print "开灯"


def shutlight(N):
    GPIO.output(N, GPIO.HIGH)
    print "关灯"


def main(URLs, N):
    flag = 0  # flag 用于储存现在的灯状态 0:关闭 1:开启
    GPIO.setup(N, GPIO.OUT)
    GPIO.output(N, GPIO.HIGH)
    while True:
        info = urllib2.urlopen(urllib2.Request(URLs)).read(10)
        if info.find('open') != -1 and flag == 0:
            openlight(N)
            flag = 1
        if info.find('shut') != -1 and flag == 1:
            shutlight(N)
            flag = 0
        if info.find('nothing') != -1:
            flag = flag
        time.sleep(0.5)


atexit.register(GPIO.cleanup)
GPIO.setmode(GPIO.BOARD)
N = 7
URLs = 'http://silverchard.me/cgi-bin/light_flag.html'
main(URLs, N)
