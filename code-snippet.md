# Snippet

- [获得资源id](#获得资源id)
- [获得android res文件下的uri](#获得android-res文件下的uri)
- [给我们评分](#给我们评分)
- [release的位置](#release的位置)
- [Handler的使用](#handler的使用)
- [adb查看最上层的activity](#adb查看最上层的activity)


## 获得资源id

```java
Resources resources = context.getResources();
int indentify= getResources().getIdentifier("icon", "drawable", "org.anddev.android.testproject");

int resId = getResources().getIdentifier("background", "color", getPackageName());
startBtn.setTextColor(getResources().getColor(resId));

public static int getResourceId(Context context,String name,String type,String packageName) {
    Resources themeResources = null;
    PackageManager pm = context.getPackageManager();
    try {
        themeResources = pm.getResourcesForApplication(packageName);
        return themeResources.getIdentifier(name, type, packageName);
    } catch (NameNotFoundException e) {
        e.printStackTrace();
    }
    return 0;
 }
```

## 获得android res文件下的uri

- "res://" + 包名+类型名 + "/" + 资源id

```java
Uri uri = Uri.parse("android.resource://"+getPackageName()+"/"+R.raw.xinyueshenhua);
Uri uri = Uri.parse("android.resource://"+getPackageName()+"/"+R.drawable.ic_launcher);

public static  Uri getResourceUri(int resId,String packageName) {
    return Uri.parse("android.resource://"+packageName+"/"+resId);
}
```

## 给我们评分

```java
Intent intent = new Intent(Intent.ACTION_VIEW);
intent.setData(Uri.parse("market://details?id=" + mContext.getPackageName()));
if (intent.resolveActivity(mContext.getPackageManager()) != null) {
    startActivity(Intent.createChooser(intent, "给我们评分"));
}
```

## release的位置

- 一个App需要在退出时调用释放资源的release函数，那么释放函数应当放到主Activity的onPause中，否则如果在onDestroy中调用的话，如果快速的关闭再重启App,会关闭的前一个onDestroy在下一个onCreate后调用，可能出现问题

```java

@Override
protected void onPause() {
    super.onPause();
    if (isFinishing()) {
        release();
    }
}

```

## Handler的使用

- 使用handler的一方面要注意内存泄漏的问题，有时候要使用WeakRefrence，也可以不使用Handler，转而使用开源库[WeakHandler](https://github.com/badoo/android-weak-handler)

- 在界面销毁的时候，比如fragment与activity的ondestroy方法中，要取消handler发送的消息

```java
if (mHandler != null) {
    mHandler.removeCallbacksAndMessages(null);
    mHandler = null;
}
```

## adb查看最上层的activity

- 查看最上面的activity

```bash
Linux:
adb shell dumpsys activity | grep "mFocusedActivity"

windows:
adb shell dumpsys activity | findstr "mFocusedActivity"
```