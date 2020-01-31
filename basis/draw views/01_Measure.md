# 流程

- 每一个视图的绘制过程都必须经历三个最主要的阶段，即measure、layout和draw

## MeasureSpec

- MeasureSpec代表一个32位的int值，高2位代表测量模式（AT_MOST,EXECTLY,UNSPECIFIED）,底30位代表SpecSize
- 在测量的过程中，系统会将View的LayoutParams根据父容器所施加的规则转换成对应的MeasureSpec,然后根据这个MeasureSpec去测量View的高和宽
- **MeasureSpec由LayoutParams和父容器一起决定**
- 测量模式
    - EXACTLY,表示父视图希望子视图的大小应该是由specSize的值来决定的，系统默认会按照这个规则来设置子视图的大小,
    - AT_MOST,表示子视图最多只能是specSize中指定的大小，开发人员应该尽可能小得去设置这个视图，并且保证不会超过specSize。
    - UNSPECIFIED,表示开发人员可以将视图按照自己的意愿设置成任意的大小，没有任何限制

## Measure的流程

- ViewRootImpl的performTraversals方法中调用performMeasure方法
- performMeasure方法通过调用ViewRootImpl的根View,也就是DectorView的measure()方法去测量View树的大小
- DectorView的measure()会调用其自身的onMeasure()方法，因为DectorView是FrameLayout，进而会调用FrameLayout的测量方法
- **在onMeasure方法中，一方面需要通过调用setMeasuredDimension()方法去设置自身的测量宽高mMeasuredWidth和mMeasureHeight**，另一方面，如果该View对象是个ViewGroup，需要重写该onMeasure()方法，对其子视图进行遍历测量大小
- 对每个子视图的measure()过程，可以调用父类ViewGroup类里的measureChild(),measureChildWithMargins(),measureChildren(),或本身的measure()方法进行测量。

