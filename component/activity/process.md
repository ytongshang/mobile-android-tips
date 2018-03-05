# Processes

- [android 进程简介](#android-进程简介)
- [Process 分类](#process-分类)
    - [Foreground process](#foreground-process)
    - [Visible process](#visible-process)
    - [Service process](#service-process)
    - [Background process](#background-process)
    - [Empty process](#empty-process)
    - [process 回收](#process-回收)
- [跨进程通信](#跨进程通信)

## android 进程简介

- 默认情况下，一个应用的所有的component运行在同一个process中

### android:process

- 通过在manifest指定android:process属性,可分别指定四大组件运行的进程名
- application也可以指定android:process属性，为所有的component指定一个默认的process
- 不指定进程名时，使用包名作为进程名
- 如果进程名是以冒号开头的，则这个进程是应用的私有进程
- 如果进程名是以字符开头的，且符合包名规范，则这个进程是全局的

```xml
<service
    android:name="com.xiaomi.push.service.XMPushService"
    android:enabled="true"
    android:process=":pushservice" />
```

### android:multiprocess

- 只有provider和activity定义了android:multiprocess，但一般不要在activity中使用。
- 如果android:multiprocess为true，则每个访问provider的应用都会自己创建一个ContentProvider实例
 优势：避免跨进程通信，提高数据访问效率，弊端：多个实例导致系统内存消耗变大，且难以处理多个进程之间的数据同步问题

### 不同APP运行在同一进程

- 如果需要两个不同APK中的组件运行于同一个进程，需要以下三个条件：
  - 两个应用程序使用相同的android:sharedUserId
  - 两个应用使用相同的keystore进行签名
  - 为组件设置相同的android:process

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.shareusertesta"
    android:versionCode="1"
    android:versionName="1.0"
    android:sharedUserId="com.example">
```

### Process的实际使用

- 子进程可以分担主进程的内存压力
- 在主进程Crash时，子进程中的功能不受影响
- 子进程的Application#onCreate中可以跳过一些不必要的初始化

## Process 分类

### Foreground process

- 用户正在使用的process，任何时候，android系统都只有一个foreground process
- 以下情况所在的process被认为是foreground process：
    - 拥有一个处于onResume()状态的activity;
    - 拥有一个与处于onResume()的activity相绑定的service;
    - 拥有一个调用了startForeground()方法的service;
    - 拥有一个正在执行生命周期函数(onCreate(), onStart(), oronDestroy())的service;
    - 拥有正在执行onReceive（）方法的broadcastreceiver
- 一般情况下，foreground procee是不会被detroy的

### Visible process

- 没有处于foreground 的componet，但是仍然能够影响用户的所见
- 以下情况的process被认为是visible process：
    - 拥有一个activity对于用户来说是可见的，但是不处于onResume（）状态
    - 拥有一个与一个visible activity绑定的service
- 一般情况下，visible procee也是不会被detroy的

### Service process

- 一个正运行service的process(调用了service 的startService()方法),比如下载东西，播放音乐
- service process也被认为是很重要的，除非内存不足，也不会被destroy

### Background process

- 拥有处于onPause（）状态的acitivty 的process
- 同一时间可以有很多个background processes, 一般被存放在lru list(least recently used)中
- 系统可以在任何时候destroy 掉background process

### Empty process

- 不含有任何activity componet
- 保留这种process一般是为了缓存目的，为了下一次启动更快

### process 回收

- android 系统总是尽可能的保存所有的process，但是有时候有可能需要回收内存，
 根据process的状态和运行在 process中的component,形成了一个优先级序列，当需要回收内存时，最低优先级的被remove掉

- android 总是将一个process标注为它能达到的最高级，比如有一个onResume（）的activity,同时也有正在播放音乐的service,
 这时这个process被认为是foreground process

- process的优先级也会与其它process有关，比如process A 中的content provider为process B中提供数据，
 那么A被认为优先级比B高，至少是和B一样高

- service process的优先级比background proces的优先级要高，所以需要消耗很长时间的操作一般被放在service中，而不是放在一个back thread中，比如上传图片等等，所以在broadcastreceiver中，如果要启动一个长时间操作，也应当启用一个service，而不是用back thread

## 跨进程通信