# 流程

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

- 每一个视图的绘制过程都必须经历三个最主要的阶段，即onMeasure()、onLayout()和onDraw()

# onMeasure

- measure()方法接收两个参数，widthMeasureSpec和heightMeasureSpec，这两个值分别用于确定视图的宽度和高度的规格和大小,MeasureSpec的值由specSize和specMode共同组成的，其中specSize记录的是大小，specMode记录的是规格,specMode一共有三种

  - EXACTLY,表示父视图希望子视图的大小应该是由specSize的值来决定的，系统默认会按照这个规则来设置子视图的大小,
  - AT_MOST,表示子视图最多只能是specSize中指定的大小，开发人员应该尽可能小得去设置这个视图，并且保证不会超过specSize。
  - UNSPECIFIED,表示开发人员可以将视图按照自己的意愿设置成任意的大小，没有任何限制

- MeasureSpec中的specSize指定的是这个View在父容器中的layout_width或layout_height

- View系统的绘制流程会从ViewRoot的performTraversals()方法中开始。

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

- 根View的widthMeasureSpec与heightMeasureSpec由window的大小,与它的ViewGroup.LayoutParams决定

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

- View的测量从measure()方法开始，然后调用onMeasure()方法

  ```java
  protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        setMeasuredDimension(getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec),
                getDefaultSize(getSuggestedMinimumHeight(), heightMeasureSpec));
    }

  public static int getDefaultSize(int size, int measureSpec) {
        int result = size;
        int specMode = MeasureSpec.getMode(measureSpec);
        int specSize = MeasureSpec.getSize(measureSpec);

        switch (specMode) {
        case MeasureSpec.UNSPECIFIED:
            result = size;
            break;
        case MeasureSpec.AT_MOST:
        case MeasureSpec.EXACTLY:
            result = specSize;
            break;
        }
        return result;
    }
  ```
