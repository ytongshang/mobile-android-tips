# ViewPager

## FragmentPagerAdapter 与 FragmentStatePagerAdapter

- **问题描述：** 最近做一个项目，要根据搜索的结果显示一个ViewPager,ViewPager的每一个页面都是fragment，原先 用的FragmentPagerAdapter, 数据发生变化后，调用notifydatasetchanged没用，fragment没有重建

- **解决思路：** FragmentPagerAdapter更多的用于少量界面的ViewPager。划过的fragment会保存在内存中，尽管已经划过。而FragmentStatePagerAdapter和ListView有点类似，会保存当前界面，以及下一个界面和上一个界面（如果有），最多保存3个，其他会被销毁掉。如果fragment的数据源发生了变化，而且需要重新构建fragment的时候，应当采用FragmentStatePagerAdapter, 这时候调用adapter的notifydatasetchanged才会有效果

## ViewPager的数据请求问题

- **问题描述：** 有时ViewPager的每一个页面都有数据请求，正确做法应当是只有切换到了该页面，才会去请求数据，而不是在每一个页面创建的时候就请求数据了。

- **解决思路：** 做法是为ViewPager设置OnPageChangeListener,只有选择了那个页面，才会请求数据，并且只请求一次

  ```java
  viewpager的OnPageChangeListener

  @Override
   public void onPageSelected(int position) {
       BaseFragment fragment = mFragmentList.get(position);
       fragment.startRequest();
   }

   ...........

   具体的fragment,并且在请求成功后，将boolean设为true

   public void startRequest() {
        if(!mIsRequested) {
            getList();
        }
    }
  ```

## ViewPager的滑动问题

- **问题描述：** im录音的一个界面，parent是一个ViewPager,在界面按下按钮录音，这个时候应当让ViewPager不能够左右滑动。

- **解决思路：** ViewPager在滑动时会拦截触摸事件，所以只要可以设定ViewPager什么时候拦截，什么时候不拦截触摸事件就行

  ```java
  public class KasViewPager extends ViewPager {
    //if true, keep View don't move
    private boolean mNoFocus = false;

    public KasViewPager(Context context) {
        this(context, null);
    }

    public KasViewPager(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    @Override
    public boolean onInterceptTouchEvent(MotionEvent event) {
      if (mNoFocus) {
        return false;
      }
      return super.onInterceptTouchEvent(event);
    }

    public void setNoFocus(boolean b) {
        mNoFocus = b;
    }
  }
  ```
