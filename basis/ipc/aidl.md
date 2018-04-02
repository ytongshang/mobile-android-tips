# AIDL

## 相关文档

- 《Android开发艺术探索》
- [Android：学习AIDL，这一篇文章就够了(上)](https://blog.csdn.net/luoyanglizi/article/details/51980630)
- [学习AIDL源码示例](https://github.com/ytongshang/AndroidLearning)

## Android Studio中的AIDL工程结构

![AIDL工程目录](./../../image-resources/ipc/android_studio_aidl工程结构.png)

## AIDL中支持的数据类型

- 基本数据类型(int,long,char,boolean,double等)
- String和CharSequence
- List,只支持ArrayList,里面每个元素都必须能够被AIDL支持
- Map,只持持HashMap,里面的每个元素都必须被AIDL支持，包括key和value
- Parcelable,所以实现了Parcelable接口的对象
- AIDL，所有的AIDL接口本身也可以在AIDL中使用

## 定向Tag

- AIDL中的定向tag表示了在跨进程通信中数据的流向，**其中 in 表示数据只能由客户端流向服务端， out 表示数据只能由服务端流向客户端，而 inout 则表示数据可在服务端与客户端之间双向流通**。其中，数据流向是针对在客户端中的那个传入方法的对象而言的。
- in为定向tag的话表现为服务端将会接收到一个那个对象的完整数据，**但是客户端的那个对象不会因为服务端对传参的修改而发生变动**；
- out的话表现为服务端将会接收到那个对象的的空对象，但是**在服务端对接收到的空对象有任何修改之后客户端将会同步变动；
- inout为定向tag的情况下，**服务端将会接收到客户端传来对象的完整信息，并且客户端将会同步服务端对该对象的任何变动**
- **Java中的基本类型和String ，CharSequence 的定向tag默认且只能是in**
- **传参时除了基本类型与String,CharSequence,其它的类型必须加上定向Tag**

## 自定义Parcelable

- **即使在对应的package中定义Parcelable Java对象，也必须在aidl中再次声明**,并且两者的package要一样

```java
// Book.java
package cradle.rancune.process.model;

import android.os.Parcel;
import android.os.Parcelable;

/**
 * Created by Rancune@126.com 2018/3/29.
 */
public class Book implements Parcelable {
    private String mId;
    private String mName;

    public Book() {

    }

    protected Book(Parcel in) {
        mId = in.readString();
        mName = in.readString();
    }

    public static final Creator<Book> CREATOR = new Creator<Book>() {
        @Override
        public Book createFromParcel(Parcel in) {
            return new Book(in);
        }

        @Override
        public Book[] newArray(int size) {
            return new Book[size];
        }
    };

    public String getId() {
        return mId;
    }

    public void setId(String id) {
        mId = id;
    }

    public String getName() {
        return mName;
    }

    public void setName(String name) {
        mName = name;
    }

    public void readFromParcel(Parcel in) {

    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(mId);
        dest.writeString(mName);
    }
}
```

```java
// Book.aidl
package cradle.rancune.process.model;

// Declare any non-default types here with import statements
parcelable Book;
```

- **如果一个Parcelable的定向Tag是inout,那么该对象除了要实现Parcelable接口，还必须实现readFromParcel(Parcel)函数**

```java
public void readFromParcel(Parcel in) {
    mId = in.readString();
    mName = in.readString();
}
```

## 显示引入

- **即使不同的aidl类在同一个包中，在使用时也必须要显示引入**

```java
// IBookManager.aidl
package cradle.rancune.process;

// 必须显示引入
import cradle.rancune.process.model.Book;

// Declare any non-default types here with import statements

interface IBookManager {
    void add(inout Book book);
    List<Book> getBookList();
}
```

## 自动生成代码

- 使用Android Studio编译自动生成代码

```java
/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Original file: /Users/tanhua/Work/android/process/app/src/main/aidl/cradle/rancune/process/IBookManager.aidl
 */
package cradle.rancune.process;
// Declare any non-default types here with import statements

public interface IBookManager extends android.os.IInterface {
    /**
     * Local-side IPC implementation stub class.
     */
    public static abstract class Stub extends android.os.Binder implements cradle.rancune.process.IBookManager {
        private static final java.lang.String DESCRIPTOR = "cradle.rancune.process.IBookManager";

        /**
         * Construct the stub at attach it to the interface.
         */
        public Stub() {
            this.attachInterface(this, DESCRIPTOR);
        }

        /**
         * Cast an IBinder object into an cradle.rancune.process.IBookManager interface,
         * generating a proxy if needed.
         */
        public static cradle.rancune.process.IBookManager asInterface(android.os.IBinder obj) {
            if ((obj == null)) {
                return null;
            }
            android.os.IInterface iin = obj.queryLocalInterface(DESCRIPTOR);
            if (((iin != null) && (iin instanceof cradle.rancune.process.IBookManager))) {
                return ((cradle.rancune.process.IBookManager) iin);
            }
            return new cradle.rancune.process.IBookManager.Stub.Proxy(obj);
        }

        @Override
        public android.os.IBinder asBinder() {
            return this;
        }

        @Override
        public boolean onTransact(int code, android.os.Parcel data, android.os.Parcel reply, int flags) throws android.os.RemoteException {
            switch (code) {
                case INTERFACE_TRANSACTION: {
                    reply.writeString(DESCRIPTOR);
                    return true;
                }
                case TRANSACTION_add: {
                    data.enforceInterface(DESCRIPTOR);
                    cradle.rancune.process.model.Book _arg0;
                    // 获得函数add(Book)的参数 Book _arg0;
                    if ((0 != data.readInt())) {
                        _arg0 = cradle.rancune.process.model.Book.CREATOR.createFromParcel(data);
                    } else {
                        _arg0 = null;
                    }
                    // 所以这里我们要注意这里的Book可能是null
                    this.add(_arg0);
                    // 函数调用中没有发生Exception
                    reply.writeNoException();
                    // 因为上面我们在定义的Book的定向Tag是inout,所以这里会再次返回函数调用参数_arg0
                    if ((_arg0 != null)) {
                        reply.writeInt(1);
                        _arg0.writeToParcel(reply, android.os.Parcelable.PARCELABLE_WRITE_RETURN_VALUE);
                    } else {
                        reply.writeInt(0);
                    }
                    return true;
                }
                case TRANSACTION_getBookList: {
                    data.enforceInterface(DESCRIPTOR);
                    java.util.List<cradle.rancune.process.model.Book> _result = this.getBookList();
                    reply.writeNoException();
                    reply.writeTypedList(_result);
                    return true;
                }
            }
            return super.onTransact(code, data, reply, flags);
        }

        private static class Proxy implements cradle.rancune.process.IBookManager {
            private android.os.IBinder mRemote;

            Proxy(android.os.IBinder remote) {
                mRemote = remote;
            }

            @Override
            public android.os.IBinder asBinder() {
                return mRemote;
            }

            public java.lang.String getInterfaceDescriptor() {
                return DESCRIPTOR;
            }

            @Override
            public void add(cradle.rancune.process.model.Book book) throws android.os.RemoteException {
                android.os.Parcel _data = android.os.Parcel.obtain();
                android.os.Parcel _reply = android.os.Parcel.obtain();
                try {
                    _data.writeInterfaceToken(DESCRIPTOR);
                    if ((book != null)) {
                        _data.writeInt(1);
                        book.writeToParcel(_data, 0);
                    } else {
                        _data.writeInt(0);
                    }
                    mRemote.transact(Stub.TRANSACTION_add, _data, _reply, 0);
                    _reply.readException();
                    if ((0 != _reply.readInt())) {
                        book.readFromParcel(_reply);
                    }
                } finally {
                    _reply.recycle();
                    _data.recycle();
                }
            }

            @Override
            public java.util.List<cradle.rancune.process.model.Book> getBookList() throws android.os.RemoteException {
                android.os.Parcel _data = android.os.Parcel.obtain();
                android.os.Parcel _reply = android.os.Parcel.obtain();
                java.util.List<cradle.rancune.process.model.Book> _result;
                try {
                    _data.writeInterfaceToken(DESCRIPTOR);
                    mRemote.transact(Stub.TRANSACTION_getBookList, _data, _reply, 0);
                    _reply.readException();
                    _result = _reply.createTypedArrayList(cradle.rancune.process.model.Book.CREATOR);
                } finally {
                    _reply.recycle();
                    _data.recycle();
                }
                return _result;
            }
        }

        static final int TRANSACTION_add = (android.os.IBinder.FIRST_CALL_TRANSACTION + 0);
        static final int TRANSACTION_getBookList = (android.os.IBinder.FIRST_CALL_TRANSACTION + 1);
    }

    public void add(cradle.rancune.process.model.Book book) throws android.os.RemoteException;

    public java.util.List<cradle.rancune.process.model.Book> getBookList() throws android.os.RemoteException;
}
```

### DESCRIPTOR

- Binder的唯一标识，一般用当前Binder的类名表示

### asInterface(android.os.IBinder obj)

- 用于将服务端的Binder对象转为客户端的AIDL接口对象
- **如果客户端与服务端位于同一进程，返回服务端的Stub对象本身**
- **如果不在同一进程，返回系统封装后的Stub.proxy对象**

### asBinder()

- 返回当前的Binder对象

### onTransact(int code, android.os.Parcel data, android.os.Parcel reply, int flags)

- **运行在服务端的Binder线程池中**
- 当客户端发起跨进程的请求时，远程请求会通过底层封装后交由此方法来处理
- 通过code可以确定客户端要调用哪一个方法
- 如果方法有参数的话，可以从data中获得方法需要的参数
- 目标方法执行完成后，如果有返回结果，需要将结果写入reply中
- **如果某个函数的参数的定向Tag是inout,那么还需要将参数还回**
- **如果这个方法返回false,那么客户端的请求会失败，可以利用这个特性来做权限验证**

### Proxy.getBookList 和 Proxy.addBook

- **这两个方法运行在客户端**
- 创建方法调用需要的_data,返回值_reply，然后将方法调用参数写入_data
- **通过transact发起RPC请求，同时将当前线程挂起**
- 服务端的onTransact方法会被调用，直到RPC过程返回，从_reply中取出返回结果，并且当前线程继续执行
- **所以客户端发起请求到返回实际上是一个阻塞的过程**

## Binder死亡

### linkToDeath和unlinkToDeath

- Binder是工作在服务器进程的，如果，由于某种原因，服务端出现故障停止了，那么该返回的Binder对象也将消失，这时，如果我们在客户端使用Binder对象进行某些函数调用将会出现错误
- 为Binder对象设置死亡代理，当出现和服务端连接故障时，系统将自动调用死亡代理函数binderDied()，我们处理相关逻辑，并且重新和服务端建立连接
- **linkToDeath()为Binder对象设置死亡代理，一般在ServiceConnection的onServiceConnected中调用注册，unlinkToDeath()将设置的死亡代理标志清除，一般在binderDied中调用**
- **IBinder.DeathRecipient的binderDied运行在客户端的Binder线程池中，不在主线程**

```java
public class MainActivity extends Activity {
    private IAidlCall mIAidlCall;

    private IBinder.DeathRecipient mDeathRecipient = new IBinder.DeathRecipient() {
        @Override
        public void binderDied() {
            // TODO Auto-generated method stub
            if (mIAidlCall == null) {
                return;
            }
            // 断开连接后，清除死亡代理
            mIAidlCall.asBinder().unlinkToDeath(mDeathRecipient, 0);
            mIAidlCall = null;
            // 重新绑定远程服务
　　　　　　　bindService(new Intent("demo.action.aidl.IAidlCall").
　　　　　　　　　　setPackage("com.example.severdemo"), conn, BIND_AUTO_CREATE);
        }
    };

    private ServiceConnection conn = new ServiceConnection() {
        @Override
        public void onServiceDisconnected(ComponentName name) {
        }

        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            mIAidlCall = IAidlCall.Stub.asInterface(service);
            try {
                // 服务端连接成功后，设置死亡代理
                service.linkToDeath(mDeathRecipient, 0);
            } catch (RemoteException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // "demo.action.aidl.IAidlCall" 是远程服务的action
        bindService(new Intent("demo.action.aidl.IAidlCall")
　　　　　　.setPackage("com.example.severdemo"), conn, BIND_AUTO_CREATE);
    }
}
```

### onServiceDisconnected

- **ServiceConnection的onServiceConnected和onServiceDisconnected都是运行在客户端的UI线程的，不能在其中执行耗时的方法**

### DeathRecipient与onServiceDisconnected

- 两者都可以监听到服务端的意外死亡，**但是DeathRecipient的binderDied运行在客户端的Binder的线程池中，而onServiceDisconnected则运行在客户端的主线程中**

## 服务端的实现

- 实现一个Service
- Service的onBind()方法返回AIDL编译生成的Stub的实现类对象
- **注意AIDL的方法是在服务端的Binder线程池中执行的，所以在注重线程同步**

```java
public class BookManagerService extends Service {

    // 因为Binder方法运行在线程池中，这里使用CopyOnWriteArrayList进行同步
    private final CopyOnWriteArrayList<Book> mBooks = new CopyOnWriteArrayList<>();

    @Override
    public void onCreate() {
        super.onCreate();
        mBooks.add(new Book("1", "Effective Java"));
        mBooks.add(new Book("2", "Go In Action"));
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        // 直接返回Stub的实现类
        return mBinder;
    }

    private final IBinder mBinder = new IBookManager.Stub() {
        @Override
        public void add(Book book) throws RemoteException {
            mBooks.add(book);
        }

        @Override
        public List<Book> getBookList() throws RemoteException {
            return mBooks;
        }
    };
}
```

## 客户端的实现

- bindService,在onServiceConnected中将Binder转为AIDL接口，并绑定死亡代理

```java
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";

    private IBookManager mBookManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Intent intent = new Intent(this,BookManagerService.class);
        bindService(intent, mConnection, Context.BIND_AUTO_CREATE);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (mBookManager != null) {
            try {
                List<Book> list = mBookManager.getBookList();
                Log.d(TAG, list.getClass().getName());
                Log.d(TAG, String.valueOf(list));
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    protected void onDestroy() {
        unbindService(mConnection);
        super.onDestroy();
    }

    private final ServiceConnection mConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            mBookManager = IBookManager.Stub.asInterface(service);
            try {
                service.linkToDeath(mDeathRecipient, 0);
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {

        }
    };

    private final IBinder.DeathRecipient mDeathRecipient = new IBinder.DeathRecipient() {
        @Override
        public void binderDied() {
            if (mBookManager == null) {
                return;
            }
            mBookManager.asBinder().unlinkToDeath(mDeathRecipient, 0);
            mBookManager = null;
        }
    };
}

```

## 跨进程Listener

- 在客户端定义listener,然后注册到服务端，服务端根据业务需求回调listener
- **服务端和客户端如果在不同的进程，由于对象不能跨进程传输，它们实际是通过序列化与反序列化完成的，所以服务端和客户端里面的listener其实不是同一个对象**

### RemoteCallbackList

- **跨进程注册的listener必须是AIDL接口**
- **服务端管理listener必须使用RemoteCallbackList管理**
- **RemoteCallbackList内部保证了线程同步，不需要我们手动同步**
- **当客户端进程终止时，RemoteCallbackList能够自动移除客户端注册的listener**
- 调用RemoteCallbackList的方法时，即使是获取size,也必须与beginBroadcast和finishBroadcast配合使用

```java
private final RemoteCallbackList<IOnNewBookArrivedListener> mListeners = new RemoteCallbackList<>();

private final IBinder mBinder = new IBookManager.Stub() {
        @Override
        public void add(Book book) throws RemoteException {
            mBooks.add(book);
            onNewBookArrived(book);
        }

        @Override
        public List<Book> getBookList() throws RemoteException {
            return mBooks;
        }

        @Override
        public void registerListener(IOnNewBookArrivedListener listener) throws RemoteException {
            mListeners.register(listener);
        }

        @Override
        public void unregisterListener(IOnNewBookArrivedListener listener) throws RemoteException {
            mListeners.unregister(listener);
        }
    };

    private void onNewBookArrived(Book book) {
        int size = mListeners.beginBroadcast();
        for (int i = 0; i < size; ++i) {
            IOnNewBookArrivedListener listener = mListeners.getBroadcastItem(i);
            try {
                listener.onNewBookArrived(book);
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }
        mListeners.finishBroadcast();
    }
```

## AIDL RPC请求流程

- **客户端在线程A发起请求的话，线程A会被挂起直到服务端方法结果返回，如果服务端方法执行比较耗时的，就会导致客户端线程长时间的阻塞在这里，如果线程A是主线程的话，就会ANR,类似于于网络请求，所以当我们知道某个远程方法是耗时的话，就不应当在主线程去调用它。**
- **服务端通过RemoteCallbackList管理回调listener的时候，这些listener是运行在客户端的线程池的**，如果客户端的listener回调是一个耗时操作，并且我们在服务端的主线程回调listener，会导致服务端的ANR,所以也**不应当在服务端的主线程调用客户端的耗时方法。**
- **客户端调用服务端的Binder方法，这些方法是运行在服务端Binder线程池中，所以Binder方法不管是否耗时都应当注意数据的同步**
- **服务端的方法是运行在服务端的Binder线程池中的，本身就可以执行大量耗时操作，我们只需要保证数据同步，所以一般情况下，我们不需要要服务端开启线程执行方法。**

![Binder工作流程](./../../image-resources/ipc/Binder工作机制.png)
