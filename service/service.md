# service

## 生命周期

### startService,stopService

- onCreate()，首次创建服务时，系统将调用此方法来执行一次性设置程序（在调用 onStartCommand() 或 onBind() 之前）。如果服务已在运行，则不会调用此方法
- onStartCommand(), 当通过调用 context.startService() 请求启动服务时，系统将调用此方法。一旦执行此方法，服务即会启动并可在后台无限期运行,
 如果您实现此方法，则在服务工作完成后，需要由您通过调用 stopSelf() 或 stopService() 来停止服务.
- onDestroy(),当服务不再使用且将被销毁时，系统将调用此方法。服务应该实现此方法来清理所有资源，如线程、注册的侦听器、接收器等
- 通过startService()启动服务，**onCreate()只会在创建的时候执行一次，但是每次startService都会执行onStartCommand()**
- **通过调用 startService() 启动服务，则服务将一直运行，直到服务使用 stopSelf() 自行停止运行**，或由其他组件通过调用 stopService() 停止它为止。


### bindService，unbindService

- 当应用组件通过调用 bindService() 绑定到服务时，服务即处于“绑定”状态。绑定服务提供了一个客户端-服务器接口
 允许组件与服务进行交互、发送请求、获取结果，甚至是利用进程间通信 (IPC) 跨进程执行这些操作，仅当与另一个应用组件绑定时，
 绑定服务才会运行。 **多个组件可以同时绑定到该服务，但全部取消绑定后，该服务即会被销毁**
- bindService()必须实现 onBind() 回调方法，**该方法返回的 IBinder 对象定义了客户端用来与服务进行交互的编程接口**
- 客户端可通过调用 bindService() 绑定到服务。调用时，它必须提供 ServiceConnection 的实现，后者会监控与服务的连接。bindService() 方法会立即无值返回，
 但当 Android 系统创建客户端与服务之间的连接时，会对 ServiceConnection 调用 onServiceConnected()，向客户端传递用来与服务通信的 IBinder。
 多个客户端可同时连接到一个服务。不过，只有在第一个客户端绑定时，系统才会调用服务的 onBind() 方法来检索 IBinder。系统随后无需再次调用 onBind()，
 便可将同一 IBinder 传递至任何其他绑定的客户端。 **当最后一个客户端取消与服务的绑定时，系统会将服务销毁（除非 startService() 也启动了该服务**


### 具有已启动和绑定两种状态的服务

- 您可以创建同时具有已启动和绑定两种状态的服务。 也就是说，可通过调用 startService() 启动该服务，让服务无限期运行；此外，还可通过调用 bindService() 使客户端绑定到服务。
 **如果您确实允许服务同时具有已启动和绑定状态，则服务启动后，系统“不会”在所有客户端都取消绑定时销毁服务**。 为此，您必须通过调用 stopSelf() 或 stopService() 显式停止服务。
 尽管您通常应该实现 onBind() 或 onStartCommand()，但有时需要同时实现这两者。例如，音乐播放器可能发现让其服务无限期运行并同时提供绑定很有用处。 这样一来
 ，Activity 便可启动服务进行音乐播放，即使用户离开应用，音乐播放也不会停止。 然后，当用户返回应用时，Activity 可绑定到服务，重新获得回放控制权



## 绑定服务

### 扩展Binder类

1.在您的服务中，创建一个可满足下列任一要求的 Binder 实例：

- 包含客户端可调用的公共方法
- 返回当前 Service 实例，其中包含客户端可调用的公共方法
- 或返回由服务承载的其他类的实例，其中包含客户端可调用的公共方法

2.从 onBind() 回调方法返回此 Binder 实例。

3.在客户端中，从 onServiceConnected() 回调方法接收 Binder，并使用提供的方法调用绑定服务。

```java
public class LocalService extends Service {
    // Binder given to clients
    private final IBinder mBinder = new LocalBinder();
    // Random number generator
    private final Random mGenerator = new Random();

    /**
     * Class used for the client Binder.  Because we know this service always
     * runs in the same process as its clients, we don't need to deal with IPC.
     */
    public class LocalBinder extends Binder {
        LocalService getService() {
            // Return this instance of LocalService so clients can call public methods
            return LocalService.this;
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    /** method for clients */
    public int getRandomNumber() {
      return mGenerator.nextInt(100);
    }
}
```

```java
public class BindingActivity extends Activity {
    LocalService mService;
    boolean mBound = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
    }

    @Override
    protected void onStart() {
        super.onStart();
        // Bind to LocalService
        Intent intent = new Intent(this, LocalService.class);
        bindService(intent, mConnection, Context.BIND_AUTO_CREATE);
    }

    @Override
    protected void onStop() {
        super.onStop();
        // Unbind from the service
        if (mBound) {
            unbindService(mConnection);
            mBound = false;
        }
    }

    /** Called when a button is clicked (the button in the layout file attaches to
      * this method with the android:onClick attribute) */
    public void onButtonClick(View v) {
        if (mBound) {
            // Call a method from the LocalService.
            // However, if this call were something that might hang, then this request should
            // occur in a separate thread to avoid slowing down the activity performance.
            int num = mService.getRandomNumber();
            Toast.makeText(this, "number: " + num, Toast.LENGTH_SHORT).show();
        }
    }

    /** Defines callbacks for service binding, passed to bindService() */
    private ServiceConnection mConnection = new ServiceConnection() {

        @Override
        public void onServiceConnected(ComponentName className,
                IBinder service) {
            // We've bound to LocalService, cast the IBinder and get LocalService instance
            LocalBinder binder = (LocalBinder) service;
            mService = binder.getService();
            mBound = true;
        }

        @Override
        public void onServiceDisconnected(ComponentName arg0) {
            mBound = false;
        }
    };
}
```