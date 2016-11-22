# API

- **dispatchTouchEvent()和onTouchEvent()**: dispatchTouchEvent()是传递触摸事件的API， 而onTouchEvent()则是View处理触摸事件的API。View中dispatchTouchEvent()将事件传递给"自己的onTouch()", "自己的onTouchEvent()"进行处理。 onTouch()是OnTouchListener接口 中API，属于View提供的，让用户自己处理触摸事件的接口，而onTouchEvent()是Android系统提供的， 用于处理触摸事件的接口；在onTouchEvent()中会进行一系列的动作，例如获取焦点、设置按下状态， 调用onClick()等

- **OnTouchListener, OnClickListener, OnLongClickListener等接口**: 这部分主要是接口。onTouch()与onTouchEvent()都是用户处理触摸事件的API。但不同的是：**(01)**, onTouch()是View提供给用户，让用户自己处理触摸事件的接口。而onTouchEvent()是Android系统自己实现的接口。**(02)**，onTouch()的优先级比onTouchEvent()的优先级更高。dispatchTouchEvent()中分发事件的时候，会先将事件分配给onTouch()进行处理，然后才分配给onTouchEvent()进行处理。 如果onTouch()对触摸事件进行了处理，并且返回true；那么，该触摸事件就不会分配在分配给onTouchEvent()进行处理了。只有当onTouch()没有处理，或者处理了但返回false时，才会分配给onTouchEvent()进行处理

## dispatchTouchEvent

### 源码

```java
    public boolean dispatchTouchEvent(MotionEvent event) {
        // If the event should be handled by accessibility focus first.
        if (event.isTargetAccessibilityFocus()) {
            // We don't have focus or no virtual descendant has it, do not handle the event.
            if (!isAccessibilityFocusedViewOrHost()) {
                return false;
            }
            // We have focus and got the event, then use normal event dispatch.
            event.setTargetAccessibilityFocus(false);
        }

        boolean result = false;

        if (mInputEventConsistencyVerifier != null) {
            mInputEventConsistencyVerifier.onTouchEvent(event, 0);
        }

        final int actionMasked = event.getActionMasked();
        if (actionMasked == MotionEvent.ACTION_DOWN) {
            // Defensive cleanup for new gesture
            stopNestedScroll();
        }

        if (onFilterTouchEventForSecurity(event)) {
            //必须ENABLED，才会去执行设置的OnTouchListener
            ListenerInfo li = mListenerInfo;
            if (li != null && li.mOnTouchListener != null
                    && (mViewFlags & ENABLED_MASK) == ENABLED
                    && li.mOnTouchListener.onTouch(this, event)) {
                result = true;
            }

            //分发顺序，先onTouch，如果返回false,才会onTouchEvent
            if (!result && onTouchEvent(event)) {
                result = true;
            }
        }

        if (!result && mInputEventConsistencyVerifier != null) {
            mInputEventConsistencyVerifier.onUnhandledEvent(event, 0);
        }

        // Clean up after nested scrolls if this is the end of a gesture;
        // also cancel it if we tried an ACTION_DOWN but we didn't want the rest
        // of the gesture.
        if (actionMasked == MotionEvent.ACTION_UP ||
                actionMasked == MotionEvent.ACTION_CANCEL ||
                (actionMasked == MotionEvent.ACTION_DOWN && !result)) {
            stopNestedScroll();
        }

        return result;
    }
```

- 如果将事件进行分发的话，会先尝试分发给onTouch()；然后才分发给onTouchEvent()
- 如果View是DISABLED的，即使设置了onTouch也不会执行

### onFilterTouchEventForSecurity

- onFilterTouchEventForSecurity()表示是否要分发该触摸事件；如果该View不是位于顶部，并且有设置属性使该View不在顶部时不响应触摸事件，则不分发该触摸事件，即不会执行onTouch()与onTouchEvent()。 否则的话，则将事件分发给onTouch(), onTouchEvent()进行处理。

