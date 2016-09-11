# ListView

- 有时候 listView如果要分组显示的话，可以使用ExpandableListView

- listview的addHeaderView,在api 19之前只能在setAdapter之前调用，如果先设置了adapter,后面
再增加header,就会崩溃，解决方法一种方法如下.不过最好还是使用自己写的RecyclerView和
ExtendedRecyclerView
```
mListView.setAdapter(null);
mListView.addHeaderView(mListHeader);
mListView.setAdapter(mAdapter);
```

# RecyclerView的notifyDataSetChanged

- 很多时候当我们的数据源发生变时时，会直接调用notifyDataSetChanged,但是有的时个仅仅只是变动了数据中的一项，或者一部分，对于UI复杂，而且刷新频繁的情况，会导致页面卡顿其实还有这些方法可以使用：
```
public final void notifyDataSetChanged()
public final void notifyItemChanged(int position)
public final void notifyItemRangeChanged(int positionStart, int itemCount)
public final void notifyItemInserted(int position)
public final void notifyItemMoved(int fromPosition, int toPosition)
public final void public final void notifyItemRangeInserted(int positionStart, int itemCount)
public final void notifyItemRemoved(int position)
public final void notifyItemRangeRemoved(int positionStart, int itemCount)
```
