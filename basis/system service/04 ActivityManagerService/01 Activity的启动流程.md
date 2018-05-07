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

- Step 1~Step4总结：这4步都是在Launcher中执行的

### Step 1: Launcher.startActivitySafely

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

### Step2: Activity.startActivity

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

### Step3: Instrumentation.execStartActivity

- Instrumentation用来监控应用程序与系统之间的交互操作
- 可以跟踪application及activity生命周期，一般用在测试框架中较多
- contextThread 为ActivityThread内的ApplicationThread
- IBinder token
    - token是Activity的内部成员变量mToken，类型为IBinder,**指向了ActivityManagerService中一个类型为ActivityRecord的Binder本地对象**
    - 每一个已经启动的Activity组件在ActivityManagerService中都有一个对应的ActivityRecord对象，用来维护Activity组件的运行状态和信息，
    - **mToken对象的赋值是发生在在Activity的attach方法中进行的**

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

### Step4: ActivityManager.getService().startActivity

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

### Step5:ActivityManagerService.startActivity,ActivityManagerService.startActivityAsUser

- Ste

```java
// ActivityManagerService.java 4516
@Override
    public final int startActivity(IApplicationThread caller, String callingPackage,
            Intent intent, String resolvedType, IBinder resultTo, String resultWho, int requestCode,
            int startFlags, ProfilerInfo profilerInfo, Bundle bOptions) {
        return startActivityAsUser(caller, callingPackage, intent, resolvedType, resultTo,
                resultWho, requestCode, startFlags, profilerInfo, bOptions,
                UserHandle.getCallingUserId());
    }

    @Override
    public final int startActivityAsUser(IApplicationThread caller, String callingPackage,
            Intent intent, String resolvedType, IBinder resultTo, String resultWho, int requestCode,
            int startFlags, ProfilerInfo profilerInfo, Bundle bOptions, int userId) {
        enforceNotIsolatedCaller("startActivity");
        userId = mUserController.handleIncomingUser(Binder.getCallingPid(), Binder.getCallingUid(),
                userId, false, ALLOW_FULL_ONLY, "startActivity", null);
        // TODO: Switch to user app stacks here.
        return mActivityStarter.startActivityMayWait(caller, -1, callingPackage, intent,
                resolvedType, null, null, resultTo, resultWho, requestCode, startFlags,
                profilerInfo, null, null, bOptions, false, userId, null, "startActivityAsUser");
    }
```

### Step6:ActivityStarter.startActivityMayWait

```java
// ActivityStarter.java 673
final int startActivityMayWait(IApplicationThread caller, int callingUid,
            String callingPackage, Intent intent, String resolvedType,
            IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
            IBinder resultTo, String resultWho, int requestCode, int startFlags,
            ProfilerInfo profilerInfo, WaitResult outResult,
            Configuration globalConfig, Bundle bOptions, boolean ignoreTargetSecurity, int userId,
            TaskRecord inTask, String reason) {
        // Refuse possible leaked file descriptors

        ...
       // 省略若干行代码

        boolean componentSpecified = intent.getComponent() != null;

         ...
       // 省略若干行代码

        //解析Intent
        ResolveInfo rInfo = mSupervisor.resolveIntent(intent, resolvedType, userId);
         ...
       // 省略若干行代码

        // Collect information about the target of the Intent.
        // 根据Intent和上面的resolveInfo获得我们真正要启动的Activity的信息
        ActivityInfo aInfo = mSupervisor.resolveActivity(intent, rInfo, startFlags, profilerInfo);

        ActivityOptions options = ActivityOptions.fromBundle(bOptions);
        synchronized (mService) {
            ...
            // 省略若干行代码

            // 调用 startActivityLocked进行下一步的启动
            final ActivityRecord[] outRecord = new ActivityRecord[1];
            int res = startActivityLocked(caller, intent, ephemeralIntent, resolvedType,
                    aInfo, rInfo, voiceSession, voiceInteractor,
                    resultTo, resultWho, requestCode, callingPid,
                    callingUid, callingPackage, realCallingPid, realCallingUid, startFlags,
                    options, ignoreTargetSecurity, componentSpecified, outRecord, inTask,
                    reason);

            Binder.restoreCallingIdentity(origId);

            ...
             // 省略若干行代码
            return res;
        }
    }
```

### Step7:ActivityStarter.startActivityLocked

