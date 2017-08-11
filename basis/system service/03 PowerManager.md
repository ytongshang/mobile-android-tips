# PowerManager

- 需要权限

```xml
<uses-permission android:name="android.permission.WAKE_LOCK"/>
```

- **WakeLock的设置是 Activiy 级别的，不是针对整个Application应用的**

## 具体使用

```java
PowerManager pm = (PowerManager)getSystemService(Context.POWER_SERVICE);
WakeLock wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MyWakeLock");
wakeLock.acquire();
/** Do things requiring the CPU stay active */
wakeLock.release();
```

## levelAndFlags

```java
 public WakeLock newWakeLock(int levelAndFlags, String tag) {
    validateWakeLockParameters(levelAndFlags, tag);
    return new WakeLock(levelAndFlags, tag, mContext.getOpPackageName());
}
```

### Wake lock level

- **PARTIAL_WAKE_LOCK**：保持CPU 运转，屏幕和键盘灯有可能是关闭的
- **SCREEN_DIM_WAKE_LOCK**：Deprecated,保持CPU 运转，允许保持屏幕亮但有可能是灰的，允许关闭键盘灯
- **SCREEN_BRIGHT_WAKE_LOCK**：Deprecated,保持CPU 运转，屏幕高亮，允许关闭键盘灯
- **FULL_WAKE_LOCK**：Deprecated，保持CPU 运转，屏幕高亮，键盘灯也保持亮度

### Wake lock flag

- **ACQUIRE_CAUSES_WAKEUP**:正常情况下，调用wakelock.acquire()时不会唤醒device,如果原来屏幕是亮的，只会让屏幕一直亮下去，设置了ACQUIRE_CAUSES_WAKEUP会唤醒屏幕
- **ON_AFTER_RELEASE**：当lock被释放后,通过reset user activity timer使屏幕多亮一会儿

## 替换选择

- 可以使用android.view.WindowManager.LayoutParams#FLAG_KEEP_SCREEN_ON来保持屏幕亮度
- 屏幕亮着变暗由系统来管理
- 并且不需要Wake Lock权限

### 具体实现

- Step 1 设置flag

```java
@Override
protected void onCreate(Bundle bundle) {
    super.onCreate(bundle);
    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
}
```

- Step 2 设置activity的根view的属性keepScreenOn为true,可以调用方法或在xml中指定

```java
@Override
protected void onCreate(Bundle bundle) {
    super.onCreate(bundle);
    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    View view = getLayoutInflater().inflate(R.layout.layout_activity, null);
    view.setKeepScreenOn(true);
    setContentView(view);
}
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="fill_parent"
    android:layout_height="fill_parent"
    android:keepScreenOn="true" />
```