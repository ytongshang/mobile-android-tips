#### android:screenOrientation设定该活动的方向，该值可以是任何一个下面的字符串：

* "unspecified", 默认值. 由系统选择显示方向. 在不同的设备可能会有所不同..
* "landscape" 横向
* "portrait" 纵向
* "user" 用户当前的首选方向
* **"behind"** 与在活动堆栈下的活动相同方向
* "sensor" 根据物理方向传感器确定方向. 取决于用户手持的方向, 当用户转动设备, 它跟随改变
* "nosensor" 不经物理方向传感器确定方向. 该传感器被忽略, 所以当用户转动设备, 显示不会跟随改变. 除了这个区别，系统选择使用相同的政策取向对于“未指定”设置. 系统根据“未指定”("unspecified")设定选择相同显示方向.


#### 点击空白处，关闭软键盘
* 原理：重载activity, fragment, viewGroup的事件分发，如果MotionEvent的位置在EditText之中，则不用关闭，否则的话闭闭软键盘

```
@Override  
    public boolean dispatchTouchEvent(MotionEvent ev) {  
        if (ev.getAction() == MotionEvent.ACTION_DOWN) {  
            // 获得当前得到焦点的View，一般情况下就是EditText（特殊情况就是轨迹求或者实体案件会移动焦点）  
            View v = getCurrentFocus();  

            if (isShouldHideInput(v, ev)) {  
                hideSoftInput(v.getWindowToken());  
            }  
        }  
        return super.dispatchTouchEvent(ev);  
    }  

    private boolean isShouldHideInput(View v, MotionEvent event) {  
       if (v != null && (v instanceof EditText)) {  
           int[] l = { 0, 0 };  
           v.getLocationInWindow(l);  
           int left = l[0], top = l[1], bottom = top + v.getHeight(), right = left  
                   + v.getWidth();  
           if (event.getX() > left && event.getX() < right  
                   && event.getY() > top && event.getY() < bottom) {  
               // 点击EditText的事件，忽略它。  
               return false;  
           } else {  
               return true;  
           }  
       }  
       // 如果焦点不是EditText则忽略，这个发生在视图刚绘制完，第一个焦点不在EditView上，和用户用轨迹球选择其他的焦点  
       return false;  
   }  


```

#### RecyclerView的notifyDataSetChanged
* 很多时候当我们的数据源发生变时时，会直接调用notifyDataSetChanged,但是有的时个仅仅只是变动了数据中的一项，或者一部分，对于UI复杂，而且刷新频繁的情况，会导致页面卡顿
* 其实还有这些方法可以使用：

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
