# ANR

## 相关文章

- [Input系统—ANR原理分析](http://gityuan.com/2017/01/01/input-anr/)
- [理解Android ANR的触发原理](http://gityuan.com/2016/07/02/android-anr/)
- [彻底理解安卓应用无响应机制](http://gityuan.com/2019/04/06/android-anr/)
- [理解Android ANR的信息收集过程](http://gityuan.com/2016/12/02/app-not-response/)
- [BlockCanary — 轻松找出Android App界面卡顿元凶](http://blog.zhaiyifan.cn/2016/01/16/BlockCanaryTransparentPerformanceMonitor/)

## ANR产生的场景

- Service Timeout
    - 对于前台服务，则超时为SERVICE_TIMEOUT = 20s；
    - 对于后台服务，则超时为SERVICE_BACKGROUND_TIMEOUT = 200s
- BroadcastQueue Timeout
    - 对于前台广播，则超时为BROADCAST_FG_TIMEOUT = 10s
    - 对于后台广播，则超时为BROADCAST_BG_TIMEOUT = 60s
- ContentProvider Timeout
    - CONTENT_PROVIDER_PUBLISH_TIMEOUT = 10s
- InputDispatching Timeout: 输入事件分发超时5s，包括按键和触摸事件

## ANR产生的源码原因

- ANR是一套监控Android应用响应是否及时的机制，可以把发生ANR比作是引爆炸弹，那么整个流程包含三部分组成：
    - **埋定时炸弹**：中控系统(system_server进程)启动倒计时，在规定时间内如果目标(应用进程)没有干完所有的活，则中控系统会定向炸毁(杀进程)目标。
    - **拆炸弹**：在规定的时间内干完工地的所有活，并及时向中控系统报告完成，请求解除定时炸弹，则幸免于难。
    - **引爆炸弹**：中控系统立即封装现场，抓取快照，搜集目标执行慢的罪证(traces)，便于后续的案件侦破(调试分析)，最后是炸毁目标。

## ANR的常见原因

- 耗时的网络访问，大量的数据读写，数据库操作
- 硬件操作（比如camera)
- 调用thread的join()方法、sleep()方法、wait()方法或者等待线程锁的时候
- 其他线程持有锁，导致主线程等待超时
- service binder的数量达到上限
- system server中发生WatchDog ANR
- service忙导致超时无响应
- 其它线程终止或崩溃导致主线程一直等待

## ANR检测

### BlockCanary

- 原理是Looper.loop对于消息分发的前后打印,计算这两个打印之前的时间差

```java
public static void loop() {
    ...

    for (;;) {
        ...

        // This must be in a local variable, in case a UI event sets the logger
        Printer logging = me.mLogging;
        if (logging != null) {
            logging.println(">>>>> Dispatching to " + msg.target + " " +
                    msg.callback + ": " + msg.what);
        }

        msg.target.dispatchMessage(msg);

        if (logging != null) {
            logging.println("<<<<< Finished to " + msg.target + " " + msg.callback);
        }

        ...
    }
}
```

- Cpu Profile
- Debug.startMethodTracing
