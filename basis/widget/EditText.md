# EditText

- [EditText的焦点问题](#edittext的焦点问题)
- [EditText的listener](#edittext的listener)
- [点击空白处，关闭软键盘](#点击空白处关闭软键盘)
- [EditText删除最后一个字符](#edittext删除最后一个字符)
- [动态设置EditText的字数限制](#动态设置edittext的字数限制)

## EditText的焦点问题

- **问题描述：** 有时个一个界面有editext的时候，我们希望它**不自动获得焦点**,但是editext调用clearFocus方法都没有用

- **解决办法：** 在EditText的父级控件中找一个，设置成

```xml
android:focusable="true"
android:focusableInTouchMode="true"
```

- 有的时候，当EditText获得焦点与否，UI不同，这时个可以重载焦点的监听函数

```java
mSearchInput.setOnFocusChangeListener(new View.OnFocusChangeListener() {
           @Override
           public void onFocusChange(View v, boolean hasFocus) {
               if (hasFocus) {
                   mSearchLeft.setVisibility(View.VISIBLE);
                   mSearchCenter.setVisibility(View.GONE);
                   mSearchCancel.setVisibility(View.VISIBLE);
               } else {
                   mSearchLeft.setVisibility(View.GONE);
                   mSearchCenter.setVisibility(View.VISIBLE);
                   mSearchCancel.setVisibility(View.GONE);
               }
           }
       });
```

## EditText的listener

- EditText的listener主要用到的有2个:

  ```java
  addTextWatcher()
  setOnEditorActionListener()
  ```

- 一旦有搜索之类的行为，要定义imeOptions,并且重载它的actionListener, 并且很多listener之类 的代码都要注意返回是true,还是false，一般情况下返回true,表示处理了该事件，该事件不会再一次分发， 否则的话会再次分发

```java
android:imeOptions="actionSearch"

mSearchInput.setOnEditorActionListener(new TextView.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
                if (actionId == EditorInfo.IME_ACTION_SEARCH || actionId == EditorInfo.IME_ACTION_UNSPECIFIED) {
                    String text = mSearchInput.getText().toString().trim();
                    if (KasUtil.isEmpty(text)) {
                        T.showShort(mContext, R.string.search_empty_hint);
                        return true;
                    }
                    Message msg = mHandler.obtainMessage(MSG_SEARCH);
                    msg.obj = text;
                    mHandler.sendMessage(msg);
                    return true;
                }
                return false;
            }
        });
```

## 点击空白处，关闭软键盘

- **问题描述：** 点击空白处，关闭软键盘
- **解决原理：** 重载activity, viewGroup的事件分发，如果MotionEvent的位置在EditText之中，则不用关闭， 否则的话闭闭软键盘

```java
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

## EditText删除最后一个字符

- 有时候，比如表情栏要点一个图标，删除最后一个表情

  ```java
  public static void backspace(EditText editText) {
    KeyEvent event = new KeyEvent(0, 0, 0, KeyEvent.KEYCODE_DEL, 0, 0, 0,
            0, KeyEvent.KEYCODE_ENDCALL);
    editText.dispatchKeyEvent(event);
  }
  ```

## 动态设置EditText的字数限制

- 有时候，我们需要动态设置EditText的最大字数限制，代码如下：

  ```java
  InputFilter[] filters = {new InputFilter.LengthFilter(NAME_MAX_LENGTH)};
  mEtGroupName.setFilters(filters);
  ```