```java
// ActivityStarter.java 263
int startActivityLocked(IApplicationThread caller, Intent intent, Intent ephemeralIntent,
            String resolvedType, ActivityInfo aInfo, ResolveInfo rInfo,
            IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
            IBinder resultTo, String resultWho, int requestCode, int callingPid, int callingUid,
            String callingPackage, int realCallingPid, int realCallingUid, int startFlags,
            ActivityOptions options, boolean ignoreTargetSecurity, boolean componentSpecified,
            ActivityRecord[] outActivity, TaskRecord inTask, String reason) {

        if (TextUtils.isEmpty(reason)) {
            throw new IllegalArgumentException("Need to specify a reason.");
        }
        mLastStartReason = reason;
        mLastStartActivityTimeMs = System.currentTimeMillis();
        mLastStartActivityRecord[0] = null;

        mLastStartActivityResult = startActivity(caller, intent, ephemeralIntent, resolvedType,
                aInfo, rInfo, voiceSession, voiceInteractor, resultTo, resultWho, requestCode,
                callingPid, callingUid, callingPackage, realCallingPid, realCallingUid, startFlags,
                options, ignoreTargetSecurity, componentSpecified, mLastStartActivityRecord,
                inTask);

        ...
        // 省略若干行代码
    }

    /** DO NOT call this method directly. Use {@link #startActivityLocked} instead. */
    private int startActivity(IApplicationThread caller, Intent intent, Intent ephemeralIntent,
            String resolvedType, ActivityInfo aInfo, ResolveInfo rInfo,
            IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
            IBinder resultTo, String resultWho, int requestCode, int callingPid, int callingUid,
            String callingPackage, int realCallingPid, int realCallingUid, int startFlags,
            ActivityOptions options, boolean ignoreTargetSecurity, boolean componentSpecified,
            ActivityRecord[] outActivity, TaskRecord inTask) {
        int err = ActivityManager.START_SUCCESS;
        // Pull the optional Ephemeral Installer-only bundle out of the options early.
        final Bundle verificationBundle
                = options != null ? options.popAppVerificationBundle() : null;

        ProcessRecord callerApp = null;
        if (caller != null) {
            callerApp = mService.getRecordForAppLocked(caller);
            if (callerApp != null) {
                callingPid = callerApp.pid;
                callingUid = callerApp.info.uid;
            } else {
                Slog.w(TAG, "Unable to find app for caller " + caller
                        + " (pid=" + callingPid + ") when starting: "
                        + intent.toString());
                err = ActivityManager.START_PERMISSION_DENIED;
            }
        }

        final int userId = aInfo != null ? UserHandle.getUserId(aInfo.applicationInfo.uid) : 0;

        if (err == ActivityManager.START_SUCCESS) {
            Slog.i(TAG, "START u" + userId + " {" + intent.toShortString(true, true, true, false)
                    + "} from uid " + callingUid);
        }

        ActivityRecord sourceRecord = null;
        ActivityRecord resultRecord = null;
        if (resultTo != null) {
            sourceRecord = mSupervisor.isInAnyStackLocked(resultTo);
            if (DEBUG_RESULTS) Slog.v(TAG_RESULTS,
                    "Will send result to " + resultTo + " " + sourceRecord);
            if (sourceRecord != null) {
                if (requestCode >= 0 && !sourceRecord.finishing) {
                    resultRecord = sourceRecord;
                }
            }
        }

        ...
        // 省略若干行代码

        ActivityRecord r = new ActivityRecord(mService, callerApp, callingPid, callingUid,
                callingPackage, intent, resolvedType, aInfo, mService.getGlobalConfiguration(),
                resultRecord, resultWho, requestCode, componentSpecified, voiceSession != null,
                mSupervisor, options, sourceRecord);
        if (outActivity != null) {
            outActivity[0] = r;
        }

        ...
        // 省略若干行代码

        return startActivity(r, sourceRecord, voiceSession, voiceInteractor, startFlags, true,options, inTask, outActivity);
    }

     private int startActivity(final ActivityRecord r, ActivityRecord sourceRecord,
            IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
            int startFlags, boolean doResume, ActivityOptions options, TaskRecord inTask,
            ActivityRecord[] outActivity) {
        int result = START_CANCELED;
        try {
            mService.mWindowManager.deferSurfaceLayout();
            result = startActivityUnchecked(r, sourceRecord, voiceSession, voiceInteractor,
                    startFlags, doResume, options, inTask, outActivity);
        } finally {
            // If we are not able to proceed, disassociate the activity from the task. Leaving an
            // activity in an incomplete state can lead to issues, such as performing operations
            // without a window container.
            if (!ActivityManager.isStartResultSuccessful(result)
                    && mStartActivity.getTask() != null) {
                mStartActivity.getTask().removeActivity(mStartActivity);
            }
            mService.mWindowManager.continueSurfaceLayout();
        }

        postStartActivityProcessing(r, result, mSupervisor.getLastStack().mStackId,  mSourceRecord,
                mTargetStack);

        return result;
    }

```