```java
        // android/view/ViewRootImpl.java
        private void performTraversals() {
            ...
            if (!mStopped || mReportNextDraw) {
                boolean focusChangedDueToTouchMode = ensureTouchModeLocally(
                        (relayoutResult&WindowManagerGlobal.RELAYOUT_RES_IN_TOUCH_MODE) != 0);
                if (focusChangedDueToTouchMode || mWidth != host.getMeasuredWidth()
                        || mHeight != host.getMeasuredHeight() || contentInsetsChanged ||
                        updatedConfiguration) {
                    int childWidthMeasureSpec = getRootMeasureSpec(mWidth, lp.width);
                    int childHeightMeasureSpec = getRootMeasureSpec(mHeight, lp.height);

                    if (DEBUG_LAYOUT) Log.v(mTag, "Ooops, something changed!  mWidth="
                            + mWidth + " measuredWidth=" + host.getMeasuredWidth()
                            + " mHeight=" + mHeight
                            + " measuredHeight=" + host.getMeasuredHeight()
                            + " coveredInsetsChanged=" + contentInsetsChanged);

                     // Ask host how big it wants to be
                     // 执行Measure
                    performMeasure(childWidthMeasureSpec, childHeightMeasureSpec);

                    // Implementation of weights from WindowManager.LayoutParams
                    // We just grow the dimensions as needed and re-measure if
                    // needs be
                    int width = host.getMeasuredWidth();
                    int height = host.getMeasuredHeight();
                    boolean measureAgain = false;

                    // 如果View水平需要占用剩下的空间
                    if (lp.horizontalWeight > 0.0f) {
                        width += (int) ((mWidth - width) * lp.horizontalWeight);
                        childWidthMeasureSpec = MeasureSpec.makeMeasureSpec(width,
                                MeasureSpec.EXACTLY);
                        measureAgain = true;
                    }
                     // 如果View竖直需要占用剩下的空间
                    if (lp.verticalWeight > 0.0f) {
                        height += (int) ((mHeight - height) * lp.verticalWeight);
                        childHeightMeasureSpec = MeasureSpec.makeMeasureSpec(height,
                                MeasureSpec.EXACTLY);
                        measureAgain = true;
                    }

                    if (measureAgain) {
                        if (DEBUG_LAYOUT) Log.v(mTag,
                                "And hey let's measure once more: width=" + width
                                + " height=" + height);
                        // 重新进行Measure
                        performMeasure(childWidthMeasureSpec, childHeightMeasureSpec);
                    }

                    layoutRequested = true;
                }
            }
        } else {
            // Not the first pass and no window/insets/visibility change but the window
            // may have moved and we need check that and if so to update the left and right
            // in the attach info. We translate only the window frame since on window move
            // the window manager tells us only for the new frame but the insets are the
            // same and we do not want to translate them more than once.
            maybeHandleWindowMove(frame);
        }

        final boolean didLayout = layoutRequested && (!mStopped || mReportNextDraw);
        boolean triggerGlobalLayoutListener = didLayout
                || mAttachInfo.mRecomputeGlobalAttributes;
        if (didLayout) {
            // 进行Layout
            performLayout(lp, mWidth, mHeight);
            ...
        }
        ...
        boolean cancelDraw = mAttachInfo.mTreeObserver.dispatchOnPreDraw() || !isViewVisible;

        if (!cancelDraw && !newSurface) {
            if (mPendingTransitions != null && mPendingTransitions.size() > 0) {
                for (int i = 0; i < mPendingTransitions.size(); ++i) {
                    mPendingTransitions.get(i).startChangingAnimations();
                }
                mPendingTransitions.clear();
            }
            // 进行绘制
            performDraw();
        } else {
            if (isViewVisible) {
                // Try again
                scheduleTraversals();
            } else if (mPendingTransitions != null && mPendingTransitions.size() > 0) {
                for (int i = 0; i < mPendingTransitions.size(); ++i) {
                    mPendingTransitions.get(i).endChangingAnimations();
                }
                mPendingTransitions.clear();
            }
        }

        mIsInTraversal = false;
    }

    // DecorView的MesaureSpec
    private static int getRootMeasureSpec(int windowSize, int rootDimension) {
        int measureSpec;
        switch (rootDimension) {
        case ViewGroup.LayoutParams.MATCH_PARENT:
            // Window can't resize. Force root view to be windowSize.
            measureSpec = MeasureSpec.makeMeasureSpec(windowSize, MeasureSpec.EXACTLY);
            break;
        case ViewGroup.LayoutParams.WRAP_CONTENT:
            // Window can resize. Set max size for root view.
            measureSpec = MeasureSpec.makeMeasureSpec(windowSize, MeasureSpec.AT_MOST);
            break;
        default:
            // Window wants to be an exact size. Force root view to be that size.
            measureSpec = MeasureSpec.makeMeasureSpec(rootDimension, MeasureSpec.EXACTLY);
            break;
        }
        return measureSpec;
    }

    // android/view/ViewRootImpl.java
    private void performMeasure(int childWidthMeasureSpec, int childHeightMeasureSpec) {
        if (mView == null) {
            return;
        }
        Trace.traceBegin(Trace.TRACE_TAG_VIEW, "measure");
        try {
            mView.measure(childWidthMeasureSpec, childHeightMeasureSpec);
        } finally {
            Trace.traceEnd(Trace.TRACE_TAG_VIEW);
        }
    }
```

