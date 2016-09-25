# Window

- Activity中有一个成员为Window，Window是一个抽象类，提供了绘制窗口的一组通用API
- Activity中Window的实例化对象为PhoneWindow，PhoneWindow是Window的具体继承实现类。

```java
// Activity.java
private Window mWindow;

//...
final void attach(Context context, ActivityThread aThread,
         Instrumentation instr, IBinder token, int ident,
         Application application, Intent intent, ActivityInfo info,
         CharSequence title, Activity parent, String id,
         NonConfigurationInstances lastNonConfigurationInstances,
         Configuration config, String referrer, IVoiceInteractor voiceInteractor) {
     attachBaseContext(context);

     mFragments.attachHost(null /*parent*/);

     mWindow = new PhoneWindow(this);
     mWindow.setCallback(this);
     //...
   }
```

- PhoneWindow类内部包含了一个DecorView对象，该DectorView对象是所有应用窗口(Activity界面)的根View。

  ```java
  // PhoneWindow.java
  // This is the top-level view of the window, containing the window decor.
    private DecorView mDecor;
  ```

- DecorView是PhoneWindow的内部类，是FrameLayout的子类，是对FrameLayout进行功能的修饰，是所有应用窗口的根View 。

# setContentView

- setContentView都是调用Window对应的方法

  ```java
  public void setContentView(@LayoutRes int layoutResID) {
    getWindow().setContentView(layoutResID);
    initWindowDecorActionBar();
  }

  public void setContentView(View view) {
    getWindow().setContentView(view);
    initWindowDecorActionBar();
  }

  public void setContentView(View view, ViewGroup.LayoutParams params) {
    getWindow().setContentView(view, params);
    initWindowDecorActionBar();
  }
  ```

  - PhoneWindow中的setContentView

  ```java
  //PhoneWindow.java
  //是我们setContentView设置的View的父布局，它是DecorView本身或者DecorView的子View
  private ViewGroup mContentParent;

  @Override
    public void setContentView(View view, ViewGroup.LayoutParams params) {
        // Note: FEATURE_CONTENT_TRANSITIONS may be set in the process of installing the window
        // decor, when theme attributes and the like are crystalized. Do not check the feature
        // before this happens.
        if (mContentParent == null) {
            installDecor();
        } else if (!hasFeature(FEATURE_CONTENT_TRANSITIONS)) {
            mContentParent.removeAllViews();
        }

        if (hasFeature(FEATURE_CONTENT_TRANSITIONS)) {
            view.setLayoutParams(params);
            final Scene newScene = new Scene(mContentParent, view);
            transitionTo(newScene);
        } else {
            mContentParent.addView(view, params);
        }
        mContentParent.requestApplyInsets();
        final Callback cb = getCallback();
        if (cb != null && !isDestroyed()) {
            cb.onContentChanged();
        }
    }
  ```