### Step8:ActivityStarter.startActivityUnchecked

这个方法的一开始，进行了一些初始化与更新标志值的过程,setInitialState更新要启动的Activity到全局常量mStartActivity等。

```java
// ActivityStarter.java 1015
private int startActivityUnchecked(final ActivityRecord r, ActivityRecord sourceRecord,
            IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
            int startFlags, boolean doResume, ActivityOptions options, TaskRecord inTask) {

        setInitialState(r, options, inTask, doResume, startFlags, sourceRecord, voiceSession,
                voiceInteractor);

        computeLaunchingTaskFlags();

        computeSourceStack();

        mIntent.setFlags(mLaunchFlags);
        mReusedActivity = getReusableIntentActivity();
        ......
}
```

- setInitialState里设置了一些参数，其中有个函数 **sendNewTaskResultRequestIfNeeded, 如果我们调用startActivityForResult来启动Flag为FLAG_ACTIVITY_NEW_TASK的activity,onActivityForResult的结果是不正常的，只要我们一启动，原activity就会收到一个RESULT_CANCELED的返回值**。

```java
private void sendNewTaskResultRequestIfNeeded() {
        if (mStartActivity.resultTo != null && (mLaunchFlags & FLAG_ACTIVITY_NEW_TASK) != 0
                && mStartActivity.resultTo.task.stack != null) {
            // For whatever reason this activity is being launched into a new task...
            // yet the caller has requested a result back.  Well, that is pretty messed up,
            // so instead immediately send back a cancel and let the new task continue launched
            // as normal without a dependency on its originator.
            Slog.w(TAG, "Activity is launching as a new task, so cancelling activity result.");
            mStartActivity.resultTo.task.stack.sendActivityResultLocked(-1, mStartActivity.resultTo,
                    mStartActivity.resultWho, mStartActivity.requestCode, RESULT_CANCELED, null);
            mStartActivity.resultTo = null;
        }
    }
```

- getReusableIntentActivity是获取是否可以复用的Activity,如果是singleTask，如果存在满足条件的Activity，可能要将上面的Activity clear掉，
 而singleInstance则要查找是存否在满足条件的Activity

```java
// ActivityStarter.java 1136
 mReusedActivity = getReusableIntentActivity();
...
if (reusedActivity != null) {
    ...
    //省略若干行
}

 ...
//省略若干行

// 满足SingleTop条件的特殊处理
// If the activity being launched is the same as the one currently at the top, then
        // we need to check if it should only be launched once.
        final ActivityStack topStack = mSupervisor.mFocusedStack;
        final ActivityRecord topFocused = topStack.topActivity();
        final ActivityRecord top = topStack.topRunningNonDelayedActivityLocked(mNotTop);
        final boolean dontStart = top != null && mStartActivity.resultTo == null
                && top.realActivity.equals(mStartActivity.realActivity)
                && top.userId == mStartActivity.userId
                && top.app != null && top.app.thread != null
                && ((mLaunchFlags & FLAG_ACTIVITY_SINGLE_TOP) != 0
                || mLaunchSingleTop || mLaunchSingleTask);
        if (dontStart) {
            // For paranoia, make sure we have correctly resumed the top activity.
            topStack.mLastPausedActivity = null;
            if (mDoResume) {
                mSupervisor.resumeFocusedStackTopActivityLocked();
            }
            ActivityOptions.abort(mOptions);
            if ((mStartFlags & START_FLAG_ONLY_IF_NEEDED) != 0) {
                // We don't need to start a new activity, and the client said not to do
                // anything if that is the case, so this is it!
                return START_RETURN_INTENT_TO_CALLER;
            }

            //SingleTop调用onNewIntent
            deliverNewIntent(top);

            // Don't use mStartActivity.task to show the toast. We're not starting a new activity
            // but reusing 'top'. Fields in mStartActivity may not be fully initialized.
            mSupervisor.handleNonResizableTaskIfNeeded(top.getTask(), preferredLaunchStackId,
                    preferredLaunchDisplayId, topStack.mStackId);

            return START_DELIVERED_TO_TOP;
        }

```

- 判断是否需要创建一个新的TaskRecord,如果从Launcher点击，就会执行创建一个新的任务栈TaskRecord

