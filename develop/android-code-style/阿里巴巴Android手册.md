# 阿里巴巴-Android

## Android 资源文件命名与使用

- 前缀

```groovy
android {
    buildTypes {
        release {
            // 保存混淆配置
            consumerProguardFiles 'proguard-rules.pro'
        }
    }
    // 资源前缀
    resourcePrefix 'rxjava_'
}
```

## Android 基本组件

- Activity间的数据通信，对于数据量比较大的，避免使用 Intent + Parcelable的方式，可以考虑 EventBus 等替代方案，以免造成 TransactionTooLargeException

- 避免在 Service#onStartCommand()/onBind()方法中执行耗时操作，如果确实有需求，应改用 IntentService 或采用其他异步机制完成

- **避免在 BroadcastReceiver#onReceive()中执行耗时操作，如果有耗时工作，应该创建 IntentService 完成**，而不应该在 BroadcastReceiver 内创建子线程去做

- 避免使用隐式 Intent 广播敏感信息，信息可能被其他注册了对应BroadcastReceiver 的 App 接收，**如果广播仅限于应用内，则可以使用 LocalBroadcastManager#sendBroadcast()实现，避免敏感信息外泄和 Intent 拦截的风险**

- 嵌套Fragment
    - [Android 多个Fragment嵌套导致的三大BUG](http://blog.csdn.net/megatronkings/article/details/51417510)
    - onActivityResult()方法的处理错乱，内嵌的 Fragment 可能收不到该方法的回调，需要由宿主 Fragment 进行转发处理
    - 突变动画效果
    - 被继承的 setRetainInstance()，导致在 Fragment 重建时多次触发不必要的逻辑。

```java
FragmentManager fragmentManager = getFragmentManager();
Fragment fragment = fragmentManager.findFragmentByTag(FragmentB.TAG);
if (null == fragment) {
    FragmentB fragmentB = new FragmentB();
    FragmentTransaction fragmentTransaction = fragmentManager.beginTransaction();
    fragmentTransaction.add(R.id.fragment_container, fragmentB,FragmentB.TAG).commit();
}
```

- 不要在 Android 的 Application 对象中缓存数据。基础组件之间的数据共享请使用 Intent 等机制，也可使用 SharedPreferences 等数据持久化机制。

## UI与布局

- AnimationDrawable的使用注意OOM,[Android 帧动画OOM问题优化](http://blog.csdn.net/wanmeilang123/article/details/53929484)

- 不能使用 ScrollView 包裹 ListView/GridView/ExpandableListVIew;因为这样会把 ListView 的所有Item 都加载到内存中，要消耗巨大的内存和 cpu 去绘制图面，**推荐使用 NestedScrollView**

## 进程、线程与消息通信

- 不要通过 Intent 在 Android 基础组件之间传递大数据（binder transaction缓存为 1MB），可能导致 OOM

- 在Application的业务初始化代码加入进程判断，确保只在自己需要的进程初始化。特别是后台进程减少不必要的业务初始化

```java
private static String getProcessName() {
    int pid = android.os.Process.myPid();
    ActivityManager am = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
    List<ActivityManager.RunningAppProcessInfo> runningApps = am.getRunningAppProcesses();
    if (!Utils.isEmpty(runningApps)) {
        for (ActivityManager.RunningAppProcessInfo procInfo : runningApps) {
            if (procInfo.pid == pid) {
                return procInfo.processName;
            }
        }
    }
    return null;
}

@Override
public void onCreate() {
    super.onCreate();
    String processName = getProcessName();
    if ("com.kascend.chushou:filedownloader".equals(processName)) {
        //如果是某个子进程，执行自自己的初始化
        return;
    }
    // 主进行的初始化
    // ...
}
```

- 新建线程相关
    - **新建线程时，必须通过线程池提供**，不允许在应用中自行显式创建线程
    - **线程池不允许使用Executors去创建，而是通过ThreadPoolExecutor的方式**
    - ThreadPoolExecutor设置线程存活时间(setKeepAliveTime)，
    - 新建线程时，定义能识别自己业务的线程名称，便于性能优化和问题排查，也就是**自定义ThreadFactory**

```java
int NUMBER_OF_CORES = Runtime.getRuntime().availableProcessors();
int KEEP_ALIVE_TIME = 1;
TimeUnit KEEP_ALIVE_TIME_UNIT = TimeUnit.SECONDS;
// 这里有坑，如果是无界BlockingQueue,maxNumPoolSize可能无用的问题
BlockingQueue<Runnable> taskQueue = new LinkedBlockingQueue<Runnable>(500);
ExecutorService executorService = new ThreadPoolExecutor(NUMBER_OF_CORES,
    NUMBER_OF_CORES*2,
    KEEP_ALIVE_TIME,
    KEEP_ALIVE_TIME_UNIT,
    taskQueue,
    new BackgroundThreadFactory(),
    new DefaultRejectedExecutionHandler()
);
```

- **禁止在多进程之间用SharedPreferences共享数据**

- 谨慎使用 Android 的多进程，多进程虽然能够降低主进程的内存压力，但会遇到如下问题：
    - 不能实现完全退出所有 Activity 的功能；
    - 首次进入新启动进程的页面时会有延时的现象（有可能黑屏、白屏几秒，是白屏还是黑屏和新 Activity 的主题有关）
    - 应用内多进程时，Application 实例化多次，需要考虑各个模块是否都需要在所有进程中初始化；
    - 多进程间通过 SharedPreferences 共享数据时不稳定

## 文件与数据库

- 当使用外部存储时，必须检查外部存储的可用性

- **应用间共享文件时，不要通过放宽文件系统权限的方式去实现，而应使用FileProvider**

- 数据库操作
    - 数据库 Cursor 必须确保使用完后关闭
    - 多线程操作写入数据库时，需要使用事务，以免出现同步问题
    - 大数据写入数据库时，请使用事务或其他能够提高 I/O 效率的机制，保证执行速度
    - 执行SQL语句时，应使用SQLiteDatabase#insert()、update()、delete()，不要使用SQLiteDatabase#execSQL()，以免SQL注入风险

## Bitmap、Drawable与动画

- **加载大图片或者一次性加载多张图片，应该在异步线程中进行**。图片的加载，涉及到IO操作，以及CPU密集操作，很可能引起卡顿

- png 图片使用 tinypng 或者类似工具压缩处理，减少包体积

- 使用完毕的图片，应该及时回收，释放宝贵的内存

```java
Bitmap bitmap = null;
loadBitmapAsync(new OnResult(result){
    bitmap = result;
});
// 使用该bitmap
// 使用结束，在 2.3.3 及以下需要调用 recycle()函数，在 2.3.3 以上 GC 会自动管理，除非你明确不需要再用。
if (Build.VERSION.SDK_INT <= 10) {
    bitmap.recycle();
}
bitmap = null;
```

- 在Activity.onPause()或 Activity.onStop()回调中，关闭当前 activity 正在执行的的动画。

```java
public void onPause() {
    mImageView.clearAnimation()
}
```

- **使用inBitmap 重复利用内存空间，避免重复开辟新内存**,[Managing Bitmap Memory](https://developer.android.com/topic/performance/graphics/manage-memory.html)

- **使用ARGB_565代替ARGB_888,要注意RGB_565是没有透明度的**，如果图片本身需要保留透明度，那么就不能使用 RGB_565

```java
Config config = drawableSave.getOpacity() != PixelFormat.OPAQUE ? Config.ARGB_8888 :Config.RGB_565;
Bitmap bitmap = Bitmap.createBitmap(w, h, config);
```

- **在有强依赖 onAnimationEnd 回调的交互时，如动画播放完毕才能操作页面 ， onAnimationEnd可能会因各种异常没被回调**,可以加上超时postDelayed来解决这个问题，[参考资料](https://stackoverflow.com/questions/5474923/onanimationend-is-not-getting-called-onanimationstart-works-fine)

```java
View v = findViewById(R.id.xxxViewID);
final FadeUpAnimation anim = new FadeUpAnimation(v);
anim.setInterpolator(new AccelerateInterpolator());
anim.setDuration(1000);
anim.setFillAfter(true);
new Handler().postDelayed(new Runnable() {
    public void run() {
        if (v != null) {
            // view的clearAnimation会回调onAnimationEnd的
            v.clearAnimation();
        }
    }
}, anim.getDuration());
v.startAnimation(anim);
```

- 推荐当View Animation执行结束时，调用 View.clearAnimation()释放相关资源

```java
View v = findViewById(R.id.xxxViewID);
final FadeUpAnimation anim = new FadeUpAnimation(v);
anim.setInterpolator(new AccelerateInterpolator());
anim.setDuration(1000);
anim.setFillAfter(true);
anim.setAnimationListener(new AnimationListener() {
    @Override
    public void onAnimationEnd(Animation arg0) {
        //判断一下资源是否被释放了
        if (v != null) {
            v.clearAnimation();
        }
    }
});
v.startAnimation(anim);
```