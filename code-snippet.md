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
