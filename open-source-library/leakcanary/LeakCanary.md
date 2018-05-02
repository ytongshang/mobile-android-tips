# LeakCanary

## ReferenceQueue

- [Java源码剖析——彻底搞懂Reference和ReferenceQueue](https://blog.csdn.net/Jesministrator/article/details/78786162)

## LeakCanary原理

- [LeakCanary核心原理源码浅析](https://blog.csdn.net/cloud_huan/article/details/53081120)

## 内存泄漏原理

- 引用超过变量的生命周期
    - static activities/views
    - 非静态内部类
    - 匿名类
    - Handler
    - Thread
    - TimerTask
- 系统服务的listener, broadcastreceiver/ContentObserver
- 资源关闭 cusor,File
- WebView
- C++代码