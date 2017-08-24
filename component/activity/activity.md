# Activity

- [google activity guide](http://developer.android.com/guide/components/activities.html)

## activity的生命周期

### 生命周期图解

![activity生命周期](./../../image-resources/activity_lifecycle.png)

### 生命周期

- 一般情况下，onPause后面会执行onStop，但是**如果新的activity采用了透明主题，那么当前activity不会执行onStop**
- **如果当前为Activity A，打开了一个新的Activity B,那么会先执行A的onPause,然后才会执行B的 onCreate, onStart, onResume**

Method | Description | Killable after? | Next
------- | ------- | ------- | -------
onCreate() | Called when the activity is first created. This is where you should do all of your normal static set up — create views, bind data to lists, and so on. This method is passed a Bundle object containing the activity's previous state, if that state was captured (see Saving Activity State, later).Always followed by onStart().  | No | onStart()
onRestart() | Called after the activity has been stopped, just prior to it being started again.Always followed by onStart() | No | onStart()
onStart() | Called just before the activity becomes visible to the user.Followed by onResume() if the activity comes to the foreground, or onStop() if it becomes hidden.| No | onResume() or onStop()
onResume() | Called just before the activity starts interacting with the user. At this point the activity is at the top of the activity stack, with user input going to it.Always followed by onPause(). | No | onPause()
onPause() | Called when the system is about to start resuming another activity. This method is typically used to commit unsaved changes to persistent data, stop animations and other things that may be consuming CPU, and so on. It should do whatever it does very quickly, because the next activity will not be resumed until it returns.Followed either by onResume() if the activity returns back to the front, or by onStop() if it becomes invisible to the user. | Yes | onResume() or onStop()
onStop() | Called when the activity is no longer visible to the user. This may happen because it is being destroyed, or because another activity (either an existing one or a new one) has been resumed and is covering it.Followed either by onRestart() if the activity is coming back to interact with the user, or byonDestroy() if this activity is going away. | Yes | onRestart() or onDestroy()
onDestroy() | Called before the activity is destroyed. This is the final call that the activity will receive. It could be called either because the activity is finishing (someone called finish() on it), or because the system is temporarily destroying this instance of the activity to save space. You can distinguish between these two scenarios with the isFinishing() method. | Yes | nothing

### 其它

- **因为一旦activity进入onPause,我们就有可能不再“回来了”,所以应当持久化我们还未保存的操作**，比如提交数据库的修改，
 提交sharedPrefences中的修改，或者停止动画好，又或者停止一些消耗cpu的行为，都在onPause中进行
- **在onPause进行持久化操作时，只能够在onPause中执行一些耗时很短的操作**，因为只有当前一个activity的onPause执行完成，
 后一个activity才能执行onCreate
- activity只要经历了onPause,onStopped,onDestroy中的一个，系统都可能杀死activity所在的process,从而导致后面的生命周期函数不会被调用
- 一旦activity停止了，系统会在需要内存空间时摧毁它的实例。极端情况下，系统会直接杀死我们的app进程，并不执行activity的onDestroy()回调方法,
 因此我们需要使用onStop()来释放资源，从而避免内存泄漏。我们在onStop里面做了哪些清除的操作，就该在onStart里面重新把那些清除掉的资源重新创建出来，


## 重新创建activity

### restore activity

![restore activity](./../../image-resources/activity_restore_instance.png)

- 正常情况下，当activity进入paused或都stopped状态的时候，activity状态、数据都会保存的, 当activity再次进入resumed状态的时候，可以还原原先的状态
- 但是在极端情况下，activity会被销毁，系统会调用onSaveInstanceState()来保存当前Activity的状态
- **onSaveInstanceState方法会在onStop之前调用，它和onPause没有既定的时序关系**，可以在onPause之前，也可以在onPause之后
- Activity重建的时候，可以通过onCreate和onRestoreInstanceState方法将保存的信息还原,两个方法选择一个就可以了，**官方文档建议我们采用onRestoreInstanceState的方法**
- **onRestoreInstanceState方法调用的时机是在onStart方法以后**
- onSaveInstanceState保存的bundle对象可以从onCreate或者onRestoreInstanceState中获取，两者的区别是，
 **onCreate中的bundle对象在正常启动的情况下为null,所以要进行非null判断，**
 **而onRestoreInstanceState方法中的bundle一定不会为空**
- **具有Id的View也会保存自身的状态**，具体保存了哪些信息，可以查看View的onSaveInstanceState方法

```java
static final String STATE_SCORE = "playerScore";
static final String STATE_LEVEL = "playerLevel";
...
@Override
public void onSaveInstanceState(Bundle savedInstanceState) {
    // Save the user's current game state
    savedInstanceState.putInt(STATE_SCORE, mCurrentScore);
    savedInstanceState.putInt(STATE_LEVEL, mCurrentLevel);
    // Always call the superclass so it can save the view hierarchy state
    super.onSaveInstanceState(savedInstanceState);
}

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState); // Always call the superclass first
    // Check whether we're recreating a previously destroyed instance
    if (savedInstanceState != null) {
        // Restore value of members from saved state
        mCurrentScore = savedInstanceState.getInt(STATE_SCORE);
        mCurrentLevel = savedInstanceState.getInt(STATE_LEVEL);
    } else {
        // Probably initialize members with default values for a new instance
    }
    ...
}

@Override
public void onRestoreInstanceState(Bundle savedInstanceState) {
    // Always call the superclass so it can restore the view hierarchy
    super.onRestoreInstanceState(savedInstanceState);
    // Restore state members from saved instance
    mCurrentScore = savedInstanceState.getInt(STATE_SCORE);
    mCurrentLevel = savedInstanceState.getInt(STATE_LEVEL);
}
```

### 资源相关的系统配置发生变化引起activity重建

- **系统配置发生了变化，在默认情况下，Activity就会被销毁并且重新创建**，当然我们也可以阻止系统重新创建我们的Activity
- **系统配置有很多内容，如果当某项内容发生变化后，我们不想系统重新创建Activity，可以给Activity指定configChanges属性**
- 如果我们没有configChanges中指定该选项的话，当该项配置发生变化后会导致Activity重建


- configChanges项目和含义

Value | Description
------|------------
“mcc“ | 移动国家号码，由三位数字组成，每个国家都有自己独立的MCC，可以识别手机用户所属国家。
“mnc“ | 移动网号，在一个国家或者地区中，用于区分手机用户的服务商。
“locale“ | 用户所在地区发生变化，一般指切换了系统语言
“touchscreen“ | 触摸屏发生了变化，这个很费解，正常情况下无法发生，可以忽略它
“keyboard“ | 键盘模式发生变化，例如：用户接入外部键盘输入。
“keyboardHidden“ | 键盘的可访问性发生了变化，比如调出了键盘
“navigation“ | 系统导航方式发生了变化，比如采用了轨迹球，可以忽略它
“screenLayout” | 屏幕布局发生了变化，很可能是用户激活了另外一个显示设备
“fontScale“ | 全局字体大小缩放发生改变
“uiMode“ | 用户界面模式发生了改变，比如开启了夜间模式
“orientation“ | 设备旋转，横向显示和竖向显示模式切换。
“screenSize“ | 屏幕尺寸信息发生了变化,当旋转设备屏幕时,屏幕尺寸大小会发生变化,当minSdkVersion和targetSdkVersion>=13时,会导致activity重启，否则不会
“smallestScreenSize“ |  设备物理屏幕大小发生了变化，比如使用了外部显示设备，当minSdkVersion和targetSdkVersion>=13时,会导致activity重启，否则不会
“layoutDirection” | 当布局方向发生变化，比较少见，一般不无须修改布局的layoutDirection,API17引入

- **Api13以上如果希望orientation发生变化，Activity不会重启，那么一定要将orientation结合screenSize使用**

- **当configChanges中的指定的项目发生变化时，会回调onConfigurationChanged(Configuration config) 函数**

```java

public void onConfigurationChanged(Configuration newConfig) {
    super.onConfigurationChanged( newConfig);
    //...
}
```

```xml

<!-- orientation ,keyboardHidden, navigation,locale, screensize发生变化后，activity不重启 -->
<activity
    android:name=".view.activity.GameZoneActivity"
    android:configChanges="orientation|keyboardHidden|navigation|locale|screenSize"
    android:screenOrientation="portrait"
    android:theme="@style/MyAppTheme"/>
```

### 资源内存不足时导致低优先级的Activity被杀死

- 优先级ForgreGround, Visible，Service, Background, Empty
- 一些后台工作不适合脱离4个组件而独立运行在后台中，这样进程很容易被杀死，比较好的方法是将后台工作放入Service从而保持进程有一定的优先级