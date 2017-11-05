# 参考文档

- [Android View 事件分发机制源码详解(ViewGroup篇)](http://blog.csdn.net/a553181867/article/details/51287844)

## API

- ViewGroup的触摸事件处理，很多继承于view,一方面它重载了dispatchTouchEvent,另外一个主要的区别在于新添加了函数onInterceptTouchEvent

## dispatchTouchEvent

- 如果ViewGroup的某个孩子没有接受ACTION_DOWN事件；那么，ACTION_MOVE和ACTION_UP等事件也一定不会分发给这个孩子

```java
  @Override
  public boolean dispatchTouchEvent(MotionEvent ev) {
    // 测试用的代码
    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onTouchEvent(ev, 1);
    }

    // If the event targets the accessibility focused view and this is it, start
    // normal event dispatch. Maybe a descendant is what will handle the click.
    if (ev.isTargetAccessibilityFocus() && isAccessibilityFocusedViewOrHost()) {
        ev.setTargetAccessibilityFocus(false);
    }

    boolean handled = false;
    // 第1步：根据遮挡情况，判断是否需要分发该触摸事件
    if (onFilterTouchEventForSecurity(ev)) {
        final int action = ev.getAction();
        final int actionMasked = action & MotionEvent.ACTION_MASK;

        // 第2步：检测是否需要清空目标和状态
        //
        // 如果是ACTION_DOWN，说明是一个新的触摸事件序列，则清空之前的触摸事件处理target和状态。
        // 这里的情况状态包括：
        // (01) 清空mFirstTouchTarget链表，并设置mFirstTouchTarget为null。
        //      mFirstTouchTarget是"接受触摸事件的子View"所组成的单向链表
        // (02) 将当前view的flags设置为~FLAG_DISALLOW_INTERCEPT，只要是一个新的触摸事件序列，那么就是允许拦截的
        // 但实际上是否会拦截，要看onInterceptTouchEvent(ev)
        // (03) 清空mPrivateFlags的PFLAG_CANCEL_NEXT_UP_EVEN标记
        if (actionMasked == MotionEvent.ACTION_DOWN) {
            cancelAndClearTouchTargets(ev);
            resetTouchState();
        }

        // 第3步：检查当前ViewGroup是否想要拦截触摸事件
        //
        // (01)如果是ACTION_DOWN,也就是一个事件序列的开始，当然要重新判断当前ViewGroup是否拦截了事件
        // (02) 如果mFirstTouchTarget不为空，意味着ACTION_DOWN是由自身的某个子View处理,后续的的比如ACTION_MOVE,ACTION_UP事件
        // 则要再一次进行判断是否拦截掉
        final boolean intercepted;
        if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
            // 检查禁止拦截标记：FLAG_DISALLOW_INTERCEPT
            // (01)如果调用了requestDisallowInterceptTouchEvent()标记的话，则FLAG_DISALLOW_INTERCEPT会为true,不允许拦截
            // 例如，ViewPager在处理scroll事件的时候，就会调用getParent().requestDisallowInterceptTouchEvent()，禁止它的父类对触摸事件进行拦截
            // (02) 如果是ACTION_DOWN事件，该标识位肯定是~FLAG_DISALLOW_INTERCEPT，表示是允许拦截的，要根据onInterceptTouchEvent进行判断
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
            // 如果不是ACTION_DOWN事件，并且mFirstTouchTarget为null的话，也就是说前面的ACTION_DOWN事件不是由子view去处理的，
            // 因为如果ACTION_DOWN不是由子View处理的，那么其它的也不会由子View处理，应当由本ViewGroup处理，也就相当于拦截了事件
            intercepted = true;
        }

        // 第4步：检查当前的触摸事件是否被取消
        // (01) 对于ACTION_DOWN而言，mPrivateFlags的PFLAG_CANCEL_NEXT_UP_EVENT位肯定是0；因此，canceled=false。
        // (02) 当前的View或ViewGroup要被从父View中detach时，PFLAG_CANCEL_NEXT_UP_EVENT就会被设为true；
        //      此时，它就不再接受触摸事情。
        final boolean canceled = resetCancelNextUpFlag(this)|| actionMasked == MotionEvent.ACTION_CANCEL;

        final boolean split = (mGroupFlags & FLAG_SPLIT_MOTION_EVENTS) != 0;
        TouchTarget newTouchTarget = null;
        boolean alreadyDispatchedToNewTouchTarget = false;

        // 第5步：将触摸事件分发给"当前ViewGroup的子View和子ViewGroup"
        //
        // 如果触摸"没有被取消"，同时也"没有被拦截"的话，则将触摸事件分发给它的子View和子ViewGroup。
        // 整一个if(!canceled && !intercepted){ … }代码块所做的工作就是对ACTION_DOWN事件的特殊处理。
        // 因为ACTION_DOWN事件是一个事件序列的开始，所以我们要先找到能够处理这个事件序列的一个子View，
        // 如果一个子View能够消耗事件，那么mFirstTouchTarget会指向子View，
        // 如果所有的子View都不能消耗事件，那么mFirstTouchTarget将为null
        if (!canceled && !intercepted) {
            //MotionEvent.ACTION_HOVER_MOVE一般指鼠标事件，鼠标在view上面
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
                        // 就继续循环查找可以分发事件的子View
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

                        // 将事件尝试分发给子View,如果找到了一个可以处理触摸事件的子View，就直接跳出循环，不用继续遍历
                        if (dispatchTransformedTouchEvent(ev, false, child, idBitsToAssign)) {
                            mLastTouchDownTime = ev.getDownTime();
                            mLastTouchDownIndex = childIndex;
                            mLastTouchDownX = ev.getX();
                            mLastTouchDownY = ev.getY();
                            // 如果child能够接受该触摸事件，即child消费或者拦截了该触摸事件的话；
                            // 则调用addTouchTarget()将child添加到mFirstTouchTarget链表的表头，并返回表头对应的TouchTarget
                            // 同时还设置alreadyDispatchedToNewTouchTarget为true。
                            newTouchTarget = addTouchTarget(child, idBitsToAssign);
                            alreadyDispatchedToNewTouchTarget = true;
                            break;
                        }
                    }
                }

                // 如果newTouchTarget为null，并且mFirstTouchTarget不为null；
                // 则设置newTouchTarget为mFirstTouchTarget链表中最后一个不为空的节点，也就是最后添加人结点
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

        // 第6步：进一步的对触摸事件进行分发,实际上是对拦截的了，取消了的，或其它非ACTION_DOWN事件的处理
        //

        if (mFirstTouchTarget == null) {
            // 如果mFirstTouchTarget为null，意味着还没有任何View来接受该触摸事件；
            // 此时，将当前ViewGroup看作一个View；
            // 将会调用"当前的ViewGroup的父类View的dispatchTouchEvent()"对触摸事件进行分发处理。
            // 注意：这里的第3个参数是null，也就是直接将事件交由这个ViewGroup处理
            // 即，会将触摸事件交给当前ViewGroup的onTouch(), onTouchEvent()进行处理。
            handled = dispatchTransformedTouchEvent(ev, canceled, null,
                    TouchTarget.ALL_POINTER_IDS);
            // 如果mFirstTouchTarget不为null，说明ACTION_DOWN事件已经有子View处理了，
            // 那么对于其它类型的事件，直接尝试分发给mFirstTouchTarget链表中的就可以了
            TouchTarget predecessor = null;
            TouchTarget target = mFirstTouchTarget;
            while (target != null) {
                final TouchTarget next = target.next;
                // 这里实际上区分开了ACTION_DOWN与其它类型的事件
                if (alreadyDispatchedToNewTouchTarget && target == newTouchTarget) {
                    handled = true;
                } else {
                    final boolean cancelChild = resetCancelNextUpFlag(target.child)
                            || intercepted;
                    // 如果正在detchView 或都viewGroup拦截了事件,则发送cancel事件给子View
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

    // 调试用
    if (!handled && mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(ev, 1);
    }
    return handled;
}
```

## onInterceptTouchEvent

- onInterceptTouchEvent是否拦截触摸事件，默认情况下是不拦截的
- 常见的例子就是ViewPager,当发生滑动事件的时候，ViewPager拦截了事件，用来左右滑动item

  ```java
  public boolean onInterceptTouchEvent(MotionEvent ev) {
    return false;
  }
  ```

- 当ViewGroup拦截了down事件，或者没有子view去处理down事件，后续的up,move事件就不会调用 onInterceptTouchEvent()方法了，所以该方法并不是每次事件都会调用的


## requestDisallowInterceptTouchEvent

- 如果FLAG_DISALLOW_INTERCEPT设置后，ViewGroup将无法拦截除了ACTION_DOWN以外的其它点击事件
- 在ACTION_DOWN事件中，会重置这个标识位
- 对于ACTION_DOWN事件，ViewGroup总会调用自己的onInterceptTouchEvent询问自己是否要拦截事件
- **子View调用requestDisallowInterceptTouchEvent并不能影响ViewGroup对ACTION_DOWN的处理**

## 图解

![viewgroup事件分发](./../../image-resources/touchevent/viewgroup.png)

## 总结

- ViewGroup默认不拦截任何事件，所以事件能正常分发到子View处（如果子View符合条件的话）
- 如果ViewGroup的onInterceptTouchEvent为true,并且允许拦截事件（allowInterceptTouchEvent），那么事件直接由ViewGroup处理
- 如果没有合适的子View或者子View不消耗ACTION_DOWN事件，那么接着事件会交由ViewGroup处理，并且同一事件序列之后的事件不会再分发给子View了。
- 如果ViewGroup的onTouchEvent也返回false，即ViewGroup也不消耗事件的话，那么最后事件会交由Activity处理。即：逐层分发事件下去，如果都没有处理事件的View，那么事件会逐层向上返回。
- 如果某一个View拦截了事件，那么同一个事件序列的其他所有事件都会交由这个View处理，此时不再调用View(ViewGroup)的onIntercept()方法去询问是否要拦截了
