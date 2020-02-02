# LeakCanary

## ReferenceQueue

- [Java源码剖析——彻底搞懂Reference和ReferenceQueue](https://blog.csdn.net/Jesministrator/article/details/78786162)

## LeakCanary原理

- [LeakCanary核心原理源码浅析](https://blog.csdn.net/cloud_huan/article/details/53081120)
- [全新 LeakCanary 2 ! 完全基于 Kotlin 重构升级 ！](https://blog.csdn.net/u012551350/article/details/97079164)

- 弱引用一旦变得弱可达，就会立即入ReferenceQueue。这将在 finalization函数调用 或者 GC 之前发生
- 将应当被gc的对象以弱引用放到一个map中，然后触发gc,如果这个弱引用进了ReferenceQueue中，则移出map,多次触发gc处理ReferenceQueue，如果map估然存在这个引用，那么这个对象就是一个可能泄漏的对象，然后heap dump，分析 dump 文件，找到引用链

### 不调用代码直接初始化

- 利用了ContentProvider的onCreate在Application的onCreate之前执行
- ActivityThread的main方法->ActivityThread.attach->

```java
    // android/app/ActivityThread.java
    public static void main(String[] args) {
        ...
        ActivityThread thread = new ActivityThread();
        thread.attach(false, startSeq);
        ...
    }

    // android/app/ActivityThread.java
    private void attach(boolean system, long startSeq) {
        sCurrentActivityThread = this;
        mSystemThread = system;
        if (!system) {
            ...
            final IActivityManager mgr = ActivityManager.getService();
            try {
                mgr.attachApplication(mAppThread, startSeq);
            } catch (RemoteException ex) {
                throw ex.rethrowFromSystemServer();
            }
            ...
        } else {
            ...
        }
        ...
    }

    //com/android/server/am/ActivityManagerService.java
    @Override
    public final void attachApplication(IApplicationThread thread, long startSeq) {
        synchronized (this) {
            int callingPid = Binder.getCallingPid();
            final int callingUid = Binder.getCallingUid();
            final long origId = Binder.clearCallingIdentity();
            attachApplicationLocked(thread, callingPid, callingUid, startSeq);
            Binder.restoreCallingIdentity(origId);
        }
    }

    //com/android/server/am/ActivityManagerService.java
    @Override
     @GuardedBy("this")
    private final boolean attachApplicationLocked(IApplicationThread thread,
            int pid, int callingUid, long startSeq) {

                ...
            if (app.isolatedEntryPoint != null) {
                // This is an isolated process which should just call an entry point instead of
                // being bound to an application.
                thread.runIsolatedEntryPoint(app.isolatedEntryPoint, app.isolatedEntryPointArgs);
            } else if (app.instr != null) {
                thread.bindApplication(processName, appInfo, providers,
                        app.instr.mClass,
                        profilerInfo, app.instr.mArguments,
                        app.instr.mWatcher,
                        app.instr.mUiAutomationConnection, testMode,
                        mBinderTransactionTrackingEnabled, enableTrackAllocation,
                        isRestrictedBackupMode || !normalMode, app.persistent,
                        new Configuration(getGlobalConfiguration()), app.compat,
                        getCommonServicesLocked(app.isolated),
                        mCoreSettingsObserver.getCoreSettingsLocked(),
                        buildSerial, isAutofillCompatEnabled);
            } else {
                thread.bindApplication(processName, appInfo, providers, null, profilerInfo,
                        null, null, null, testMode,
                        mBinderTransactionTrackingEnabled, enableTrackAllocation,
                        isRestrictedBackupMode || !normalMode, app.persistent,
                        new Configuration(getGlobalConfiguration()), app.compat,
                        getCommonServicesLocked(app.isolated),
                        mCoreSettingsObserver.getCoreSettingsLocked(),
                        buildSerial, isAutofillCompatEnabled);
            }
            ...
    }

    // android/app/ActivityThread.java
    public final void bindApplication(String processName, ApplicationInfo appInfo,
                List<ProviderInfo> providers, ComponentName instrumentationName,
                ProfilerInfo profilerInfo, Bundle instrumentationArgs,
                IInstrumentationWatcher instrumentationWatcher,
                IUiAutomationConnection instrumentationUiConnection, int debugMode,
                boolean enableBinderTracking, boolean trackAllocation,
                boolean isRestrictedBackupMode, boolean persistent, Configuration config,
                CompatibilityInfo compatInfo, Map services, Bundle coreSettings,
                String buildSerial, boolean autofillCompatibilityEnabled) {

            ...

            AppBindData data = new AppBindData();
            data.processName = processName;
            data.appInfo = appInfo;
            data.providers = providers;
            data.instrumentationName = instrumentationName;
            data.instrumentationArgs = instrumentationArgs;
            data.instrumentationWatcher = instrumentationWatcher;
            data.instrumentationUiAutomationConnection = instrumentationUiConnection;
            data.debugMode = debugMode;
            data.enableBinderTracking = enableBinderTracking;
            data.trackAllocation = trackAllocation;
            data.restrictedBackupMode = isRestrictedBackupMode;
            data.persistent = persistent;
            data.config = config;
            data.compatInfo = compatInfo;
            data.initProfilerInfo = profilerInfo;
            data.buildSerial = buildSerial;
            data.autofillCompatibilityEnabled = autofillCompatibilityEnabled;
            sendMessage(H.BIND_APPLICATION, data);
        }

      private void handleBindApplication(AppBindData data) {
         ...
        // Allow disk access during application and provider setup. This could
        // block processing ordered broadcasts, but later processing would
        // probably end up doing the same disk access.
        Application app;
        final StrictMode.ThreadPolicy savedPolicy = StrictMode.allowThreadDiskWrites();
        final StrictMode.ThreadPolicy writesAllowedPolicy = StrictMode.getThreadPolicy();
        try {
            // If the app is being launched for full backup or restore, bring it up in
            // a restricted environment with the base application class.
            app = data.info.makeApplication(data.restrictedBackupMode, null);

            // Propagate autofill compat state
            app.setAutofillCompatibilityEnabled(data.autofillCompatibilityEnabled);

            mInitialApplication = app;

            // don't bring up providers in restricted mode; they may depend on the
            // app's custom Application class
            if (!data.restrictedBackupMode) {
                if (!ArrayUtils.isEmpty(data.providers)) {
                    // 创建ContentProviders
                    installContentProviders(app, data.providers);
                    // For process that contains content providers, we want to
                    // ensure that the JIT is enabled "at some point".
                    mH.sendEmptyMessageDelayed(H.ENABLE_JIT, 10*1000);
                }
            }

            // Do this after providers, since instrumentation tests generally start their
            // test thread at this point, and we don't want that racing.
            try {
                mInstrumentation.onCreate(data.instrumentationArgs);
            }
            catch (Exception e) {
                throw new RuntimeException(
                    "Exception thrown in onCreate() of "
                    + data.instrumentationName + ": " + e.toString(), e);
            }
            try {
                // Application的 onCreate
                mInstrumentation.callApplicationOnCreate(app);
            } catch (Exception e) {
                if (!mInstrumentation.onException(app, e)) {
                    throw new RuntimeException(
                      "Unable to create application " + app.getClass().getName()
                      + ": " + e.toString(), e);
                }
            }
        } finally {
            // If the app targets < O-MR1, or doesn't change the thread policy
            // during startup, clobber the policy to maintain behavior of b/36951662
            if (data.appInfo.targetSdkVersion < Build.VERSION_CODES.O_MR1
                    || StrictMode.getThreadPolicy().equals(writesAllowedPolicy)) {
                StrictMode.setThreadPolicy(savedPolicy);
            }
        }

        ...
    }

    // android/app/ActivityThread.java
    private void installContentProviders(
            Context context, List<ProviderInfo> providers) {
        final ArrayList<ContentProviderHolder> results = new ArrayList<>();

        for (ProviderInfo cpi : providers) {
            if (DEBUG_PROVIDER) {
                StringBuilder buf = new StringBuilder(128);
                buf.append("Pub ");
                buf.append(cpi.authority);
                buf.append(": ");
                buf.append(cpi.name);
                Log.i(TAG, buf.toString());
            }
            ContentProviderHolder cph = installProvider(context, null, cpi,
                    false /*noisy*/, true /*noReleaseNeeded*/, true /*stable*/);
            if (cph != null) {
                cph.noReleaseNeeded = true;
                results.add(cph);
            }
        }

        try {
            ActivityManager.getService().publishContentProviders(
                getApplicationThread(), results);
        } catch (RemoteException ex) {
            throw ex.rethrowFromSystemServer();
        }
    }
```

## 内存泄漏原理

- 引用超过变量的生命周期
    - static activities/views
    - 非静态内部类
    - 匿名类
    - Handler
    - Thread
    - TimerTask
- 系统服务的listener, broadcastreceiver/ContentObserver
- 资源关闭 cusor,File
- WebView
- C++代码