```java
// android/view/View.java
public final void measure(int widthMeasureSpec, int heightMeasureSpec) {
        boolean optical = isLayoutModeOptical(this);
        if (optical != isLayoutModeOptical(mParent)) {
            Insets insets = getOpticalInsets();
            int oWidth  = insets.left + insets.right;
            int oHeight = insets.top  + insets.bottom;
            widthMeasureSpec  = MeasureSpec.adjust(widthMeasureSpec,  optical ? -oWidth  : oWidth);
            heightMeasureSpec = MeasureSpec.adjust(heightMeasureSpec, optical ? -oHeight : oHeight);
        }

        // Suppress sign extension for the low bytes
        long key = (long) widthMeasureSpec << 32 | (long) heightMeasureSpec & 0xffffffffL;
        if (mMeasureCache == null) mMeasureCache = new LongSparseLongArray(2);

        final boolean forceLayout = (mPrivateFlags & PFLAG_FORCE_LAYOUT) == PFLAG_FORCE_LAYOUT;

        // Optimize layout by avoiding an extra EXACTLY pass when the view is
        // already measured as the correct size. In API 23 and below, this
        // extra pass is required to make LinearLayout re-distribute weight.
        // 如果传进来是exactly并且当前的大小已经是这么大了，那么可以减少测量的次数
        final boolean specChanged = widthMeasureSpec != mOldWidthMeasureSpec
                || heightMeasureSpec != mOldHeightMeasureSpec;
        final boolean isSpecExactly = MeasureSpec.getMode(widthMeasureSpec) == MeasureSpec.EXACTLY
                && MeasureSpec.getMode(heightMeasureSpec) == MeasureSpec.EXACTLY;
        final boolean matchesSpecSize = getMeasuredWidth() == MeasureSpec.getSize(widthMeasureSpec)
                && getMeasuredHeight() == MeasureSpec.getSize(heightMeasureSpec);
        final boolean needsLayout = specChanged
                && (sAlwaysRemeasureExactly || !isSpecExactly || !matchesSpecSize);

        if (forceLayout || needsLayout) {
            // first clears the measured dimension flag
            mPrivateFlags &= ~PFLAG_MEASURED_DIMENSION_SET;

            resolveRtlPropertiesIfNeeded();

            int cacheIndex = forceLayout ? -1 : mMeasureCache.indexOfKey(key);
            if (cacheIndex < 0 || sIgnoreMeasureCache) {
                // onMeasure进行测试
                // measure ourselves, this should set the measured dimension flag back
                onMeasure(widthMeasureSpec, heightMeasureSpec);
                mPrivateFlags3 &= ~PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
            } else {
                // 使用缓存
                long value = mMeasureCache.valueAt(cacheIndex);
                // Casting a long to int drops the high 32 bits, no mask needed
                setMeasuredDimensionRaw((int) (value >> 32), (int) value);
                mPrivateFlags3 |= PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
            }

            // flag not set, setMeasuredDimension() was not invoked, we raise
            // an exception to warn the developer
            if ((mPrivateFlags & PFLAG_MEASURED_DIMENSION_SET) != PFLAG_MEASURED_DIMENSION_SET) {
                throw new IllegalStateException("View with id " + getId() + ": "
                        + getClass().getName() + "#onMeasure() did not set the"
                        + " measured dimension by calling"
                        + " setMeasuredDimension()");
            }

            mPrivateFlags |= PFLAG_LAYOUT_REQUIRED;
        }

        mOldWidthMeasureSpec = widthMeasureSpec;
        mOldHeightMeasureSpec = heightMeasureSpec;

        mMeasureCache.put(key, ((long) mMeasuredWidth) << 32 |
                (long) mMeasuredHeight & 0xffffffffL); // suppress sign extension
    }
```

## ViewGroup

- ViewGroup是一个抽象类，它没有重写onMeasure方法，因此当我们直接继承ViewGroup时，必须重写onMeasure方法

### measureChild

- **measureChild，其中已经考虑了padding,但没有考虑margin**,用来测量子View的大小

```java

  protected void measureChild(View child, int parentWidthMeasureSpec,int parentHeightMeasureSpec) {
        final LayoutParams lp = child.getLayoutParams();
        // 考虑了父ViewGroup的padding
        final int childWidthMeasureSpec = getChildMeasureSpec(parentWidthMeasureSpec,mPaddingLeft + mPaddingRight, lp.width);
        final int childHeightMeasureSpec = getChildMeasureSpec(parentHeightMeasureSpec,mPaddingTop + mPaddingBottom, lp.height);
        child.measure(childWidthMeasureSpec, childHeightMeasureSpec);
    }

```

### getChildMeasureSpec

- 当View采用固定宽/高时，无论父容器的MeasureSpec是什么，View的MeasureSpec都是精确模式并且大小遵循LayoutParams的大小
- 当View的宽/高是match_parent时
    - 如果父容器是精确模式，那么View也是精确模式，并且大小为父容器剩余的大小
    - 如果父容器是最大模式，那么View也是最大模式，并且大小不会超过父容器的剩余的大小
- 当View的宽/高是wrap_content时，无论父容器的模式是最大化还是准确，View的模式总是最大化，并且大小不能超过父容器剩余的大小

