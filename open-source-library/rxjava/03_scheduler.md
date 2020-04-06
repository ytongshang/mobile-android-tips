# scheduler

- [调度器类型](#调度器类型)
- [使用调度器](#使用调度器)
- [递归调度器](#递归调度器)
- [检查或设置取消订阅状态](#检查或设置取消订阅状态)
- [延时和周期调度器](#延时和周期调度器)

## 调度器类型

调度器类型 | 效
------|------
Schedulers.computation( )   | 用于计算任务，如事件循环或和回调处理，不要用于IO操作(IO操作请使用Schedulers.io())；默认线程数等于处理器的数量
Schedulers.from(executor)   | 使用指定的Executor作为调度器
Schedulers.immediate( )     | 在当前线程立即开始执行任务
Schedulers.io( )    | 用于IO密集型任务，如异步阻塞IO操作，这个调度器的线程池会根据需要增长；对于普通的计算任务，请使用Schedulers.computation()；Schedulers.io( )默认是一个CachedThreadScheduler，很像一个有线程缓存的新线程调度器
Schedulers.newThread( ) | 为每个任务创建一个新线程
Schedulers.trampoline( )    | 当其它排队的任务完成后，在当前线程排队开始执行

## 使用调度器

除了将这些调度器传递给RxJava的Observable操作符，你也可以用它们调度你自己的任务。下面的示例展示了Scheduler.Worker的用法：

```java

worker = Schedulers.newThread().createWorker();
worker.schedule(new Action0() {

    @Override
    public void call() {
        yourWork();
    }

});
// some time later...
worker.unsubscribe();

```

## 递归调度器

要调度递归的方法调用，你可以使用schedule，然后再用schedule(this)，示例：

```java

worker = Schedulers.newThread().createWorker();
worker.schedule(new Action0() {

    @Override
    public void call() {
        yourWork();
        // recurse until unsubscribed (schedule will do nothing if unsubscribed)
        worker.schedule(this);
    }

});
// some time later...
worker.unsubscribe();

```

## 检查或设置取消订阅状态

- Worker类的对象实现了Subscription接口，使用它的isUnsubscribed和unsubscribe方法，所以你可以在订阅取消时停止任务，或者从正在调度的任务内部取消订阅，示例：

- Worker同时是Subscription，因此你可以（通常也应该）调用它的unsubscribe方法通知可以挂起任务和释放资源了。

```java

Worker worker = Schedulers.newThread().createWorker();
Subscription mySubscription = worker.schedule(new Action0() {

    @Override
    public void call() {
        while(!worker.isUnsubscribed()) {
            status = yourWork();
            if(QUIT == status) { worker.unsubscribe(); }
        }
    }

});

```

## 延时和周期调度器

- 你可以使用schedule(action,delayTime,timeUnit)在指定的调度器上延时执行你的任务，下面例子中的任务将在500毫秒之后开始执行：

```java
someScheduler.schedule(someAction, 500, TimeUnit.MILLISECONDS);
```

- 使用另一个版本的schedule，schedulePeriodically(action,initialDelay,period,timeUnit)方法让你可以安排一个定期执行的任务，下面例子的任务将在500毫秒之后执行，然后每250毫秒执行一次：

```java
someScheduler.schedulePeriodically(someAction, 500, 250, TimeUnit.MILLISECONDS);
```