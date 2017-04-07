# Activity

## activity的生命周期

### 生命周期图解

![activity生命周期](./../../../image-resources/activity_lifecycle.png)

### 生命周期

- [google activity guide](http://developer.android.com/guide/components/activities.html)

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
- **在onPause进行持久化操作时，只应当在onPause中应当进行耗时很短的操作**，因为只有当前一个activity的onPause执行完成，
 后一个activity才能执行onResume
- activity只要经历了onPause,onStopped,onDestroy中的一个，系统都可能杀死activity所在的process,从而导致后面的生命周期函数不会被调用
- 一旦activity停止了，系统会在需要内存空间时摧毁它的实例。极端情况下，系统会直接杀死我们的app进程，并不执行activity的onDestroy()回调方法, 因此我们需要使用onStop()来释放资源，从而避免内存泄漏。我们在onStop里面做了哪些清除的操作，就该在onStart里面重新把那些清除掉的资源重新创建出来，**比如一般在onStart动态注册广播，在onStop取消注册**

## 重新创建activity

### restore activity 图解

![restore activity](./../../../image-resources/activity_restore_instance.png)


- 正常情况下，当activity进入paused或都stopped状态的时候，activity所有的状态、数据都会保存的，
 当activity再次进入resumed状态的时候，可以还原原先的状态
- 但是在极端情况下，activity会被销毁，这样，当回到原先activity 的时候，要重建activity,这时会调用onSaveInstanceState()，并且activity被销毁再次重建的时候，原先保存的Bundle对象会被传递到你我们activity的onRestoreInstanceState()方法与 onCreate() 方法中，选择其中的任何一个方法恢复到原先状态
- 只有activity被销毁，并且需要重建的时候，才会调用onSaveInstanceState()
- 如果没有保存数据，那么onSavedInstanceState可能是空的，**所以要进行onSavedInstanceState !=null判断**

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

## activity的协作

### activity a跳转到activity b

- activity a调用onPause();
- activity b 调用oncreate(), onPause(),onResume()
- activity a调用onStop(), onDestroy()
- 因些应当在a的onPause进行持久化操作