```java
    // ActivityStarter.java 1169
        boolean newTask = false;
        final TaskRecord taskToAffiliate = (mLaunchTaskBehind && mSourceRecord != null)
                ? mSourceRecord.getTask() : null;

        // Should this be considered a new task?
        //下面的一段代码 实际上就是找到我们将要启动的activity应当放到哪一个任务栈中
        int result = START_SUCCESS;
        if (mStartActivity.resultTo == null && mInTask == null && !mAddingToTask
                && (mLaunchFlags & FLAG_ACTIVITY_NEW_TASK) != 0) {
            // 处理SingleTask的情况，复用原来的Task或创建新的Task
            newTask = true;
            result = setTaskFromReuseOrCreateNewTask(
                    taskToAffiliate, preferredLaunchStackId, topStack);
        } else if (mSourceRecord != null) {
            // 如果调用startActivity方法的Context也是一个Activity,复用Context的Task
            result = setTaskFromSourceRecord();
        } else if (mInTask != null) {
             // 如果我们设置了希望将启动的Activity放到哪个task中，一般指使用了taskaffiiliate
            result = setTaskFromInTask();
        } else {
            // 最后的情况，放在现在task的上面，或创建新的task
            // This not being started from an existing activity, and not part of a new task...
            // just put it in the top task, though these days this case should never happen.
            setTaskToCurrentTopOrCreateNewTask();
        }
        if (result != START_SUCCESS) {
            return result;
        }

        mService.grantUriPermissionFromIntentLocked(mCallingUid, mStartActivity.packageName,
                mIntent, mStartActivity.getUriPermissionsLocked(), mStartActivity.userId);
        mService.grantEphemeralAccessLocked(mStartActivity.userId, mIntent,
                mStartActivity.appInfo.uid, UserHandle.getAppId(mCallingUid));
        if (mSourceRecord != null) {
            mStartActivity.getTask().setTaskToReturnTo(mSourceRecord);
        }
        if (newTask) {
            EventLog.writeEvent(
                    EventLogTags.AM_CREATE_TASK, mStartActivity.userId,
                    mStartActivity.getTask().taskId);
        }
        ActivityStack.logStartActivity(
                EventLogTags.AM_CREATE_ACTIVITY, mStartActivity, mStartActivity.getTask());
        mTargetStack.mLastPausedActivity = null;

        sendPowerHintForLaunchStartIfNeeded(false /* forceSend */, mStartActivity);

        // 调用ActivityStack,也就是任务栈的启动Activity的方法
        mTargetStack.startActivityLocked(mStartActivity, topFocused, newTask, mKeepCurTransition,
                mOptions);
        if (mDoResume) {
            final ActivityRecord topTaskActivity =
                    mStartActivity.getTask().topRunningActivityLocked();
            if (!mTargetStack.isFocusable()
                    || (topTaskActivity != null && topTaskActivity.mTaskOverlay
                    && mStartActivity != topTaskActivity)) {
                // If the activity is not focusable, we can't resume it, but still would like to
                // make sure it becomes visible as it starts (this will also trigger entry
                // animation). An example of this are PIP activities.
                // Also, we don't want to resume activities in a task that currently has an overlay
                // as the starting activity just needs to be in the visible paused state until the
                // over is removed.
                mTargetStack.ensureActivitiesVisibleLocked(null, 0, !PRESERVE_WINDOWS);
                // Go ahead and tell window manager to execute app transition for this activity
                // since the app transition will not be triggered through the resume channel.
                mWindowManager.executeAppTransition();
            } else {
                // If the target stack was not previously focusable (previous top running activity
                // on that stack was not visible) then any prior calls to move the stack to the
                // will not update the focused stack.  If starting the new activity now allows the
                // task stack to be focusable, then ensure that we now update the focused stack
                // accordingly.
                if (mTargetStack.isFocusable() && !mSupervisor.isFocusedStack(mTargetStack)) {
                    mTargetStack.moveToFront("startActivityUnchecked");
                }
                mSupervisor.resumeFocusedStackTopActivityLocked(mTargetStack, mStartActivity,
                        mOptions);
            }
        } else {
            mTargetStack.addRecentActivityLocked(mStartActivity);
        }
        mSupervisor.updateUserStackLocked(mStartActivity.userId, mTargetStack);

        mSupervisor.handleNonResizableTaskIfNeeded(mStartActivity.getTask(), preferredLaunchStackId,
                preferredLaunchDisplayId, mTargetStack.mStackId);

        return START_SUCCESS;
```
