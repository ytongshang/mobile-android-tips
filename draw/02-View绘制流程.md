# 流程

- 每一个视图的绘制过程都必须经历三个最主要的阶段，即onMeasure()、onLayout()和onDraw()

# onMeasure

- measure()方法接收两个参数，widthMeasureSpec和heightMeasureSpec，这两个值分别用于确定视图的宽度和高度的规格和大小,MeasureSpec的值由specSize和specMode共同组成的，其中specSize记录的是大小，specMode记录的是规格,specMode一共有三种

  - EXACTLY,表示父视图希望子视图的大小应该是由specSize的值来决定的，系统默认会按照这个规则来设置子视图的大小,
  - AT_MOST,表示子视图最多只能是specSize中指定的大小，开发人员应该尽可能小得去设置这个视图，并且保证不会超过specSize。
  - UNSPECIFIED,表示开发人员可以将视图按照自己的意愿设置成任意的大小，没有任何限制

## DecorView

- activity的根View是DecorView，它被加载到WindowManager上

  ```java
  // activity.java
  void makeVisible() {
      if (!mWindowAdded) {
          ViewManager wm = getWindowManager();
          wm.addView(mDecor, getWindow().getAttributes());
          mWindowAdded = true;
        }
      mDecor.setVisibility(View.VISIBLE);
    }
  ```

- View系统的绘制流程会从ViewRootImpl的performTraversals()方法中开始。

  ```java
  // ViewRootImpl.java

  private void performTraversals() {
      ......
      //最外层的根视图的widthMeasureSpec和heightMeasureSpec由来
      //lp.width和lp.height和Window的大小决定
      int childWidthMeasureSpec = getRootMeasureSpec(mWidth, lp.width);
      int childHeightMeasureSpec = getRootMeasureSpec(mHeight, lp.height);
  }
  ```

- 根View,也就是DecorView的widthMeasureSpec与heightMeasureSpec是由Window的大小,以及它的的ViewGroup.LayoutParams共同决定

  ```java
  // ViewRootImpl.java
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
  ```

## View

- View的测量从measure()方法开始，然后调用onMeasure()方法,这时会传入父容器的MeasureSpec
- 完成一次测量后，通过setMeasuredDimension()设定视图的大小，这样就完成了一次测量
- 只有在setMeasuredDimension()方法调用之后，我们才能使用getMeasuredWidth()和getMeasuredHeight()来获取视图测量出的宽高，以此之前调用这两个方法得到的值都会是0
- 一般情况下，在指定了一个View的layout_width与layout_height的时候

  - 指定了具体大小（具体多少dp的）或者是MATCH_PARENT的，在测量的时候,它的specMode就是 MeasureSpec.EXACTLY,只不过MATCH_PARENT的时候，大小为父容器的大小，而指定具体大小的时候，就是具体的大小;
  - 而指定为WRAP_CONTENT的时候，它的specMode就是MeasureSpec.AT_MOST,它的大小也为父容器的大小

- 视图大小的控制是由父视图、布局文件、以及视图本身共同完成的，父视图会提供给子视图参考的大小，如果视图本身设置了背景，或设置了最小的宽，或设转眼了最小的高，也会对视图本身有影ktnk，除此之外开发人员可以在XML文件中指定视图的大小，然后视图本身会对最终的大小进行拍板

  ```java
  protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    // 自定义View实现onMeasure的时候，必须最终调用setMeasuredDimension,来设置View的大小
    // 另一点，自定义View时，也必须保证宽度和高度，与getSuggestedMinimumWidth()，getSuggestedMinimumHeight()的关系
    setMeasuredDimension(getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec),
      getDefaultSize(getSuggestedMinimumHeight(), heightMeasureSpec));
  }

  // view的最小宽度，由背景和设置的最小宽度共同决定
  protected int getSuggestedMinimumWidth() {
    return (mBackground == null) ? mMinWidth : max(mMinWidth, mBackground.getMinimumWidth());
  }

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

## ViewGroup

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

  protected void measureChild(View child, int parentWidthMeasureSpec,
            int parentHeightMeasureSpec) {
        final LayoutParams lp = child.getLayoutParams();

        // 考虑了父ViewGroup的padding
        final int childWidthMeasureSpec = getChildMeasureSpec(parentWidthMeasureSpec,
                mPaddingLeft + mPaddingRight, lp.width);
        final int childHeightMeasureSpec = getChildMeasureSpec(parentHeightMeasureSpec,
                mPaddingTop + mPaddingBottom, lp.height);

        child.measure(childWidthMeasureSpec, childHeightMeasureSpec);
    }

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

- ViewGroup在测量子视图的时候，已经考虑了自身的padding,有时候也要考虑子视图的margin，因而测量子视图有另外一个方法measureChildWithMargins

  - 子视图的ViewGroup.LayoutParams必须是MarginLayoutParams

    ```java
    protected void measureChildWithMargins(View child,
            int parentWidthMeasureSpec, int widthUsed,
            int parentHeightMeasureSpec, int heightUsed) {

        //子视图的LayoutParams必须是MarginLayoutParams      
        final MarginLayoutParams lp = (MarginLayoutParams) child.getLayoutParams();

        final int childWidthMeasureSpec = getChildMeasureSpec(parentWidthMeasureSpec,
                mPaddingLeft + mPaddingRight + lp.leftMargin + lp.rightMargin
                        + widthUsed, lp.width);
        final int childHeightMeasureSpec = getChildMeasureSpec(parentHeightMeasureSpec,
                mPaddingTop + mPaddingBottom + lp.topMargin + lp.bottomMargin
                        + heightUsed, lp.height);

        child.measure(childWidthMeasureSpec, childHeightMeasureSpec);
    }
    ```

    - 有时候，当ViewGroup的LayoutParams不是MarginLayoutParams的时候，可以通过重写下面方法，生成MarginLayoutParams

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
