# Subject

- [Subject类型](#subject类型)
- [PublishSubject](#publishsubject)
- [ReplaySubject](#replaysubject)
- [BehaviorSubject](#behaviorsubject)
- [AsyncSubject](#asyncsubject)

## Rxjava2

- 在Rxjava2中对应着Processor

## Subject类型

- 继承了Observable，也实现了Observer接口
- 如果你把 Subject 当作一个 Subscriber 使用，注意不要从多个线程中调用它的onNext方法（包括其它的on系列方法），这可能导致同时（非顺序）调用，这会违反Observable协议，给Subject的结果增加了不确定性

```java
mySafeSubject = new SerializedSubject( myUnsafeSubject );
```

## PublishSubject

- PublishSubject 是最直接的一个 Subject。当一个数据发射到 PublishSubject 中时，PublishSubject 将立刻把这个数据发射到订阅到该 subject 上的所有 subscriber 中.

```java
PublishSubject<Integer> subject = PublishSubject.create();
    subject.onNext(1);
    subject.subscribe(System.out::println);
    subject.onNext(2);
    subject.onNext(3);
    subject.onNext(4);

2
3
4
```

## ReplaySubject

- ReplaySubject 可以缓存所有发射给他的数据。当一个新的订阅者订阅的时候，缓存的所有数据都会发射给这个订阅者。 由于使用了缓存，所以每个订阅者都会收到所有的数据
- 缓存所有的数据并不是一个十分理想的情况，如果 Observable 事件流运行很长时间，则缓存所有的数据会消耗很多内存。
- 可以限制缓存数据的数量和时间。 ReplaySubject.createWithSize 限制缓存多少个数据；而 ReplaySubject.createWithTime 限制一个数据可以在缓存中保留多长时间。

```java
ReplaySubject<Integer> s = ReplaySubject.create();
s.subscribe(v -> System.out.println("Early:" + v));
s.onNext(0);
s.onNext(1);
s.subscribe(v -> System.out.println("Late: " + v));
s.onNext(2);

Early:0
Early:1
Late: 0
Late: 1
Early:2
Late: 2
```

## BehaviorSubject

- BehaviorSubject 只保留最后一个值。 等同于限制 ReplaySubject 的个数为 1 的情况。在创建的时候可以指定一个初始值，这样可以确保党订阅者订阅的时候可以立刻收到一个值

```java
BehaviorSubject<Integer> s = BehaviorSubject.create();
s.onNext(0);
s.onNext(1);
s.onNext(2);
s.subscribe(v -> System.out.println("Late: " + v));
s.onNext(3);

Late:  2
Late:  3
```

## AsyncSubject

- AsyncSubject 也缓存最后一个数据。区别是 AsyncSubject 只有当数据发送完成时（onCompleted 调用的时候）才发射这个缓存的最后一个数据。可以使用 AsyncSubject 发射一个数据并立刻结束。

```java
AsyncSubject<Integer> s = AsyncSubject.create();
s.subscribe(v -> System.out.println(v));
s.onNext(0);
s.onNext(1);
s.onNext(2);
s.onCompleted();

2
```