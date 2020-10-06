# Binder

- [谈一谈Binder的原理和实现一次拷贝的流程](https://blog.csdn.net/AndroidStudyDay/article/details/93749470)
- [一篇文章了解相见恨晚的 Android Binder 进程间通讯机制](https://blog.csdn.net/freekiteyu/article/details/70082302)
- [Android Bander设计与实现 - 设计篇](https://blog.csdn.net/universus/article/details/6211589)

## 用户空间/内核空间

-   **进程隔离**
-   **用户空间/内核空间**，系统调用是用户空间访问内核空间的唯一方式，保证了所有的资源访问都是在内核的控制下进行的，避免了用户程序对系统资源的越权访问，提升了系统安全性和稳定性
-   当一个任务（进程）执行系统调用而陷入内核代码中执行时，称进程处于**内核运行态（内核态）**。此时处理器处于特权级最高的（0级）内核代码中执行。当进程处于内核态时，执行的内核代码会使用当前进程的内核栈。每个进程都有自己的内核栈。当进程在执行用户自己的代码的时候，我们称其处于**用户运行态（用户态)**。此时处理器在特权级最低的（3级）用户代码中运行。系统调用主要通过如下两个函数来实现

```java
copy_from_user() //将数据从用户空间拷贝到内核空间
copy_to_user() //将数据从内核空间拷贝到用户空间
```

-   Linux 的动态内核可加载模块,在 Android 系统中，**这个运行在内核空间，负责各个用户进程通过 Binder 实现通信的内核模块就叫 Binder 驱动（Binder Dirver）**
-   **内存映射**简单的讲就是将用户空间的一块内存区域映射到内核空间。映射关系建立后，用户对这块内存区域的修改可以直接反应到内核空间；反之内核空间对这段区域的修改也能直接反应到用户空间。内存映射能减少数据拷贝次数，实现用户空间和内核空间的高效互动。两个空间各自的修改能直接反映在映射的内存区域，从而被对方空间及时感知。也正因为如此，内存映射能够提供对进程间通信的支持。

## Binder的优势

-   **支持client-server的结构**，访问接入点，获得访问接入点的方法，制定Command-Reply协议
-   **面向对象的程序设计**，面向对象思想的引入将进程间通信转化为通过对某个Binder对象的引用调用该对象的方法，而其独特之处在于。Binder对象是一个可以跨进程引用的对象，它的实体位于一个进程中，而它的引用却遍布于系统的各个进程之中。最诱人的是，这个引用和java里引用一样既可以是强类型，也可以是弱类型，而且可以从一个进程传给其它进程，让大家都能访问同一Server，就象将一个对象或引用赋值给另一个引用一样。Binder模糊了进程边界，淡化了进程间通信过程，整个系统仿佛运行于同一个面向对象的程序之中
-   传统IPC性能低下，一次数据传递需要经历：内存缓存区 --> 内核缓存区 --> 内存缓存区，需要 2 次数据拷贝，**binder只需要一次拷贝**。
-   **安全性**，Android为每个安装好的应用程序分配了自己的UID，故进程的UID是鉴别进程身份的重要标志。使用传统IPC只能由用户在数据包里填入UID/PID，但这样不可靠，容易被恶意程序利用。**可靠的身份标记只有由IPC机制本身在内核中添加**
-   **支持匿名binder**,其次传统IPC访问接入点是开放的，无法建立私有通道。比如命名管道的名称，system V的键值，socket的ip地址或文件名都是开放的，只要知道这些接入点的程序都可以和对端建立连接，不管怎样都无法阻止恶意程序通过猜测接收方地址获得连接

## Binder 通信模型

-   类比Server, Client,  DNS, 路由器

### Binder 驱动

-   Binder驱动，Linux 的动态内核可加载模块，工作为内核态，提供open()，mmap()，poll()，ioctl()等标准文件操作，驱动负责进程之间Binder通信的建立，Binder在进程之间的传递，Binder引用计数管理，数据包在进程之间的传递和交互等一系列底层支持

### ServiceManager

-   ServiceManager，SMgr的作用是将字符形式的Binder名字转化成Client中对该Binder的引用，使得Client能够通过Binder名字获得对Server中Binder实体的引用
    -   Server创建了Binder实体，为其取一个字符形式，可读易记的名字
    -   将这个Binder连同名字以数据包的形式通过Binder驱动发送给SMgr，通知SMgr注册一个名叫张三的Binder，它位于某个Server中。
    -   驱动为这个穿过进程边界的Binder创建位于内核中的实体节点以及SMgr对实体的引用，将名字及新建的引用打包传递给SMgr。
    -   SMgr收数据包后，从中取出名字和引用填入一张查找表中

### Client 获得实名Binder的引用

-   Server向SMgr注册了Binder实体及其名字后，Client就可以通过名字获得该Binder的引用了。Client也利用保留的0号引用向SMgr请求访问某个Binder：我申请获得名字叫张三的Binder的引用。SMgr收到这个连接请求，从请求数据包里获得Binder的名字，在查找表里找到该名字对应的条目，从条目中取出Binder的引用，将该引用作为回复发送给发起请求的Client

### 匿名 Binder

-   并不是所有Binder都需要注册给SMgr广而告之的。Server端可以通过已经建立的Binder连接将创建的Binder实体传给Client，当然这条已经建立的Binder连接必须是通过实名Binder实现。由于这个Binder没有向SMgr注册名字，所以是个匿名Binder。Client将会收到这个匿名Binder的引用，通过这个引用向位于Server中的实体发送请求。匿名Binder为通信双方建立一条私密通道，只要Server没有把匿名Binder发给别的进程，别的进程就无法通过穷举或猜测等任何方式获得该Binder的引用，向该Binder发送请求

## Binder 在应用程序中的表述

### Binder 在Server端的表述 – Binder实体

-   **做为Proxy设计模式的基础，首先定义一个抽象接口类封装Server所有功能(AIDL接口)**，其中包含一系列纯虚函数留待Server和Proxy各自实现。由于这些函数需要跨进程调用，须为其一一编号，从而Server可以根据收到的编号决定调用哪个函数。
-   其次就要引入Binder了。**Server端定义另一个Binder抽象类处理来自Client的Binder请求数据包，其中最重要的成员是虚函数onTransact()。该函数分析收到的数据包，调用相应的接口函数处理请求(AIDL接口生成的Stub)**。
-   **接下来采用继承方式以接口类和Binder抽象类为基类构建Binder在Server中的实体，实现基类里所有的虚函数，包括公共接口函数以及数据包处理函数：onTransact()**。这个函数的输入是来自Client的binder_transaction_data结构的数据包。前面提到，该结构里有个成员code，包含这次请求的接口函数编号。onTransact()将case-by-case地解析code值，从数据包里取出函数参数，调用接口类中相应的，已经实现的公共接口函数。函数执行完毕，如果需要返回数据就再构建一个binder_transaction_data包将返回数据包填入其中。
-   那么各个Binder实体的onTransact()又是什么时候调用呢？这就需要驱动参与了。前面说过，Binder实体须要以Binde传输结构flat_binder_object形式发送给其它进程才能建立Binder通信，而Binder实体指针就存放在该结构的handle域中。驱动根据Binder位置数组从传输数据中获取该Binder的传输结构，为它创建位于内核中的Binder节点，将Binder实体指针记录在该节点中。如果接下来有其它进程向该Binder发送数据，驱动会根据节点中记录的信息将Binder实体指针填入binder_transaction_data的target.ptr中返回给接收线程。接收线程从数据包中取出该指针，reinterpret_cast成Binder抽象类并调用onTransact()函数。由于这是个虚函数，不同的Binder实体中有各自的实现，从而可以调用到不同Binder实体提供的onTransact()。

### Binder 在Client端的表述 – Binder引用

-   做为Proxy设计模式的一部分，Client端的Binder同样要继承Server提供的公共接口类并实现公共函数。但这不是真正的实现，而是对远程函数调用的包装：将函数参数打包，通过Binder向Server发送申请并等待返回值。为此Client端的Binder还要知道Binder实体的相关信息，即对Binder实体的引用。该引用或是由SMgr转发过来的，对实名Binder的引用或是由另一个进程直接发送过来的，对匿名Binder的引用。
-   由于继承了同样的公共接口类，Client Binder提供了与Server Binder一样的函数原型，使用户感觉不出Server是运行在本地还是远端。Client Binder中，公共接口函数的包装方式是：创建一个binder_transaction_data数据包，将其对应的编码填入code域，将调用该函数所需的参数填入data.buffer指向的缓存中，并指明数据包的目的地，那就是已经获得的对Binder实体的引用，填入数据包的target.handle中。注意这里和Server的区别：实际上target域是个联合体，包括ptr和handle两个成员，前者用于接收数据包的Server，指向 Binder实体对应的内存空间；后者用于作为请求方的Client，存放Binder实体的引用，告知驱动数据包将路由给哪个实体。数据包准备好后，通过驱动接口发送出去。经过BC_TRANSACTION/BC_REPLY回合完成函数的远程调用并得到返回值。