```java
public boolean onFilterTouchEventForSecurity(MotionEvent event) {
    //noinspection RedundantIfStatement
    if ((mViewFlags & FILTER_TOUCHES_WHEN_OBSCURED) != 0
            && (event.getFlags() & MotionEvent.FLAG_WINDOW_IS_OBSCURED) != 0) {
        // Window is obscured, drop this touch.
        return false;
    }
    return true;
}
```

- FILTER_TOUCHES_WHEN_OBSCURED是android:filterTouchesWhenObscured属性所对应的位。android:filterTouchesWhenObscured是true的话，则表示其他视图在该视图之上，导致该视图被隐藏时，该视图就不再响应触摸事件。
- MotionEvent.FLAG_WINDOW_IS_OBSCURED为true的话，则表示该视图的窗口是被隐藏的。

## onTouchEvent

```java
public boolean onTouchEvent(MotionEvent event) {
        final float x = event.getX();
        final float y = event.getY();
        final int viewFlags = mViewFlags;

        if ((viewFlags & ENABLED_MASK) == DISABLED) {
            if (event.getAction() == MotionEvent.ACTION_UP && (mPrivateFlags & PFLAG_PRESSED) != 0) {
                setPressed(false);
            }
            // 一个DISABLED的，但是是CLICKABLE或LONG_CLICKABLE的，也会消费掉事件
            return (((viewFlags & CLICKABLE) == CLICKABLE ||
                    (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE));
        }

        //代理
        if (mTouchDelegate != null) {
            if (mTouchDelegate.onTouchEvent(event)) {
                return true;
            }
        }

        if (((viewFlags & CLICKABLE) == CLICKABLE ||
                (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE)) {
            switch (event.getAction()) {
                case MotionEvent.ACTION_UP:
                    boolean prepressed = (mPrivateFlags & PFLAG_PREPRESSED) != 0;
                    if ((mPrivateFlags & PFLAG_PRESSED) != 0 || prepressed) {
                        //如果有PFLAG_PRESSED，或者PFLAG_PREPRESSED,尝试获取焦点
                        boolean focusTaken = false;
                        if (isFocusable() && isFocusableInTouchMode() && !isFocused()) {
                            focusTaken = requestFocus();
                        }

                        if (prepressed) {
                            // The button is being released before we actually
                            // showed it as pressed.  Make it show the pressed
                            // state now (before scheduling the click) to ensure
                            // the user sees it.
                            setPressed(true, x, y);
                       }

                        // 不是长按事件
                        //可能是时长不够，也可能时长够了，没有设置OnLongClickListener,或者OnLongClickListener返回为false
                        //所以如果要想只处理长按，不处理click,OnLongClickListener应当返回为true
                        if (!mHasPerformedLongPress) {

                            removeLongPressCallback();

                            // 如是获取焦点失败，才会有可能执行OnClickListener
                            // 可以参考Edittext
                            if (!focusTaken) {
                                //这里有可能按下的效果还没有显示出来，
                                //所以将执行OnClickListener的动作交由Handler去处理，实际上放到了后面去处理
                                if (mPerformClick == null) {
                                    mPerformClick = new PerformClick();
                                }
                                //!!!!!放到MessagQueue中去
                                if (!post(mPerformClick)) {
                                    performClick();
                                }
                            }
                        }

                        if (mUnsetPressedState == null) {
                            mUnsetPressedState = new UnsetPressedState();
                        }

                        //!!!!用postDelayed,回复原来
                        if (prepressed) {
                            postDelayed(mUnsetPressedState,
                                    ViewConfiguration.getPressedStateDuration());
                        } else if (!post(mUnsetPressedState)) {
                            // If the post failed, unpress right now
                            mUnsetPressedState.run();
                        }

                        removeTapCallback();
                    }
                    break;

                case MotionEvent.ACTION_DOWN:
                    mHasPerformedLongPress = false;

                    if (performButtonActionOnTouchDown(event)) {
                        break;
                    }

                    // 判断是否在一个可以滑动的容器内部
                    boolean isInScrollingContainer = isInScrollingContainer();

                    //如果在一个滑动的容器的内部，因为即将有可能是一个滑动事件，所以要过一段时间去判断这是否是一个点击事件
                    //也就是过一段时间去设置按下状态，设置PFLAG_PREPRESSED标识
                    if (isInScrollingContainer) {
                        mPrivateFlags |= PFLAG_PREPRESSED;
                        if (mPendingCheckForTap == null) {
                            mPendingCheckForTap = new CheckForTap();
                        }
                        mPendingCheckForTap.x = event.getX();
                        mPendingCheckForTap.y = event.getY();
                        //!!!!精髓的用postDelayed
                        postDelayed(mPendingCheckForTap, ViewConfiguration.getTapTimeout());
                    } else {
                        // 如果不是在一个滑动容器内部，则直接设置按下状态和PFLAG_PREPRESSED标志
                        //设置检验长按的Runnable
                        setPressed(true, x, y);
                        checkForLongClick(0);
                    }
                    break;

                case MotionEvent.ACTION_CANCEL:
                    setPressed(false);
                    removeTapCallback();
                    removeLongPressCallback();
                    break;

                case MotionEvent.ACTION_MOVE:
                    drawableHotspotChanged(x, y);

                    // 如是移出了View的范围外
                    if (!pointInView(x, y, mTouchSlop)) {
                        //不用继续检测是否是按下动作
                        removeTapCallback();
                        if ((mPrivateFlags & PFLAG_PRESSED) != 0) {
                            //如果已经是按下了，则不用继续检测是否是长按
                            removeLongPressCallback();

                            setPressed(false);
                        }
                    }
                    break;
            }

            return true;
        }

        return false;
    }
```

