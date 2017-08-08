# UsageStatsManager

## 简介

- UsageStatsManager就是使用情况统计管理者，通过它可以获取应用的使用情况
- 系统会统计应用的使用情况并保存起来，然后按照这些保存起来的信息的时间长短进行划分

## 统计数据组别

- 日长短级别数据：Daily data， 最长7天内的数据
- 星期长短级别数据：Weekly data最长4个星期内的数据
- 月长短级别数据： Monthly data最长6个月内的数据
- 年长短级别数据： Yearly data最长2年内的数据，也就是说，数据最长保存2年

## 统计数据类型

- 对于每一个应用来说，系统会记录以下信息：
    - 应用最后一次被用的时间
    - 对应存储的4个级别，应用在前台的总共时间
    - 时间戳：一个组件一天之内改变状态的时刻（从前台到后台，或从后台到前台），这个组件可以通过包名或activity的名字来唯一标示。
    - 时间戳：设备配置信息改变的时刻，如：横竖屏切换。

## 使用

### 首先声明权限

```xml
<uses-permission android:name="android.permission.PACKAGE_USAGE_STATS"
                     tools:ignore="ProtectedPermissions"/>
```

### 手动确保拥有对应的权限

```java
@TargetApi(Build.VERSION_CODES.LOLLIPOP)
private static boolean checkUsageStatsPermission(Context context) {
    try {
        PackageManager packageManager = context.getPackageManager();
        ApplicationInfo applicationInfo = packageManager.getApplicationInfo(context.getPackageName(), 0);
        AppOpsManager appOpsManager = (AppOpsManager) context.getSystemService(Context.APP_OPS_SERVICE);
        int mode = appOpsManager.checkOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS, applicationInfo.uid, applicationInfo.packageName);
        return (mode == AppOpsManager.MODE_ALLOWED);
    } catch (PackageManager.NameNotFoundException e) {
        return false;
    }
}

if (Build.VERSION.SDK_INT >=21 && !checkUsageStatsPermission(context)) {
    RecAlertDialog.RecBuilder builder = RecAlertDialog.builder(mContext)
        .setMessage(R.string.camera_permission_dialog_content)
        .setPositiveButton(R.string.done, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(intent);
            }
        });
        builder.setCancelable(false);
        AlertDialogActivity.alert(builder);
        AlertDialogActivity.show(mContext);
}
```

### 具体使用

```java
Calendar calendar=Calendar.getInstance();
calendar.setTime(new Date());

//结束时间
long endt = calendar.getTimeInMillis();
//时间间隔为一个月
calendar.add(Calendar.DAY_OF_MONTH, -1);
//开始时间
long statt = calendar.getTimeInMillis();
UsageStatsManager usageStatsManager=(UsageStatsManager) getSystemService(USAGE_STATS_SERVICE);

//获取一个月内的信息
List<UsageStats> queryUsageStats = usageStatsManager.queryUsageStats(UsageStatsManager.INTERVAL_MONTHLY,statt,endt);
```

- **无论使用哪种级别，start和end都必须时时间戳**
- **在设置时间间隔时，最好不要将时间间隔设置的太短**，否则如果没有上面对应的数据，查询的数据很可能是为空的

## 检则前台app

- android 21以前

```java
private String getForegroundApp () {
    ActivityManager mActivityManager =(ActivityManager) mContext.getSystemService(Context.ACTIVITY_SERVICE);
    if (mActivityManager.getRunningTasks(1) == null) {
        Log.e(TAG, "running task is null, ams is abnormal!!!");
        return null;
    }
    ActivityManager.RunningTaskInfo mRunningTask = mActivityManager.getRunningTasks(1).get(0);
    if (mRunningTask == null) {
        Log.e(TAG, "failed to get RunningTaskInfo");
        return null;
    }

    return mRunningTask.topActivity.getPackageName();
    }
```

- android 21以后

```java
@TargetApi(21)
private String getForegroundAppL (Context context) {
    UsageStatsManager usageStatsManager =(UsageStatsManager) context.getSystemService(Context.USAGE_STATS_SERVICE);
    long ts = System.currentTimeMillis();
    // 收集20s以内的app使用情况，情间不能太短，否则会返回为空
    UsageEvents usageEvents = usageStatsManager.queryEvents(ts - 20000, ts);
    if (usageEvents == null) {
        return null;
    }

    UsageEvents.Event event = new UsageEvents.Event();
    UsageEvents.Event lastEvent = null;
    while (usageEvents.hasNextEvent()) {
        usageEvents.getNextEvent(event);
            // if from notification bar, class name will be null
        if (event.getPackageName() == null || event.getClassName() == null) {
            continue;
        }

        if (lastEvent == null || lastEvent.getTimeStamp() < event.getTimeStamp()) {
            lastEvent = event;
        }
    }

    if (lastEvent == null) {
        return null;
    }
    return lastEvent.getPackageName();

}
```