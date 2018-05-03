# Activity启动过程

## 根Activity与子Activity

- 根Activity

```xml
<intent-filter>
    <action android:name="android.intent.action.MAIN"/>
    <category android:name="android.intent.category.LAUNCHER"/>
</intent-filter>
```

- 子Activity

## 根Activity的启动流程

### 总结

### Step 1~Step4

- 总结：这4步都是在Launcher中执行的

#### Step 1: Launcher.startActivitySafely

- Launcher继承于Activity
- 在 Launcher点击icon的时候，执行了startActivitySafely方法，其实就是调用startActivity方法

```java
boolean startActivitySafely(View v, Intent intent, Object tag) {
    boolean success = false;
    try {
        success = startActivity(v, intent, tag);
    } catch (ActivityNotFoundException e) {
        Toast.makeText(this, R.string.activity_not_found, Toast.LENGTH_SHORT).show();
        Log.e(TAG, "Unable to launch. tag=" + tag + " intent=" + intent, e);
    }
    return success;
}
```

#### Step2: Activity.startActivity

- Activity的startActivity方法，会调用的startActivityForResult，只不过requestCode为-1

```java
    @Override
    public void startActivity(Intent intent) {
        this.startActivity(intent, null);
    }

    @Override
    public void startActivity(Intent intent, @Nullable Bundle options) {
        if (options != null) {
            startActivityForResult(intent, -1, options);
        } else {
            // Note we want to go through this call for compatibility with
            // applications that may have overridden the method.
            startActivityForResult(intent, -1);
        }
    }


// Activity.java  4496
public void startActivityForResult(@RequiresPermission Intent intent, int requestCode,@Nullable Bundle options) {
        if (mParent == null) {
            options = transferSpringboardActivityOptions(options);
            Instrumentation.ActivityResult ar =
                mInstrumentation.execStartActivity(
                    this, mMainThread.getApplicationThread(), mToken, this,
                    intent, requestCode, options);
            if (ar != null) {
                mMainThread.sendActivityResult(
                    mToken, mEmbeddedID, requestCode, ar.getResultCode(),
                    ar.getResultData());
            }
            if (requestCode >= 0) {
                // If this start is requesting a result, we can avoid making
                // the activity visible until the result is received.  Setting
                // this code during onCreate(Bundle savedInstanceState) or onResume() will keep the
                // activity hidden during this time, to avoid flickering.
                // This can only be done when a result is requested because
                // that guarantees we will get information back when the
                // activity is finished, no matter what happens to it.
                mStartedActivity = true;
            }

            cancelInputsAndStartExitTransition(options);
            // TODO Consider clearing/flushing other event sources and events for child windows.
        } else {
           ...
        }
    }
```

#### Step3: Instrumentation.execStartActivity

- Instrumentation用来监控应用程序与系统之间的交互操作
- 可以跟踪application及activity生命周期，一般用在测试框架中较多
- contextThread 为ActivityThread内的ApplicationThread
- token是Activity的mToken对象，类型为IBinder,**指向了ActivityManagerService中一个类型为ActivityRecord的Binder本地对象**
- 每一个已经启动的Activity组件在ActivityManagerService中都有一个对应的ActivityRecord对象，用来维护Activity组件的运行状态和信息，**而Activity的mToken对象的赋值是在Activity的attach方法中**

```java
// Instrumentation.java  1578
 public ActivityResult execStartActivity(
            Context who, IBinder contextThread, IBinder token, Activity target,
            Intent intent, int requestCode, Bundle options) {
        IApplicationThread whoThread = (IApplicationThread) contextThread;
        Uri referrer = target != null ? target.onProvideReferrer() : null;
        if (referrer != null) {
            intent.putExtra(Intent.EXTRA_REFERRER, referrer);
        }
        if (mActivityMonitors != null) {
            synchronized (mSync) {
                ...
                // 忽略
            }
        }
        try {
            intent.migrateExtraStreamToClipData();
            intent.prepareToLeaveProcess(who);
            int result = ActivityManager.getService()
                .startActivity(whoThread, who.getBasePackageName(), intent,
                        intent.resolveTypeIfNeeded(who.getContentResolver()),
                        token, target != null ? target.mEmbeddedID : null,
                        requestCode, 0, null, options);
            // 检查startActivity的结果，其中最常见的错误就是我们没有的AndroidManifest
            // 中声明这个Activity
            checkStartActivityResult(result, intent);
        } catch (RemoteException e) {
            throw new RuntimeException("Failure from system", e);
        }
        return null;
    }

```

#### Step4: ActivityManager.getService().startActivity

- ActivityManager.getService返回的实际上是ActivityManagerService在本地的一个代理对象
- 这其中涉及到了AIDL通信，
    - **IAcitivityManager是AIDL接口**， IActivityManager中的Stub和Proxy和我们使用AIDL代码自动生成的代码一样
    - 因为我们肯定不是在系统进程中的，所以这里返回的其实是IActivityManager.Stub.Proxy对象
- 调用IActivityManager.Stub.Proxy中startActivity方法,向ActivityManagerService发起了RPC请求

```java
// ActivityManager.java 4216
public static IActivityManager getService() {
        return IActivityManagerSingleton.get();
}

 private static final Singleton<IActivityManager> IActivityManagerSingleton =
            new Singleton<IActivityManager>() {
                @Override
                protected IActivityManager create() {
                    final IBinder b = ServiceManager.getService(Context.ACTIVITY_SERVICE;
                    // 因为不在系统进程中，所以这里返回的是IActivityManager.Stub.Proxy类型的对象
                    final IActivityManager am = IActivityManager.Stub.asInterface(b);
                    return am;
                }
            };
```