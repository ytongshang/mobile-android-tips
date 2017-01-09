# AdapterView

## ListView

- 有时候 listView如果要分组显示的话，可以使用ExpandableListView

- listview的addHeaderView,在api 19之前只能在setAdapter之前调用，如果先设置了adapter,后面 再增加header,就会崩溃，解决方法一种方法如下.不过最好还是使用自己写的RecyclerView和 ExtendedRecyclerView

  ```java
  mListView.setAdapter(null);
  mListView.addHeaderView(mListHeader);
  mListView.setAdapter(mAdapter);
  ```

## RecyclerView的notifyDataSetChanged

- 很多时候当我们的数据源发生变时时，会直接调用notifyDataSetChanged,但是有的时个仅仅只是变动了数据中的一项，或者一部分，对于UI复杂，而且刷新频繁的情况，会导致页面卡顿其实还有这些方法可以使用：

  ```java
  public final void notifyDataSetChanged()
  public final void notifyItemChanged(int position)
  public final void notifyItemRangeChanged(int positionStart, int itemCount)
  public final void notifyItemInserted(int position)
  public final void notifyItemMoved(int fromPosition, int toPosition)
  public final void public final void notifyItemRangeInserted(int positionStart, int itemCount)
  public final void notifyItemRemoved(int position)
  public final void notifyItemRangeRemoved(int positionStart, int itemCount)
  ```

## 类似微信表情栏长按显示表情详情

- **问题描述：** 最近做一个项目，GridView表情栏中，长按一个表情要显示一个有表情gif的popupWindow,在长按状态下，左右移动，当在不同的的位置时，popupWindow显示对应位置的gif表情，popupWindow的位置也要随之变化，当长按结束时，关闭显示的popupWindow

- **关键问题：** 长按显示popupWindow很好做，问题主要在两个方面，一方面怎么监听长按结束，另一方面在长按状态下，移动手指如何显示对应位置的内容

- **解决思路：**

  - 长按显示直接监听其OnItemLongClickListener,使用popupWindow作为弹窗，popupWindow的位置使用showAtLocation指定
  - 长按结束的监听，开始想到的是GestureDetector.OnGestureListener,可惜长按结束的时候，GestureDetector.OnGestureListener的 **boolean onSingleTapUp(MotionEvent e)** 是不会执行的，最后最简单的的方法其实是重写其OnTouchListener,如果是ACTION_UP事件，则关闭popupWindow
  - 滑动的时候，在不同位置展示，不同的内容，这个主要的问题是获得当前的位置与哪一个GridView的item相关联，只要解决的这个应好办了，最后发现GridView有一个方法叫作 **public int pointToPosition(int x, int y)** ,看到这个方法的源码就知道怎么做了

