# PopupWindow

- PopupWindow这个类用来实现一个弹出框，可以使用任意布局的View作为其内容，这个弹出框是悬浮在当前activity之上的

- 如果没有给PopupWindow设置背景的话，无论是点击外部区域还是Back键都无法dismiss掉的

```
popupWindow.setBackgroundDrawable(getResources().getDrawable(R.drawable.selectmenu_bg_downward));
```

- showAtLocation方法中，其中的x,y是相对于整个屏幕的，可以参看android.view.WindowManager.LayoutParams

```
public void showAtLocation(View parent, int gravity, int x, int y)
public void showAtLocation(IBinder token, int gravity, int x, int y)
```

- showAsDropDown,这里相于对另一个view显示

```
public void showAsDropDown(View anchor)
public void showAsDropDown(View anchor, int xoff, int yoff) 相对于anchor的左下角，并且偏移xoff, yoff
public void showAsDropDown(View anchor, int xoff, int yoff, int gravity)
```

- popupWindow如果在屏幕上显示不下，是被会剪裁的，所以有的时候，要特别注意其显示坐标的位置

```
```

- 如果popupWindow有背景，则会在contentView外面包一层PopupViewContainer之后作为mPopupView，如果没有背景，则直接用contentView作为mPopupView。而这个PopupViewContainer是一个内部私有类，它继承了FrameLayout，在其中重写了Key和Touch事件的分发处理.由于PopupView本身并没有重写Key和Touch事件的处理，所以如果没有包这个外层容器类，点击Back键或者外部区域是不会导致弹框消失的

```
  @Override
  public boolean dispatchKeyEvent(KeyEvent event) {
       if (event.getKeyCode() == KeyEvent.KEYCODE_BACK) {
           if (getKeyDispatcherState() == null) {
               return super.dispatchKeyEvent(event);
           }

           if (event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0) {
               final KeyEvent.DispatcherState state = getKeyDispatcherState();
               if (state != null) {
                   state.startTracking(event, this);
               }
               return true;
           } else if (event.getAction() == KeyEvent.ACTION_UP) {
               final KeyEvent.DispatcherState state = getKeyDispatcherState();
               if (state != null && state.isTracking(event) && !event.isCanceled()) {
                   dismiss();
                   return true;
               }
           }
           return super.dispatchKeyEvent(event);
       } else {
           return super.dispatchKeyEvent(event);
       }
   }

   @Override
   public boolean dispatchTouchEvent(MotionEvent ev) {
       if (mTouchInterceptor != null && mTouchInterceptor.onTouch(this, ev)) {
           return true;
       }
       return super.dispatchTouchEvent(ev);
   }

   @Override
   public boolean onTouchEvent(MotionEvent event) {
       final int x = (int) event.getX();
       final int y = (int) event.getY();

       if ((event.getAction() == MotionEvent.ACTION_DOWN)
               && ((x < 0) || (x >= getWidth()) || (y < 0) || (y >= getHeight()))) {
           dismiss();
           return true;
       } else if (event.getAction() == MotionEvent.ACTION_OUTSIDE) {
           dismiss();
           return true;
       } else {
           return super.onTouchEvent(event);
       }
   }

```

- 设置了PopupWindow的background,点击Back键或者点击弹窗的外部区域,弹窗就会dismiss.相反,如果不设置PopupWindow的background,那么点击back键和点击弹窗的外部区域,弹窗是不会消失的. 那么,如果我想要一个效果,点击外部区域,弹窗不消失,但是点击事件会向下面的activity传递,比如下面是一个WebView,我想点击里面的链接等.具体的 方法是设置 WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL，这个Flag的设置与否是由一个叫mNotTouchModal的字段控制，但是设置该字段的set方法被标记为@hide，可以通过反射调用

```
    /**
     * Set whether this window is touch modal or if outside touches will be sent
     * to
     * other windows behind it.
     *
     */
    public static void setPopupWindowTouchModal(PopupWindow popupWindow,
            boolean touchModal) {
        if (null == popupWindow) {
            return;
        }
        Method method;
        try {

            method = PopupWindow.class.getDeclaredMethod("setTouchModal",
                    boolean.class);
            method.setAccessible(true);
            method.invoke(popupWindow, touchModal);

        }
        catch (Exception e) {
            e.printStackTrace();
        }

    }
```
