# Activity

## activity的生命周期

- 因为一旦activity进入onPause,我们就有可能不再“回来了”,所以持久化我们还未保存的操作，比如提交数据库的修改，
 提交sharedPrefences中的修改，或者停止动画好，又或者停止一些消耗cpu的行为，都在onPause中进行
- onPause进行这些动作，但是onPause中应当进行一些短时间的动作，因为只有当前一个activity 的onPause返回，
 后一个activity才能进入  onResume
- activity只要经历了onPause,onStopped,onDestroy中的一个，系统都可能杀死activity所在的process,从而导致后面的生命周期函数不会被调用
- 一旦activity停止了，系统会在需要内存空间时摧毁它的实例。极端情况下，系统会直接杀死我们的app进程，并不执行activity的onDestroy()回调方法, 因此我们需要使用onStop()来释放资源，从而避免内存泄漏。我们在onStop里面做了哪些清除的操作，就该在onStart里面重新把那些清除掉的资源重新创建出来，比如一般在onStart动态注册广播，在onStop取消注册

## 重新创建activity

- 正常情况下，当activity进入paused或都stopped状态的时候，activity所有的状态、数据都会保存的，当activity   再次进入resumed状 态的时候，可以还原原先的状态但是在极端情况下，activity会被销毁，这样，
 当back到原先activity 的时候，要重建activity,并不会回到原先的状态，这时应当调用onSaveInstanceState()
 调用onSaveInstanceState()，并且activity被销毁再次重建的时候，原先保存的Bundle对象会被传递到你我们activity的onRestoreInstanceState()方法与 onCreate() 方法中，选择其中的任何一个方法恢复到原先状态
- 只有activity被销毁，并且需要重建的时候，才会调用onSaveInstanceState()
- 如果保存的bundle没有数据是空的，是onSavedInstanceState是空的，所以要进行onSavedInstanceState !=null判断
- 通常来说，跳转到其他的activity或者是点击Home都会导致当前的activity执行onSaveInstanceState，因为这种情况下的activity都是有  可能会被destory并且是需要保存状态以便后续恢复使用的，而从跳转的activity点击back回到前一个activity，那么跳转前的activity是执   行退栈的操作，所以这种情况下是不会执行onSaveInstanceState的，因为这个activity不可能存在需要重建的操作
 系统默认onSaveInstanceState()会保存每个view的状态，因而在重写该方法时，要先调用super的，然后保存一引起比较重要的类的成员变量，来帮助重建activity

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
public void onRestoreInstanceState(Bundle savedInstanceState) {
    // Always call the superclass so it can restore the view hierarchy
    super.onRestoreInstanceState(savedInstanceState);
    // Restore state members from saved instance
    mCurrentScore = savedInstanceState.getInt(STATE_SCORE);
    mCurrentLevel = savedInstanceState.getInt(STATE_LEVEL);
}
```

## activity的协作

- activity a调用onPause();
- activity b 调用oncreate(), onPause(),onResume()
- activity a调用onStop();因些应当在a的onPause进行持久化操作