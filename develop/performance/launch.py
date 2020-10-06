# -*- coding: utf-8 -*-

import os
import re
import time


class MobileQQTest(object):

    def __init__(self, num):
        self.data = []
        self.num = num
        self.app = 'com.guang.client'
        self.activity = 'com.guang.client.SplashActivity'

    def check_devices(self):
        '''检查设备是否连接成功，如果成功返回True，否则返回False'''
        try:
            deviceInfo = os.popen('adb devices').read()
            if 'device' in deviceInfo.split('\n')[1]:
                print('=' * 21, '已连接设备,开始测试', '=' * 21)
                print(self.deviceInfo())
                return True
            else:
                return False
        except Exception as e:
            print(e)

    def deviceInfo(self):
        '''获取设备基础信息(如：厂商、型号、系统版本)'''
        deviceName = os.popen('adb shell getprop ro.product.model').read()
        platformVersion = os.popen(
            'adb shell getprop ro.build.version.release').read()
        producer = os.popen('adb shell getprop ro.product.brand').read()
        return "手机型号：%s %s，系统版本：Android %s" % (
            producer.replace('\n', ''), deviceName.replace('\n', ''), platformVersion.replace('\n', ''))

    def start_adb(self):
        '''运行adb命令，并记录启动耗时'''
        start = 'adb shell am start -W %s/%s' % (self.app, self.activity)
        data = re.findall(r'.*ThisTime: (.*?)TotalTime:(.*?)WaitTime: (.*?)Complete',
                          os.popen(start).read().replace('\n', ''))
        if len(data) == 0:
            print("adb命令执行出错，数据为空")
        else:
            self.data.append(int(data[0][0]))
            return data

    def stop_adb(self):
        '''结束程序运行'''
        stop = 'adb shell am force-stop %s' % self.app
        os.popen(stop)

    def run_test_cold(self):
        '''app 冷启动耗时测试'''
        self.data = []
        if self.check_devices() == True:
            self.stop_adb()
            for i in range(self.num):
                print('=' * 20, '冷启动测试：第%d次运行' % (i + 1), '=' * 20)
                self.stop_adb()
                time.sleep(3)
                test = self.start_adb()
                print("ThisTime:%s,TotalTime:%s,WaitTime:%s" %
                      (test[0][0], test[0][1], test[0][2]))
                time.sleep(3)
            self.stop_adb()
            print('\n冷启动%s次平均耗时为：%s' %
                  (len(self.data), sum(self.data) / len(self.data)))

        else:
            print("未连接安卓设备,请连接设备（3秒后重试）")
            while True:
                time.sleep(3)
                self.run_test_cold()

    def run_test_hot(self):
        '''app 热启动耗时测试'''
        self.data = []
        if self.check_devices() == True:
            os.popen('adb shell am start -W %s/%s' % (self.app, self.activity))
            time.sleep(3)
            for i in range(self.num):
                print('=' * 20, '热启动测试：第%d次运行' % (i + 1), '=' * 20)
                os.popen('adb shell input keyevent 3')
                time.sleep(3)
                test = self.start_adb()
                time.sleep(3)
                print("ThisTime:%s,TotalTime:%s,WaitTime:%s" %
                      (test[0][0], test[0][1], test[0][2]))
            self.stop_adb()
            print('\n热启动%s次平均耗时为：%s' %
                  (len(self.data), sum(self.data) / len(self.data)))

        else:
            print("未连接安卓设备,请连接设备（3秒后重试）")
            while True:
                time.sleep(3)
                self.run_test_hot()


if __name__ == '__main__':
    apptest = MobileQQTest(4)
    apptest.run_test_cold()
    apptest.run_test_hot()