- **代码**

  ```java
    @Override
    public void onViewCreated(View view, Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        final GridView gridView = (GridView) view.findViewById(R.id.emoji_gridView);
        Bundle bundle = getArguments();
        if (bundle != null) {
            gridView.setNumColumns(EmojiManager.COLUM_COUNT);
            mKey = bundle.getInt(BUNDLE_KEY);
        }
        mEmojiList = EmojiManager.instance().getEmojiList(mKey);
        if (mEmojiList != null && mEmojiList.size() > 0) {
            gridView.setAdapter(new EmojiAdapter(getActivity(), mEmojiList));
        }

        gridView.setOnItemClickListener(new OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                if (mOnEmojiconClickedListener != null) {
                    Emojicon icon = (Emojicon) parent.getItemAtPosition(position);
                    if (icon != null && !icon.mEmojiStr.equals(EmojiManager.SPACE)) {
                        mOnEmojiconClickedListener.onEmojiconClicked(icon);
                    }
                }
            }
        });

        gridView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
            @Override
            public boolean onItemLongClick(AdapterView<?> parent, View view, int position, long id) {
                showPopWindow(view, position);
                mIsLongClick = true;
                BusProvider.postMainBus(new MessageEvent(MessageEvent.IM_DISALLOW_VIEWPAGER_SCROLL, true));
                return true;
            }
        });

        gridView.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_UP) {
                    mIsLongClick = false;
                    hidePopWindow();
                    BusProvider.postMainBus(new MessageEvent(MessageEvent.IM_DISALLOW_VIEWPAGER_SCROLL, false));
                } else if (event.getAction() == MotionEvent.ACTION_MOVE) {
                    if (!mIsLongClick) {
                        return false;
                    }
                    View anchor = null;
                    int x = (int) event.getX();
                    int y = (int) event.getY();
                    //使用类变量,而不是每次都新建一个,可以减少变量的创建
                    if (mFrame == null) {
                        mFrame = new Rect();
                    }
                    for (int i = 0; i < gridView.getChildCount(); ++i) {
                        final View child = gridView.getChildAt(i);
                        if (child.getVisibility() == View.VISIBLE) {
                            child.getHitRect(mFrame);
                            if (mFrame.contains(x, y)) {
                                anchor = child;
                                break;
                            }
                        }
                    }
                    int position = gridView.pointToPosition(x, y);
                    if (anchor != null && position != GridView.INVALID_POSITION) {
                        showPopWindow(anchor, position);
                    }
                }
                return false;
            }
        });
    }

    private void initPopup() {
        if (mPopWindow != null) {
            return;
        }

        mPopWidth = (int) KasUtil.getRawSize(TypedValue.COMPLEX_UNIT_DIP, 73, mContext);
        mPopHeight = (int) KasUtil.getRawSize(TypedValue.COMPLEX_UNIT_DIP, 80, mContext);

        Point point = KasUtil.getScreenSize(mContext);
        mWinWidth = point.x;

        View v = LayoutInflater.from(mContext).inflate(R.layout.im_popwindow_emoji, null);
        mEmojiGif = (ImageView) v.findViewById(R.id.iv_emoji);
        mEmojiDesc = (TextView) v.findViewById(R.id.tv_emoji_desc);
        mPopWindow = new PopupWindow(v, mPopWidth, mPopHeight);
        mPopWindow.setBackgroundDrawable(ContextCompat.getDrawable(mContext,
                R.drawable.im_popow_emoji_background));
        mPopWindow.setTouchable(true);
        mPopWindow.setOutsideTouchable(true);
    }

    private void showPopWindow(View anchor, int position) {
        if (anchor == null || position < 0 || position >= mEmojiList.size()) {
            return;
        }
        Emojicon item = mEmojiList.get(position);

        //有一部分是空白的。。。。
        if (item.mDrawableId == 0) {
            return;
        }

        //初始化popou
        initPopup();

        //anchor
        int[] loc = new int[2];
        anchor.getLocationOnScreen(loc);
        int anchorX = loc[0];
        int anchorY = loc[1];

        //因为gridview是stretchMode="columnWidth",所以在大屏幕上有可能一个item的大小在大于popupwindow
        int x;
        if (mPopWidth >= anchor.getWidth()) {
            x = anchorX - (mPopWidth - anchor.getWidth()) / 2;
        } else {
            x = anchorX + (anchor.getWidth() - mPopWidth) / 2;
        }

        //因为popWindow如果跑到屏幕以外,会被剪切掉,所以做限定
        //加上一个边距,不要贴边显示
        if (x <= 0) {
            x = (int) KasUtil.getRawSize(TypedValue.COMPLEX_UNIT_DIP, 8, mContext);
        }
        if (x >= mWinWidth - mPopWidth) {
            x = mWinWidth - mPopWidth - (int) KasUtil.getRawSize(TypedValue.COMPLEX_UNIT_DIP, 8, mContext);
        }

        //不要被肥硕的大拇指挡住挡住。。。。。
        int y = anchorY - mPopHeight -
                (int) KasUtil.getRawSize(TypedValue.COMPLEX_UNIT_DIP, 30, mContext);

        if (mEmojiGif != null) {
            GifDrawable gif = GifDrawable.createFromResource(mContext.getResources(), item.mDrawableId);
            if (gif != null) {
                mEmojiGif.setImageDrawable(gif);
            }
        }

        if (mEmojiDesc != null) {
            if (!KasUtil.isEmpty(item.mDesc)) {
                mEmojiDesc.setVisibility(View.VISIBLE);
                mEmojiDesc.setText(item.mDesc);
            } else {
                mEmojiDesc.setVisibility(View.GONE);
            }
        }
        if (!mPopWindow.isShowing()) {
            mPopWindow.showAtLocation(anchor, Gravity.NO_GRAVITY, x, y);
        } else {
            //使用-1,忽略大小变化
            mPopWindow.update(x, y, -1, -1);
        }
    }

    private void hidePopWindow() {
        if (mPopWindow != null) {
            mPopWindow.dismiss();
            mPopWindow = null;
            mEmojiGif = null;
            mEmojiDesc = null;
        }
    }
  ```