```java

    public static int getChildMeasureSpec(int spec, int padding, int childDimension) {
           int specMode = MeasureSpec.getMode(spec);
           int specSize = MeasureSpec.getSize(spec);

           int size = Math.max(0, specSize - padding);

           int resultSize = 0;
           int resultMode = 0;

           switch (specMode) {
           // Parent has imposed an exact size on us
           case MeasureSpec.EXACTLY:
               if (childDimension >= 0) {
                   resultSize = childDimension;
                   resultMode = MeasureSpec.EXACTLY;
               } else if (childDimension == LayoutParams.MATCH_PARENT) {
                   // Child wants to be our size. So be it.
                   resultSize = size;
                   resultMode = MeasureSpec.EXACTLY;
               } else if (childDimension == LayoutParams.WRAP_CONTENT) {
                   // Child wants to determine its own size. It can't be
                   // bigger than us.
                   resultSize = size;
                   resultMode = MeasureSpec.AT_MOST;
               }
               break;

           // Parent has imposed a maximum size on us
           case MeasureSpec.AT_MOST:
               if (childDimension >= 0) {
                   // Child wants a specific size... so be it
                   resultSize = childDimension;
                   resultMode = MeasureSpec.EXACTLY;
               } else if (childDimension == LayoutParams.MATCH_PARENT) {
                   // Child wants to be our size, but our size is not fixed.
                   // Constrain child to not be bigger than us.
                   resultSize = size;
                   resultMode = MeasureSpec.AT_MOST;
               } else if (childDimension == LayoutParams.WRAP_CONTENT) {
                   // Child wants to determine its own size. It can't be
                   // bigger than us.
                   resultSize = size;
                   resultMode = MeasureSpec.AT_MOST;
               }
               break;

           // Parent asked to see how big we want to be
           case MeasureSpec.UNSPECIFIED:
               if (childDimension >= 0) {
                   // Child wants a specific size... let him have it
                   resultSize = childDimension;
                   resultMode = MeasureSpec.EXACTLY;
               } else if (childDimension == LayoutParams.MATCH_PARENT) {
                   // Child wants to be our size... find out how big it should
                   // be
                   resultSize = View.sUseZeroUnspecifiedMeasureSpec ? 0 : size;
                   resultMode = MeasureSpec.UNSPECIFIED;
               } else if (childDimension == LayoutParams.WRAP_CONTENT) {
                   // Child wants to determine its own size.... find out how
                   // big it should be
                   resultSize = View.sUseZeroUnspecifiedMeasureSpec ? 0 : size;
                   resultMode = MeasureSpec.UNSPECIFIED;
               }
               break;
           }
           return MeasureSpec.makeMeasureSpec(resultSize, resultMode);
       }
```

### measureChildWithMargins

- 有的时候，需要考虑margin，此时，应当调用measureChildWithMargins

```java

    protected void measureChildWithMargins(View child,int parentWidthMeasureSpec, int widthUsed,int parentHeightMeasureSpec, int heightUsed) {

        //子视图的LayoutParams必须是MarginLayoutParams
        final MarginLayoutParams lp = (MarginLayoutParams) child.getLayoutParams();

        final int childWidthMeasureSpec = getChildMeasureSpec(parentWidthMeasureSpec,
            mPaddingLeft + mPaddingRight + lp.leftMargin + lp.rightMargin + widthUsed, lp.width);
        final int childHeightMeasureSpec = getChildMeasureSpec(parentHeightMeasureSpec,
            mPaddingTop + mPaddingBottom + lp.topMargin + lp.bottomMargin+ heightUsed, lp.height);

        child.measure(childWidthMeasureSpec, childHeightMeasureSpec);
    }

```

- **使用measureChildWithMargins时,View的LayoutMargins必须是MarginLayoutParams**
- 有时候，当我们继承ViewGroup实现自定义ViewGroup时，子View的LayoutParams不是MarginLayoutParams的时候，可以通过重写下面方法，生成MarginLayoutParams

```java

      @Override
      protected LayoutParams generateLayoutParams(LayoutParams p) {
          return new MarginLayoutParams(p);
      }

      @Override
      public LayoutParams generateLayoutParams(AttributeSet attrs) {
          return new MarginLayoutParams(getContext(), attrs);
      }

```

### measureChildren

- ViewGroup中定义了一个measureChildren()方法来去测量子视图的大小

```java

  protected void measureChildren(int widthMeasureSpec, int heightMeasureSpec) {
        final int size = mChildrenCount;
        final View[] children = mChildren;
        for (int i = 0; i < size; ++i) {
            final View child = children[i];
            // GONE的View是不占大小的，而VISIBLE和INVISIBLE都是会占据空间的
            if ((child.mViewFlags & VISIBILITY_MASK) != GONE) {
                measureChild(child, widthMeasureSpec, heightMeasureSpec);
            }
        }
    }

```

### 自定义ViewGroup的onMeasure方法

