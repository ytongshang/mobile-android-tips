# Snippet

- [获得资源id](#获得资源id)
- [获得android res文件下的uri](#获得android-res文件下的uri)
- [给我们评分](#给我们评分)
- [release的位置](#release的位置)
- [Handler的使用](#handler的使用)
- [dialogFragment设置宽度](#dialogfragment设置宽度)
- [bitmap的平铺](#bitmap的平铺)
- [监听Home键](#监听home键)
- [悬浮窗类型](#悬浮窗类型)
- [App启动黑屏解决办法](#app启动黑屏解决办法)

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

## dialogFragment设置宽度

- DialogFragment左右距离屏幕都是默认有一定的padding,但是在API里并没有设置方法

- 解决办法，在onStart方法中手动设置dialogFragment的宽度

```java
    @Override
    public void onStart() {
        super.onStart();
        Window window = getDialog().getWindow();
        if (window != null) {
            window.setBackgroundDrawableResource(android.R.color.transparent);
            WindowManager.LayoutParams lp = window.getAttributes();
            lp.width = (int) (AppUtils.getScreenSize(getActivity()).x / 1.5);
            window.setAttributes(lp);
        }
    }
```

- 注意：**必须给window设置background，上面这种设置dialogFragment的宽度的方法才有效**

```java

    <style name="alert_dialog" parent="android:Theme.Dialog">
        <item name="android:windowIsFloating">true</item>
        <item name="android:windowIsTranslucent">false</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:windowFullscreen">false</item>
        <item name="android:windowBackground">@color/float_transparent</item>
        <item name="android:windowAnimationStyle">@null</item>
        <item name="android:backgroundDimEnabled">true</item>
    </style>

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setStyle(DialogFragment.STYLE_NO_TITLE, R.style.alert_dialog);
    }

```

- 使用dialogfragment时，不要通过onCreateDialog创建dialog,仅仅通过onCreateDialog设置dialog的style,
 dialog的动画等

```java

public abstract class BaseDialog extends DialogFragment {
    protected Context mContext;

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mContext = getActivity();
        setStyle(DialogFragment.STYLE_NO_TITLE, R.style.alert_dialog);
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        Dialog dialog = super.onCreateDialog(savedInstanceState);
        dialog.setCanceledOnTouchOutside(true);
        Window window = dialog.getWindow();
        if (window != null) {
            window.setWindowAnimations(R.style.alert_dialog_animation);
        }
        return dialog;
    }

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = initDialog(inflater, container, savedInstanceState);
        initData(v);
        return v;
    }

    @Override
    public void show(FragmentManager manager, String tag) {
        FragmentTransaction ft = manager.beginTransaction();
        ft.add(this, tag);
        ft.commitAllowingStateLoss();
    }

    public abstract View initDialog(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState);

    public abstract void initData(View v);

}

<style name="alert_dialog_animation" parent="android:Theme.Dialog">
    <item name="android:windowEnterAnimation">@anim/zues_sweetalert_modal_in</item>
    <item name="android:windowExitAnimation">@anim/zues_sweetalert_modal_out</item>
</style>

```

## bitmap的平铺

- 有时时候，给我们一个小的图片，通过将图片不拉伸重复平铺形成背景图,类似于将一张小图作为电脑桌面的效果

```xml

<xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/backrepeat"／>

<!-- backrepeat.xml-->
<bitmap
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:src="@drawable/repeatimg"
    android:tileMode="repeat"
    android:dither="true" />

```

- 代码方式

```java

Bitmap bitmap = BitmapFactory.decodeResource(getResources(), R.drawable.repeatimg);
BitmapDrawable bd = new BitmapDrawable(bitmap);
bd.setTileModeXY(TileMode.REPEAT , TileMode.REPEAT );
bd.setDither(true);
view.setBackgroundDrawable(bd);

```

## 监听Home键

- **android中home键按下的分发是分发给系统framework的，不会分发给onKeyDown的**，所以监听onkeydown是没有用的
- 一般通过监听广播的事件来实现
- 另外一方式可以重载activity的onUserLeaveHint,这个方法会在onPause之后执行
- 系统的很多行为都是通过广播形式来分发消息的，**具体的广播可以参看Intent中定义的static final action**

```java

public class HomeKeyReceiver extends BroadcastReceiver {
    private static final String LOG_TAG = "HomeKeyReceiver";
    private static final String SYSTEM_DIALOG_REASON_KEY = "reason";
    private static final String SYSTEM_DIALOG_REASON_RECENT_APPS = "recentapps";
    private static final String SYSTEM_DIALOG_REASON_HOME_KEY = "homekey";
    private static final String SYSTEM_DIALOG_REASON_LOCK = "lock";
    private static final String SYSTEM_DIALOG_REASON_ASSIST = "assist";

    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        Log.i(LOG_TAG, "onReceive: action: " + action);
        if (action.equals(Intent.ACTION_CLOSE_SYSTEM_DIALOGS)) {
            // android.intent.action.CLOSE_SYSTEM_DIALOGS
            String reason = intent.getStringExtra(SYSTEM_DIALOG_REASON_KEY);
            Log.i(LOG_TAG, "reason: " + reason);

            if (SYSTEM_DIALOG_REASON_HOME_KEY.equals(reason)) {
                // 短按Home键
                Log.i(LOG_TAG, "homekey");
            }
            else if (SYSTEM_DIALOG_REASON_RECENT_APPS.equals(reason)) {
                // 长按Home键 或者 activity切换键
                Log.i(LOG_TAG, "long press home key or activity switch");
            }
            else if (SYSTEM_DIALOG_REASON_LOCK.equals(reason)) {
                // 锁屏
                Log.i(LOG_TAG, "lock");
            }
            else if (SYSTEM_DIALOG_REASON_ASSIST.equals(reason)) {
                // samsung 长按Home键
                Log.i(LOG_TAG, "assist");
            }
        }
    }
}

```

## 悬浮窗类型

- 悬浮窗也就是在WindowManager上加上view
- 悬浮窗类型**WindowManager.LayoutParams.TYPE_TOAST与WindowManager.LayoutParams.TYPE_SYSTEM_ALERT**
- TYPE_TOAST在19以下的系统上无法接收touch事件
- 7.0及以上系统，TOAST类型窗口只能有一个，已被系统Toast控件用掉，其他的浮窗需要用别的类型
- 使用TYPE_SYSTEM_ALERT类型的悬浮窗,**必须具有权限 android.permission.SYSTEM_ALERT_WINDOW**

```java

if (Build.VERSION.SDK_INT >= 19 && Build.VERSION.SDK_INT < 24) {
    mWindowManagerParams.type = WindowManager.LayoutParams.TYPE_TOAST;
} else {
    mWindowManagerParams.type = WindowManager.LayoutParams.TYPE_SYSTEM_ALERT;
}

```

## App启动黑屏解决办法

[Android启动页黑屏及最优解决方案](https://juejin.im/post/58ad90518ac2472a2ad9b684)

- 在启动的Activity的主题中设置windowBackground为具体的图片资源
- 必须为图片资，也可以是可以解决为bitmap的资源

```xml
<style name="APPTheme" parent="@android:style/Theme.Holo.NoActionBar">
    <item name="android:windowBackground">@drawable/splash_icon</item>
</style>

<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:opacity="opaque">
    <item android:drawable="@color/white"/>
    <item>
        <bitmap
            android:gravity="center"
            android:src="@drawable/qq"/>
    </item>
</layer-list>
```

- 启动完成之后，设置windowbackground为null

```java
@Override
protected void onCreate(@Nullable Bundle savedInstanceState) {
    //将window的背景图设置为空
    getWindow().setBackgroundDrawable(null);
    super.onCreate(savedInstanceState);
}
```
