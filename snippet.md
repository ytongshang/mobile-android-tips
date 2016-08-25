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
