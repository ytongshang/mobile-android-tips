# API

- ViewGroup的触摸事件处理，很多继承于view,一方面它重载了dispatchTouchEvent,另外一个主要的区别在于新添加了函数onInterceptTouchEvent

# dispatchTouchEvent

- 如果ViewGroup的某个孩子没有接受ACTION_DOWN事件；那么，ACTION_MOVE和ACTION_UP等事件也一定不会分发给这个孩子

```java
  @Override
  public boolean dispatchTouchEvent(MotionEvent ev) {
    // mInputEventConsistencyVerifier是调试用的
    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onTouchEvent(ev, 1);
    }

    // If the event targets the accessibility focused view and this is it, start
    // normal event dispatch. Maybe a descendant is what will handle the click.
    if (ev.isTargetAccessibilityFocus() && isAccessibilityFocusedViewOrHost()) {
        ev.setTargetAccessibilityFocus(false);
    }

    // 第1步：根据遮挡问题，判断是否分发该触摸事件
    boolean handled = false;
    if (onFilterTouchEventForSecurity(ev)) {
        final int action = ev.getAction();
        final int actionMasked = action & MotionEvent.ACTION_MASK;

        // 第2步：检测是否需要清空目标和状态
        //
        // 如果是ACTION_DOWN，则清空之前的触摸事件处理目标和状态。
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
        // 如果是ACTION_DOWN,也就是一个事件序列的开始，当然要重新判断当前ViewGroup是否拦截了事件
        // 而如果mFirstTouchTarget为null的话，也就是说前面的down事件不是由子view去处理的，
        // 所以以后的up,move等事件也不会交由子view去处理,所以就相当于直接拦截了事件，直接返回了true
        final boolean intercepted;
        if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
            // 检查禁止拦截标记：FLAG_DISALLOW_INTERCEPT
            // 如果调用了requestDisallowInterceptTouchEvent()标记的话，则FLAG_DISALLOW_INTERCEPT会为true,不允许拦截
            // 例如，ViewPager在处理scroll事件的时候，就会调用requestDisallowInterceptTouchEvent()，
            // 禁止它的父类对触摸事件进行拦截
            final boolean disallowIntercept = (mGroupFlags & FLAG_DISALLOW_INTERCEPT) != 0;
            if (!disallowIntercept) {
                // 允许自身拦截的话，返回onInterceptTouchEvent()
                intercepted = onInterceptTouchEvent(ev);
                // restore action in case it was changed
                ev.setAction(action);
            } else {
                //不允许拦截的话，当然也就没有拦截
                intercepted = false;
            }    
        } else {
            //up, move事件，并且没有子view可以处理down,当然也没有子view处理up,move,直接相当于拦截掉了
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
        // 如果当前ViewGroup的孩子有接受触摸事件的话，则将该孩子添加到mFirstTouchTarget链表中。
        final boolean split = (mGroupFlags & FLAG_SPLIT_MOTION_EVENTS) != 0;
        // 首先清除了标识
        TouchTarget newTouchTarget = null;
        boolean alreadyDispatchedToNewTouchTarget = false;
        //不是cancel事件，也没有被拦截掉
        if (!canceled && !intercepted) {
            if (actionMasked == MotionEvent.ACTION_DOWN
                    || (split && actionMasked == MotionEvent.ACTION_POINTER_DOWN)
                    || actionMasked == MotionEvent.ACTION_HOVER_MOVE) {
                // 这是获取触摸事件的序号 以及 触摸事件的id信息。
                // 对于down事件，一般是0
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
                    //倒序遍历，一般都是希望最上面的反馈
                    for (int i = childrenCount - 1; i >= 0; i--) {
                        final int childIndex = customOrder ?
                                getChildDrawingOrder(childrenCount, i) : i;
                        final View child = children[childIndex];
                        // 如果child不能够接受触摸事件，又或者触摸坐标(x,y)在child的可视范围之外
                        // 就移到下一个child，继续循环查找
                        if (!canViewReceivePointerEvents(child)
                                || !isTransformedTouchPointInView(x, y, child, null)) {
                            continue;
                        }

                        // getTouchTarget()的作用是查找child是否存在于mFirstTouchTarget的单链表中。
                        // 是的话，则更新相应的值
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

- 当ViewGroup拦截了down事件，或者没有子view去处理down事件，后续的up,move事件就不会调用onInterceptTouchEvent()方法了，所以该方法并不是每次事件都会调用的

# 总结

- ViewGroup中的dispatchTouchEvent()会将触摸事件进行递归遍历传递。ViewGroup会遍历它的所有孩子，对每个孩子都递归的调用dispatchTouchEvent()来分发触摸事件。
- 如果ViewGroup的某个孩子没有接受(消费或者拦截)ACTION_DOWN事件；那么，ACTION_MOVE和ACTION_UP等事件也一定不会分发给这个孩子
