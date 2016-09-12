# FragmentPagerAdapter 与 FragmentStatePagerAdapter

- 最近做一个项目，要根据搜索的结果显示一个ViewPager,ViewPager的每一个页面都是fragment，原先 用的FragmentPagerAdapter, 数据发生变化后，调用notifydatasetchanged没用，fragment没有重建， 研究好久才发现应当使用FragmentStatePagerAdapter

- FragmentPagerAdapter更多的用于少量界面的ViewPager。划过的fragment会保存在内存中，尽管已经划过。而FragmentStatePagerAdapter和ListView有点类似，会保存当前界面，以及下一个界面和上一个界面（如果有），最多保存3个，其他会被销毁掉

- 如果fragment的数据源发生了变化，而需要重新构建fragment的时候，应当采用FragmentStatePagerAdapter, 这时候调用adapter的notifydatasetchanged才会有效果

# ViewPager的数据请求问题

- 有时ViewPager的每一个页面都有数据请求，正确做法应当是只有切换到了该页面，才会去请求数据，而不是在每一个页面创建的时候就请求数据了。

- 做法是为ViewPager设置OnPageChangeListener,只有选择了那个页面，才会请求数据，并且只请求一次

  ```
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
