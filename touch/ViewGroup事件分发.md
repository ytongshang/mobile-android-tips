# API

- ViewGroup的触摸事件处理，很多继承于view,一方面它重载了dispatchTouchEvent,另外一个主要的区别在于新添加了函数onInterceptTouchEvent

# dispatchTouchEvent

- 如果ViewGroup的某个孩子没有接受ACTION_DOWN事件；那么，ACTION_MOVE和ACTION_UP等事件也一定不会分发给这个孩子

```java
  @Override
  public boolean dispatchTouchEvent(MotionEvent ev) {
    // mInputEventConsistencyVerifier是调试用的，不会理会
    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onTouchEvent(ev, 1);
    }

    // 第1步：是否要分发该触摸事件
    //
    // onFilterTouchEventForSecurity()表示是否要分发该触摸事件。
    // 如果该View不是位于顶部，并且有设置属性使该View不在顶部时不响应触摸事件，则不分发该触摸事件，即返回false。
    // 否则，则对触摸事件进行分发，即返回true。
    boolean handled = false;
    if (onFilterTouchEventForSecurity(ev)) {
        final int action = ev.getAction();
        final int actionMasked = action & MotionEvent.ACTION_MASK;

        // 第2步：检测是否需要清空目标和状态
        //
        // 如果是ACTION_DOWN(即按下事件)，则清空之前的触摸事件处理目标和状态。
        // 这里的情况状态包括：
        // (01) 清空mFirstTouchTarget链表，并设置mFirstTouchTarget为null。
        //      mFirstTouchTarget是"接受触摸事件的View"所组成的单链表
        // (02) 清空mGroupFlags的FLAG_DISALLOW_INTERCEPT标记
        //      如果设置了FLAG_DISALLOW_INTERCEPT，则不允许ViewGroup对触摸事件进行拦截。
        // (03) 清空mPrivateFlags的PFLAG_CANCEL_NEXT_UP_EVEN标记
        if (actionMasked == MotionEvent.ACTION_DOWN) {
            cancelAndClearTouchTargets(ev);
            resetTouchState();
        }    

        // 第3步：检查当前ViewGroup是否想要拦截触摸事件
        //
        // 是的话，设置intercepted为true；否则intercepted为false。
        // 如果是"按下事件(ACTION_DOWN)" 或者 mFirstTouchTarget不为null；就执行if代码块里面的内容。
        // 否则的话，设置intercepted为true。
        final boolean intercepted;
        if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
            // 检查禁止拦截标记：FLAG_DISALLOW_INTERCEPT
            // 如果调用了requestDisallowInterceptTouchEvent()标记的话，则FLAG_DISALLOW_INTERCEPT会为true。
            // 例如，ViewPager在处理触摸事件的时候，就会调用requestDisallowInterceptTouchEvent()
            //     ，禁止它的父类对触摸事件进行拦截
            final boolean disallowIntercept = (mGroupFlags & FLAG_DISALLOW_INTERCEPT) != 0;
            if (!disallowIntercept) {
                // 如果禁止拦截标记为false的话，则调用onInterceptTouchEvent()；并返回拦截状态。
                intercepted = onInterceptTouchEvent(ev);
                ev.setAction(action); // restore action in case it was changed
            } else {
                intercepted = false;
            }    
        } else {
            intercepted = true;
        }    

        // 第4步：检查当前的触摸事件是否被取消
        //
        // (01) 对于ACTION_DOWN而言，mPrivateFlags的PFLAG_CANCEL_NEXT_UP_EVENT位肯定是0；因此，canceled=false。
        // (02) 当前的View或ViewGroup要被从父View中detach时，PFLAG_CANCEL_NEXT_UP_EVENT就会被设为true；
        //      此时，它就不再接受触摸事情。
        final boolean canceled = resetCancelNextUpFlag(this)
                || actionMasked == MotionEvent.ACTION_CANCEL;

        // 第5步：将触摸事件分发给"当前ViewGroup的子View和子ViewGroup"
        //
        // 如果触摸"没有被取消"，同时也"没有被拦截"的话，则将触摸事件分发给它的子View和子ViewGroup。  
        //     如果当前ViewGroup的孩子有接受触摸事件的话，则将该孩子添加到mFirstTouchTarget链表中。
        final boolean split = (mGroupFlags & FLAG_SPLIT_MOTION_EVENTS) != 0;
        TouchTarget newTouchTarget = null;
        boolean alreadyDispatchedToNewTouchTarget = false;
        if (!canceled && !intercepted) {
            if (actionMasked == MotionEvent.ACTION_DOWN
                    || (split && actionMasked == MotionEvent.ACTION_POINTER_DOWN)
                    || actionMasked == MotionEvent.ACTION_HOVER_MOVE) {
                // 这是获取触摸事件的序号 以及 触摸事件的id信息。
                // (01) 对于ACTION_DOWN，actionIndex肯定是0
                // (02) 而getPointerId()是获取的该触摸事件的id，并将该id信息保存到idBitsToAssign中。
                //    这个触摸事件的id是为多指触摸而添加的；对于单指触摸，getActionIndex()返回的肯定是0；
                //    而对于多指触摸，第一个手指的id是0，第二个手指的id是1，第三个手指的id是2，...依次类推。
                final int actionIndex = ev.getActionIndex();
                final int idBitsToAssign = split ? 1 << ev.getPointerId(actionIndex)
                        : TouchTarget.ALL_POINTER_IDS;

                // 清空这个手指之前的TouchTarget链表。
                // 一个TouchTarget，相当于一个可以被触摸的对象；它中记录了接受触摸事件的View
                removePointersFromTouchTargets(idBitsToAssign);

                // 获取该ViewGroup包含的View和ViewGroup的数目，
                // 然后递归遍历ViewGroup的孩子，对触摸事件进行分发。
                // 递归遍历ViewGroup的孩子：是指对于当前ViewGroup的所有孩子，都会逐个遍历，并分发触摸事件；
                //   对于逐个遍历到的每一个孩子，若该孩子是ViewGroup类型的话，则会递归到调用该孩子的孩子，...
                final int childrenCount = mChildrenCount;
                if (newTouchTarget == null && childrenCount != 0) {
                    final float x = ev.getX(actionIndex);
                    final float y = ev.getY(actionIndex);
                    final View[] children = mChildren;

                    final boolean customOrder = isChildrenDrawingOrderEnabled();
                    for (int i = childrenCount - 1; i >= 0; i--) {
                        final int childIndex = customOrder ?
                                getChildDrawingOrder(childrenCount, i) : i;
                        final View child = children[childIndex];
                        // 如果child可以接受触摸事件，
                        // 并且触摸坐标(x,y)在child的可视范围之内的话；
                        // 则继续往下执行。否则，调用continue。
                        // child可接受触摸事件：是指child的是可见的(VISIBLE)；或者虽然不可见，但是位于动画状态。
                        if (!canViewReceivePointerEvents(child)
                                || !isTransformedTouchPointInView(x, y, child, null)) {
                            continue;
                        }

                        // getTouchTarget()的作用是查找child是否存在于mFirstTouchTarget的单链表中。
                        // 是的话，返回对应的TouchTarget对象；否则，返回null。
                        newTouchTarget = getTouchTarget(child);
                        if (newTouchTarget != null) {
                            newTouchTarget.pointerIdBits |= idBitsToAssign;
                            break;
                        }

                        // 重置child的mPrivateFlags变量中的PFLAG_CANCEL_NEXT_UP_EVENT位。
                        resetCancelNextUpFlag(child);

                        // 调用dispatchTransformedTouchEvent()将触摸事件分发给child。
                        if (dispatchTransformedTouchEvent(ev, false, child, idBitsToAssign)) {
                            // 如果child能够接受该触摸事件，即child消费或者拦截了该触摸事件的话；
                            // 则调用addTouchTarget()将child添加到mFirstTouchTarget链表的表头，并返回表头对应的TouchTarget
                            // 同时还设置alreadyDispatchedToNewTouchTarget为true。
                            mLastTouchDownTime = ev.getDownTime();
                            mLastTouchDownIndex = childIndex;
                            mLastTouchDownX = ev.getX();
                            mLastTouchDownY = ev.getY();
                            newTouchTarget = addTouchTarget(child, idBitsToAssign);
                            alreadyDispatchedToNewTouchTarget = true;
                            break;
                        }
                    }
                }

                // 如果newTouchTarget为null，并且mFirstTouchTarget不为null；
                // 则设置newTouchTarget为mFirstTouchTarget链表中第一个不为空的节点。
                if (newTouchTarget == null && mFirstTouchTarget != null) {
                    // Did not find a child to receive the event.
                    // Assign the pointer to the least recently added target.
                    newTouchTarget = mFirstTouchTarget;
                    while (newTouchTarget.next != null) {
                        newTouchTarget = newTouchTarget.next;
                    }
                    newTouchTarget.pointerIdBits |= idBitsToAssign;
                }
            }
        }

        // 第6步：进一步的对触摸事件进行分发
        //
        // (01) 如果mFirstTouchTarget为null，意味着还没有任何View来接受该触摸事件；
        //   此时，将当前ViewGroup看作一个View；
        //   将会调用"当前的ViewGroup的父类View的dispatchTouchEvent()"对触摸事件进行分发处理。
        //   即，会将触摸事件交给当前ViewGroup的onTouch(), onTouchEvent()进行处理。
        // (02) 如果mFirstTouchTarget不为null，意味着有ViewGroup的子View或子ViewGroup中，
        //   有可以接受触摸事件的。那么，就将触摸事件分发给这些可以接受触摸事件的子View或子ViewGroup。
        if (mFirstTouchTarget == null) {
            // 注意：这里的第3个参数是null
            handled = dispatchTransformedTouchEvent(ev, canceled, null,
                    TouchTarget.ALL_POINTER_IDS);
        } else {
            // Dispatch to touch targets, excluding the new touch target if we already
            // dispatched to it.  Cancel touch targets if necessary.
            TouchTarget predecessor = null;
            TouchTarget target = mFirstTouchTarget;
            while (target != null) {
                final TouchTarget next = target.next;
                if (alreadyDispatchedToNewTouchTarget && target == newTouchTarget) {
                    handled = true;
                } else {
                    final boolean cancelChild = resetCancelNextUpFlag(target.child)
                            || intercepted;
                    if (dispatchTransformedTouchEvent(ev, cancelChild,
                            target.child, target.pointerIdBits)) {
                        handled = true;
                    }
                    if (cancelChild) {
                        if (predecessor == null) {
                            mFirstTouchTarget = next;
                        } else {
                            predecessor.next = next;
                        }
                        target.recycle();
                        target = next;
                        continue;
                    }
                }
                predecessor = target;
                target = next;
            }
        }

        // 第7步：再次检查取消标记，并进行相应的处理
        //
        // Update list of touch targets for pointer up or cancel, if needed.
        if (canceled
                || actionMasked == MotionEvent.ACTION_UP
                || actionMasked == MotionEvent.ACTION_HOVER_MOVE) {
            resetTouchState();
        } else if (split && actionMasked == MotionEvent.ACTION_POINTER_UP) {
            final int actionIndex = ev.getActionIndex();
            final int idBitsToRemove = 1 << ev.getPointerId(actionIndex);
            removePointersFromTouchTargets(idBitsToRemove);
        }
    }

    // mInputEventConsistencyVerifier是调试用的，不会理会
    if (!handled && mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(ev, 1);
    }
    return handled;
}
```

# onInterceptTouchEvent

- onInterceptTouchEvent是否拦截触摸事件，默认情况下是不拦截的
- 常见的例子就是ViewPager,当发生滑动事件的时候，ViewPager拦截了事件，用来左右滑动item

  ```java
  public boolean onInterceptTouchEvent(MotionEvent ev) {
    return false;
  }
  ```

# 总结

- ViewGroup中的dispatchTouchEvent()会将触摸事件进行递归遍历传递。ViewGroup会遍历它的所有孩子，对每个孩子都递归的调用dispatchTouchEvent()来分发触摸事件。
- 如果ViewGroup的某个孩子没有接受(消费或者拦截)ACTION_DOWN事件；那么，ACTION_MOVE和ACTION_UP等事件也一定不会分发给这个孩子