```java

protected void onMeasure(int height , int width){
    // 1. 测量本身的大小，然后设置测量宽(mMeasuredWidth)，测量高(mMeasuredHeight)
    // 设置测量宽和测量高是能过setMeasuredDimension完成的
    setMeasuredDimension(h , l) ;

     //2、如果该View是ViewGroup，则对它的每个子View进行measure()
    int childCount = getChildCount() ;

    for(int i=0 ;i<childCount ;i++){
        View child = getChildAt(i) ;
        // Gone的
        if (View.getVisibility != View.GONE) {
            // 测量子View的大小,哪种方法都是可以的
            measureChildWithMargins(child , h, i) ;
            //measureChild(child , h, i) ;
            //child.measure(h,l);
        }
    }
}

```

## View

- View的测量从measure()方法开始，measure是一个final方法，子类不能够重写该方法

```java

public final void measure(int widthMeasureSpec, int heightMeasureSpec) {
        boolean optical = isLayoutModeOptical(this);
        if (optical != isLayoutModeOptical(mParent)) {
            Insets insets = getOpticalInsets();
            int oWidth  = insets.left + insets.right;
            int oHeight = insets.top  + insets.bottom;
            widthMeasureSpec  = MeasureSpec.adjust(widthMeasureSpec,  optical ? -oWidth  : oWidth);
            heightMeasureSpec = MeasureSpec.adjust(heightMeasureSpec, optical ? -oHeight : oHeight);
        }

        // Suppress sign extension for the low bytes
        long key = (long) widthMeasureSpec << 32 | (long) heightMeasureSpec & 0xffffffffL;
        if (mMeasureCache == null) mMeasureCache = new LongSparseLongArray(2);

        final boolean forceLayout = (mPrivateFlags & PFLAG_FORCE_LAYOUT) == PFLAG_FORCE_LAYOUT;

        // Optimize layout by avoiding an extra EXACTLY pass when the view is
        // already measured as the correct size. In API 23 and below, this
        // extra pass is required to make LinearLayout re-distribute weight.
        final boolean specChanged = widthMeasureSpec != mOldWidthMeasureSpec
                || heightMeasureSpec != mOldHeightMeasureSpec;
        final boolean isSpecExactly = MeasureSpec.getMode(widthMeasureSpec) == MeasureSpec.EXACTLY
                && MeasureSpec.getMode(heightMeasureSpec) == MeasureSpec.EXACTLY;
        final boolean matchesSpecSize = getMeasuredWidth() == MeasureSpec.getSize(widthMeasureSpec)
                && getMeasuredHeight() == MeasureSpec.getSize(heightMeasureSpec);
        final boolean needsLayout = specChanged
                && (sAlwaysRemeasureExactly || !isSpecExactly || !matchesSpecSize);

        if (forceLayout || needsLayout) {
            // first clears the measured dimension flag
            mPrivateFlags &= ~PFLAG_MEASURED_DIMENSION_SET;

            resolveRtlPropertiesIfNeeded();

            int cacheIndex = forceLayout ? -1 : mMeasureCache.indexOfKey(key);
            if (cacheIndex < 0 || sIgnoreMeasureCache) {
                // measure ourselves, this should set the measured dimension flag back
                onMeasure(widthMeasureSpec, heightMeasureSpec);
                mPrivateFlags3 &= ~PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
            } else {
                long value = mMeasureCache.valueAt(cacheIndex);
                // Casting a long to int drops the high 32 bits, no mask needed
                setMeasuredDimensionRaw((int) (value >> 32), (int) value);
                mPrivateFlags3 |= PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
            }

            // flag not set, setMeasuredDimension() was not invoked, we raise
            // an exception to warn the developer
            if ((mPrivateFlags & PFLAG_MEASURED_DIMENSION_SET) != PFLAG_MEASURED_DIMENSION_SET) {
                throw new IllegalStateException("View with id " + getId() + ": "
                        + getClass().getName() + "#onMeasure() did not set the"
                        + " measured dimension by calling"
                        + " setMeasuredDimension()");
            }

            mPrivateFlags |= PFLAG_LAYOUT_REQUIRED;
        }

        mOldWidthMeasureSpec = widthMeasureSpec;
        mOldHeightMeasureSpec = heightMeasureSpec;

        mMeasureCache.put(key, ((long) mMeasuredWidth) << 32 |
                (long) mMeasuredHeight & 0xffffffffL); // suppress sign extension
    }

```

### onMeasure

- **调用onMeasure()方法时会传入通过父容器通过measureChild或measureChildWithMargins生成的measureSpec**
- 完成一次测量后，通过setMeasuredDimension()设定视图的大小，这样就完成了一次测量
- **在重写onMeasure方法是一方面必须最终调用setMeasuredDimension,来设置View的测量大小**
- **另一方面必须保证宽度和高度和最小宽度/最小高度之间的关系**

