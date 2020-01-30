# AMS

- [深入理解ActivityManagerService](https://blog.csdn.net/Innost/article/details/47254381?utm_source=app)

## 相关类

### ActivityManagerService

- ActivityManagerService是一个位于system_server进程的服务
- IActivityManager是AMS的业务接口，IActivityManager.Stub继承binder，实现接口IActivityManager，但是具体的业务仍然没有实现，IActivityManager.Stub.Proxy是对应的代理类
- ActivityManagerService是IActivityManager.Stub的具体业务实现类

### ActivityThread

- IApplicationThread是应用提供给AMS的业务接口，并有对应的IApplicationThread.Stub和IApplicationThread.Stub.Proxy
- ApplicationThread继承IApplicationThread.Stub.Proxy，相当于具体的业务实现类
- ActivityThread一方面是应用的主线程，另一方面它是应用与AMS打交道的外交官

### Instrumentation

- 用于实现应用程序测试代码的基类,允许您监视系统与应用程序的所有交互

### ActivityManager

- 客户端使用ActivityManager类

### ActivityRecord,TaskRecord,ProcessRecord

- AMS进程中的概念
- AMS提供了一个ArrayList mHistory来管理所有的activity，activity在AMS中的形式是ActivityRecord，task在AMS中的形式为TaskRecord，进程在AMS中的管理形式为ProcessRecord

### ActivityStack,ActivityStackSupervisor

- ActivityStack负责单个Activity栈的状态和管理
- ActivityStackSupervisor负责所有Activity栈的管理