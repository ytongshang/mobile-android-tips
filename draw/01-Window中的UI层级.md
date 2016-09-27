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

     //初始化window
     mWindow = new PhoneWindow(this);

    // 设置Window的回调
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

## setContentView

```java
  //PhoneWindow.java

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

## PhoneWindow中的setContentView

```java
  // PhoneWindow.java

  // 是setContentView设置的View的父布局，它是DecorView本身或者DecorView的子View
  // com.android.internal.R.id.content
  private ViewGroup mContentParent;

  // 根据不同的Window feature选择的Add 到mDecor布局的View根结点
  private ViewGroup mContentRoot;

  @Override
    public void setContentView(View view, ViewGroup.LayoutParams params) {
        // Note: FEATURE_CONTENT_TRANSITIONS may be set in the process of installing the window
        // decor, when theme attributes and the like are crystalized. Do not check the feature
        // before this happens.
        if (mContentParent == null) {
            // 如果contentParent为空的话，
            // 将生成一个DecorView,其实际上是一个FrameLayout
            installDecor();
        } else if (!hasFeature(FEATURE_CONTENT_TRANSITIONS)) {
            // FEATURE_CONTENT_TRANSITIONS指转场动画，是在API21引入的
            mContentParent.removeAllViews();
        }

        if (hasFeature(FEATURE_CONTENT_TRANSITIONS)) {
            // 通过转场动画切换到新页面
            view.setLayoutParams(params);
            final Scene newScene = new Scene(mContentParent, view);
            transitionTo(newScene);
        } else {
            mContentParent.addView(view, params);
        }
        mContentParent.requestApplyInsets();

        // 当mContentParent内容发生变化时，回调通过到Activity相应方法
        final Callback cb = getCallback();
        if (cb != null && !isDestroyed()) {
            cb.onContentChanged();
        }
    }
```

## installDecor

```java
  private void installDecor() {
        if (mDecor == null) {
            // 创建一个DecorView，也就是Activity所有View的根布局
            mDecor = generateDecor();
            mDecor.setDescendantFocusability(ViewGroup.FOCUS_AFTER_DESCENDANTS);
            mDecor.setIsRootNamespace(true);
            if (!mInvalidatePanelMenuPosted && mInvalidatePanelMenuFeatures != 0) {
                mDecor.postOnAnimation(mInvalidatePanelMenuRunnable);
            }
        }

        // 创建contentParent,也就是我们setContentView的父布局
        if (mContentParent == null) {
            // mContentParent一定是一个FrameLayout,但是加载进mDecor的布局
            // 会因为有不同的选项，而选用不同的布局
            mContentParent = generateLayout(mDecor);

            // ..........
            // 省略其它代码
            }
        }
    }
```

## generateLayout

```java
  protected ViewGroup generateLayout(DecorView decor) {
        // Apply data from current theme.

        TypedArray a = getWindowStyle();

        if (false) {
            System.out.println("From style:");
            String s = "Attrs:";
            for (int i = 0; i < R.styleable.Window.length; i++) {
                s = s + " " + Integer.toHexString(R.styleable.Window[i]) + "="
                        + a.getString(i);
            }
            System.out.println(s);
        }

        //设置window的属性
        mIsFloating = a.getBoolean(R.styleable.Window_windowIsFloating, false);

        // ..........
        // 省略其它代码

        // 根据Window属性选用特定的布局
        int layoutResource;
        int features = getLocalFeatures();

        // ..........
        // 省略其它代码

        mDecor.startChanging();

        //将选择的布局加载到mDecor上面
        View in = mLayoutInflater.inflate(layoutResource, null);
        decor.addView(in, new ViewGroup.LayoutParams(MATCH_PARENT, MATCH_PARENT));
        mContentRoot = (ViewGroup) in;

        // 但是无论选用哪一个布局，都会有一个叫com.android.internal.R.id.content的FrameLayout
        // 这个也就是我们后面setContentView生成View的父布局
        // 所以名字叫作 content parent
        ViewGroup contentParent = (ViewGroup)findViewById(ID_ANDROID_CONTENT);
        if (contentParent == null) {
            throw new RuntimeException("Window couldn't find content container view");
        }

        // ..........
        // 省略其它代码
        // 设置其它的属性

        mDecor.finishChanging();

        return contentParent;
    }
```

# 总结

- 首先创建一个DecorView,该DecorView对象将作为整个应用窗口的根视图。

- 创依据Feature等style theme选择不同的窗口修饰布局文件，并且通过findViewById获取Activity布局文件该存放的地方（窗口修饰布局文件中id为content的FrameLayout）。

- 将Activity的布局文件添加至id为content的FrameLayout内。

- 当setContentView设置显示完成后，回调到Activity的onContentChanged方法

- 整个ActivityUI布局层次为:DecorView(FrameLayout)->DecorView 的mContentRoot(不确定ViewGroup类型) -> DecorView 的mContentParent(FrameLayout)->通过setContentView设置进来的View