```java

  protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    setMeasuredDimension(getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec),
      getDefaultSize(getSuggestedMinimumHeight(), heightMeasureSpec));
  }

```

### getDefaultSize

- **直接继承View的控件，在UNSPECIFIED下它的测量宽/高为最小宽和最小高**
- 在AT_MOST和EXACTLY模式下，返回的是父容器的剩余的大小

```java

  public static int getDefaultSize(int size, int measureSpec) {
        int result = size;
        // measureSpec是父容器的相关数据
        int specMode = MeasureSpec.getMode(measureSpec);
        int specSize = MeasureSpec.getSize(measureSpec);

        switch (specMode) {
        case MeasureSpec.UNSPECIFIED:
            // 没有指定的时候，设置为最小的宽和高
            result = size;
            break;
        case MeasureSpec.AT_MOST:
        case MeasureSpec.EXACTLY:
            // 默认行为，width和height不可能超过父容器，都设置为父容器的大小
            result = specSize;
            break;
        }
        return result;
    }

```

- **也就是说直接继承View的控件，它的wrap_content属性是无效的**，
 解决办法是直接继承View的控件，当我们使用wrap_content，去给它指定一个固定的宽和高

```java

protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    //... 其中mWidth是一个具体的数值，比如100，或者通过minWidth指定的数值都行
    if (widthSpecMode == MeasureSpec.AT_MOST) {
        setMeasuredDimen(mWidth, heightSpecSize);
    }
}

```

### 最小宽度/高度

- getSuggestedMinimumWidth，**对于如果View没有设置背景，那么返回android：minWidth的所指定的数值，可能为0**
 **如果设置了背景，则返回android：minWidth和背景最小宽度这两者中的最大值**
- **getSuggestedMinimumWidth和getSuggestedMininumHeight返回的是View在UNSPECIFIED模式下的测量宽/测量高**

```java

  // view的最小宽度，由背景和设置的最小宽度共同决定
  protected int getSuggestedMinimumWidth() {
    return (mBackground == null) ? mMinWidth : max(mMinWidth, mBackground.getMinimumWidth());
  }

  ```

## View的高度

- **View的测量高/测量宽，getMeasuredWidth(),getMeasuredHeight(),是在经过measure()后才能够获取的**
- **View的高和宽，getWidth，getHeight是在经过layout之后才能够获取的**
- **一般情况下，getMeasuredWidth=getWidth， getMeasuredHeight = getHeight，但是两者是可能不同的**

## measure还没执行完，获得MeasureWidth

### Activity/View#onWindowFocusChanged

```java
public void onWindowFocusChanged(boolean hasFocus) {
    super.onWindowFocusChanged(hasFocus);
    if (hasFocus) {
        int width = view.getMeasuredWidth();
        int height = view.getMeasuredHeight();
    }
}
```

### View的post方法

```java
protected void onStart() {
    super.onStart();
    view.post(new Runnable() {

        @Override
        public void run() {
             int width = view.getMeasuredWidth();
             int height = view.getMeasuredHeight();
        }
    });
}
```

### ViewTreeObserver

```java
protected void onStart() {
    super.onStart();
    ViewTreeObserver observer = view.getViewTreeObserver();
    observer.addOnGlobalLayoutListener (new OnGlobalLayoutListener() {

        @Override
        public void onGlobalLayout() {
           view.getViewTreeObserver().removeGlobalOnGlobalLayoutListener(this);
            int width = view.getMeasuredWidth();
             int height = view.getMeasuredHeight();
        }
    });
}

```

### View.measure(int widthMeasureSpec, int heightMeasureSpec)

#### match_parent

- 无法获得，因为spec为父容器剩下的大小，而父容器大小还没有得到

#### 具体的数值

```java
int widthMeasureSpec = MeasureSpec.makeMeasureSpec(100, MeasureSpec.EXACTLY);
int heightMeasureSpec = MeasureSpec.makeMeasureSpec(100, MeasureSpec.EXACTLY);
view.measure(widthMeasureSpec, widthMeasureSpec);
```

#### wrap_content

```java
int widthMeasureSpec = MeasureSpec.makeMeasureSpec((1<<30)-1, MeasureSpec.AT_MOST);
int heightMeasureSpec = MeasureSpec.makeMeasureSpec((1<<30)-1, MeasureSpec.AT_MOST);
view.measure(widthMeasureSpec,heightMeasureSpec);
```