- 一个View如果是DISABLED的，则返回它是否可以点击。如果View是DISABLED的,但是它是CLICKABLE/LONG_CLICKABLE，它不会对事件有反应，但是它会消费掉触摸事件。
- 当我们调用了setEnabled(false)时，View就被禁用了；默认情况下，View是可用的。当调用setClickable(true)或者android:clickable为true时，View就是可点击状态；默认情况下，一个View如是是不可点击的，也不能够长按

  ```java
  public void setClickable(boolean clickable) {
        setFlags(clickable ? CLICKABLE : 0, CLICKABLE);
    }

  public void setLongClickable(boolean longClickable) {
        setFlags(longClickable ? LONG_CLICKABLE : 0, LONG_CLICKABLE);
    }
  ```

- 如果该View的mTouchDelegate不为null的话，将触摸消息分发给mTouchDelegate。例如，假设有两个视图v1和v2，它们的布局相互之间不重叠；如果设置了v1.setTouchDelegate(v2)的话，v1的触摸事件就会分发给v2。

- 对于ACTION_DOWN事件，要根据容器是否可以滑动区分处理

- 对于ACTION_MOVE事件，如果触摸点跑到了View的范围外，则要清除掉点击的标识，清除掉相应的视觉效果，当然也不用继续去测试是否是长按

- 对于ACTION_UP事件，如果已经有PFLAG_PRESSED或PFLAG_PREPRESSED的标志，则尝试获取焦点，如果获取失败并且这次点击时长不足以当作一次长按事件（或者是长按事件，但是OnLongClickListener返回为false），才会去执行OnClickListener

- 在这里最精髓的是使用Handler去判断是否是点击，是否是长按，去执行onClick,去执行onLongClick

## 总结

- View中的dispatchTouchEvent()会将事件传递给"onTouch()", "onTouchEvent()"进行处理。而且onTouch()的优先级比onTouchEvent()的优先级要高。

- onTouch()与onTouchEvent()有两个不同之处：

  - 如果View是DISABLED的，即使设置了onTouch也不会执行，而onTouchEvent则会返回是否可以点击/是否可以长按。因此如果你有一个控件是DISABLED的，那么给它注册onTouch事件将永远得不到执行，对于这一类控件，如果我们想要监听它的touch事件，就必须通过在该控件中重写onTouchEvent方法来实现
  - onTouch()的优先级比onTouchEvent()的优先级更高。如果onTouch()对触摸事件进行了处理，并且返回true；那么，该触摸事件就不会分配在分配给onTouchEvent()进行处理了。只有当onTouch()没有处理，或者处理了但返回false时，才会分配给onTouchEvent()进行处理。
