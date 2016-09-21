# API

- **dispatchTouchEvent()和onTouchEvent()**: dispatchTouchEvent()是传递触摸事件的API， 而onTouchEvent()则是View处理触摸事件的API。View中dispatchTouchEvent()将事件传递给"自己的onTouch()", "自己的onTouchEvent()"进行处理。 onTouch()是OnTouchListener接口 中API，属于View提供的，让用户自己处理触摸事件的接口，而onTouchEvent()是Android系统提供的， 用于处理触摸事件的接口；在onTouchEvent()中会进行一系列的动作，例如获取焦点、设置按下状态， 调用onClick()等

- **OnTouchListener, OnClickListener, OnLongClickListener等接口**: 这部分主要是接口。onTouch()与onTouchEvent()都是用户处理触摸事件的API。但不同的是：**(01)**, onTouch()是View提供给用户，让用户自己处理触摸事件的接口。而onTouchEvent()是Android系统自己实现的接口。**(02)**，onTouch()的优先级比onTouchEvent()的优先级更高。dispatchTouchEvent()中分发事件的时候，会先将事件分配给onTouch()进行处理，然后才分配给onTouchEvent()进行处理。 如果onTouch()对触摸事件进行了处理，并且返回true；那么，该触摸事件就不会分配在分配给onTouchEvent()进行处理了。只有当onTouch()没有处理，或者处理了但返回false时，才会分配给onTouchEvent()进行处理

# dispatchTouchEvent

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
            //noinspection SimplifiableIfStatement
            ListenerInfo li = mListenerInfo;
            if (li != null && li.mOnTouchListener != null
                    && (mViewFlags & ENABLED_MASK) == ENABLED
                    && li.mOnTouchListener.onTouch(this, event)) {
                result = true;
            }

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

- 如果将事件进行分发的话，会先尝试分发给onTouch()；然后才分发给onTouchEvent()

# onFilterTouchEventForSecurity()

- onFilterTouchEventForSecurity()返回true，表示可以分发该触摸事件；否则，不能分发该触摸事件。不能分发事件的情况，只有mViewFlags&FILTER_TOUCHES_WHEN_OBSCURED!=0，并且event.getFlags()&MotionEvent.FLAG_WINDOW_IS_OBSCURED!=0同时成立。
- FILTER_TOUCHES_WHEN_OBSCURED是android:filterTouchesWhenObscured属性所对应的位。android:filterTouchesWhenObscured是true的话，则表示其他视图在该视图之上，导致该视图被隐藏时，该视图就不再响应触摸事件。
- MotionEvent.FLAG_WINDOW_IS_OBSCURED为true的话，则表示该视图的窗口是被隐藏的。

# onTouchEvent

```java
public boolean onTouchEvent(MotionEvent event) {
        final float x = event.getX();
        final float y = event.getY();
        final int viewFlags = mViewFlags;

        if ((viewFlags & ENABLED_MASK) == DISABLED) {
            if (event.getAction() == MotionEvent.ACTION_UP && (mPrivateFlags & PFLAG_PRESSED) != 0) {
                setPressed(false);
            }
            // A disabled view that is clickable still consumes the touch
            // events, it just doesn't respond to them.
            return (((viewFlags & CLICKABLE) == CLICKABLE ||
                    (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE));
        }

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
                        // take focus if we don't have it already and we should in
                        // touch mode.
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

                        if (!mHasPerformedLongPress) {
                            // This is a tap, so remove the longpress check
                            removeLongPressCallback();

                            // Only perform take click actions if we were in the pressed state
                            if (!focusTaken) {
                                // Use a Runnable and post this rather than calling
                                // performClick directly. This lets other visual state
                                // of the view update before click actions start.
                                if (mPerformClick == null) {
                                    mPerformClick = new PerformClick();
                                }
                                if (!post(mPerformClick)) {
                                    performClick();
                                }
                            }
                        }

                        if (mUnsetPressedState == null) {
                            mUnsetPressedState = new UnsetPressedState();
                        }

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

                    // Walk up the hierarchy to determine if we're inside a scrolling container.
                    boolean isInScrollingContainer = isInScrollingContainer();

                    // For views inside a scrolling container, delay the pressed feedback for
                    // a short period in case this is a scroll.
                    if (isInScrollingContainer) {
                        mPrivateFlags |= PFLAG_PREPRESSED;
                        if (mPendingCheckForTap == null) {
                            mPendingCheckForTap = new CheckForTap();
                        }
                        mPendingCheckForTap.x = event.getX();
                        mPendingCheckForTap.y = event.getY();
                        postDelayed(mPendingCheckForTap, ViewConfiguration.getTapTimeout());
                    } else {
                        // Not inside a scrolling container, so show the feedback right away
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

                    // Be lenient about moving outside of buttons
                    if (!pointInView(x, y, mTouchSlop)) {
                        // Outside button
                        removeTapCallback();
                        if ((mPrivateFlags & PFLAG_PRESSED) != 0) {
                            // Remove any future long press/tap checks
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

- 如果View被禁用的话，则返回它是否可以点击。当我们调用了setEnabled(false)时，View就被禁用了；默认情况下，View是可用的。当调用setClickable(true)或者android:clickable为true时，View就是可点击状态；默认情况下，View是不可点击的。
- 如果该View的mTouchDelegate不为null的话，将触摸消息分发给mTouchDelegate。例如，假设有两个视图v1和v2，它们的布局相互之间不重叠；如果设置了v1.setTouchDelegate(v2)的话，v1的触摸事件就会分发给v2。 注意：mTouchDelegate的默认值是null。
- 如果View可以被点击的话，则执行if里面的内容。例如，setPressed()是设置View的按下状态，如果用户有设置View在不同状态的图片时，setPressed()时会导致View的图片的更新

# 总结

- View中的dispatchTouchEvent()会将事件传递给"自己的onTouch()", "自己的onTouchEvent()"进行处理。而且onTouch()的优先级比onTouchEvent()的优先级要高。

- onTouch()与onTouchEvent()都是View中用户处理触摸事件的API。onTouch是OnTouchListener接口中的函数，OnTouchListener接口需要用户自己实现。onTouchEvent()是View自带的接口，Android系统提供了默认的实现；当然，用户可以重载该API。

- onTouch()与onTouchEvent()有两个不同之处：**(01)** onTouch()是View提供给用户，让用户自己处理触摸事件的接口。而onTouchEvent()是Android系统自己实现的接口。**(02)** onTouch()的优先级比onTouchEvent()的优先级更高。dispatchTouchEvent()中分发事件的时候，会先将事件分配给onTouch()进行处理，然后才分配给onTouchEvent()进行处理。 如果onTouch()对触摸事件进行了处理，并且返回true；那么，该触摸事件就不会分配在分配给onTouchEvent()进行处理了。只有当onTouch()没有处理，或者处理了但返回false时，才会分配给onTouchEvent()进行处理。

- onTouch能够得到执行需要两个前提条件，第一mOnTouchListener的值不能为空，第二当前点击的控件必须是enable的。因此如果你有一个控件是非enable的，那么给它注册onTouch事件将永远得不到执行。对于这一类控件，如果我们想要监听它的touch事件，就必须通过在该控件中重写onTouchEvent方法来实现
