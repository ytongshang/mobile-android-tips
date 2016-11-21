-   属性动画基本属性

    -   Duration：动画的持续时间；
    -   TimeInterpolation：定义动画变化速率的接口，所有插值器都必须实现此接口，如线性、非线性插值器；
    -   TypeEvaluator：用于定义属性值计算方式的接口，有int、float、color类型，根据属性的起始、结束值和插值一起计算出当前时间的属性值；
    -   Animation sets：动画集合，即可以同时对一个对象应用多个动画，这些动画可以同时播放也可以对不同动画设置不同的延迟；
    -   Frame refreash delay：多少时间刷新一次，即每隔多少时间计算一次属性值，默认为10ms，最终刷新时间还受系统进程调度与硬件的影响；
    -   Repeat Country and behavoir：重复次数与方式，如播放3次、5次、无限循环，可以让此动画一直重复，或播放完时向反向播放；

-   ValueAnimator属性

| column0              | column1                                                                                                                              |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| android:propertyName | String类型，必须要设置的节点属性，代表要执行动画的属性，辟如你可以指定了一个View的”alpha” ，必须通过调用loadAnimator()方法加载你的XML动画资源，然后调用setTarget()应用到具备这个属性的目标对象上（譬如TextView）。 |
| android:valueTo      | float、int或者color类型，必须要设置的节点属性，表明动画结束的点；如果是颜色的话，由6位十六进制的数字表示。                                                                         |
| android:duration     | 动画的时长，int类型，以毫秒为单位，默认为300毫秒。                                                                                                         |
| android:startOffset  | 动画延迟的时间，从调用start方法后开始计算，int型，毫秒为单位。                                                                                                  |
| android:repeatCount  | 一个动画的重复次数，int型，”-1“表示无限循环，”1“表示动画在第一次执行完成后重复执行一次，也就是两次，默认为0，不重复执行。                                                                   |
| android:repeatMode   | 重复模式：int型，当一个动画执行完的时候应该如何处理。该值必须是正数或者是-1，“reverse”会使得按照动画向相反的方向执行，可实现类似钟摆效果。“repeat”会使得动画每次都从头开始循环。                                  |
| android:valueType    | 关键参数，如果该value是一个颜色，那么就不需要指定，因为动画框架会自动的处理颜色值。有intType和floatType（默认）两种：分别说明动画值为int和float型。                                             |

-   xml animator使用方法

```java
AnimatorSet set = (AnimatorSet) AnimatorInflater.loadAnimator(myContext,R.animtor.property_animator);
set.setTarget(myObject);
set.start();                                                   
```

-   ObjectAnimator

    -   ObjectAnimator：继承自ValueAnimator，允许你指定要进行动画的对象以及该对象的一个属性
    -   ObjectAnimator的动画原理是不停的调用setXXX方法更新属性值，所有使用ObjectAnimator更新属性时的前提是Object必须声明有getXXX和setXXX方法

        ```java
            ObjectAnimator mObjectAnimator= ObjectAnimator.ofInt(view, "customerDefineAnyThingName", 0,  1).setDuration(2000);
            mObjectAnimator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener()
            {
                @Override
                public void onAnimationUpdate(ValueAnimator animation)
                {
                    //int value = animation.getAnimatedValue();  可以获取当前属性值
                    //view.postInvalidate();  可以主动刷新
                    //view.setXXX(value);
                    //view.setXXX(value);
                    //......可以批量修改属性
                }
            });
        ```


-   PropertyValuesHolder

    -   PropertyValuesHolder：多属性动画同时工作管理类。有时候我们需要同时修改多个属性，那就可以用到此类

        ```java
        PropertyValuesHolder a1 = PropertyValuesHolder.ofFloat("alpha", 0f, 1f);  
        PropertyValuesHolder a2 = PropertyValuesHolder.ofFloat("translationY", 0, viewWidth);  
        ObjectAnimator.ofPropertyValuesHolder(view, a1, a2).setDuration(1000).start();
        ```

-   ValueAnimator

    -   ValueAnimator只是动画计算管理驱动，设置了作用目标，但没有设置属性，需要通过updateListener里设置属性才会生效

        ```java
        ValueAnimator animator = ValueAnimator.ofFloat(0, mContentHeight);  //定义动画
        animator.setTarget(view);   //设置作用目标
        animator.setDuration(5000).start();
        animator.addUpdateListener(new AnimatorUpdateListener() {
            @Override
            public void onAnimationUpdate(ValueAnimator animation){
                float value = (float) animation.getAnimatedValue();
                view.setXXX(value);  //必须通过这里设置属性值才有效
                view.mXXX = value;  //不需要setXXX属性方法
            }

        });
        ```

-   AnimatorSet

    -   AnimationSet：动画集合，提供把多个动画组合成一个组合的机制，并可设置动画的时序关系，如同时播放、顺序播放或延迟播放

        ```java
        ObjectAnimator a1 = ObjectAnimator.ofFloat(view, "alpha", 1.0f, 0f);  
        ObjectAnimator a2 = ObjectAnimator.ofFloat(view, "translationY", 0f, viewWidth);  
        AnimatorSet animSet = new AnimatorSet();  
        animSet.setDuration(5000);  
        animSet.setInterpolator(new LinearInterpolator());  
        //animSet.playTogether(a1, a2, ...); //两个动画同时执行  
        animSet.play(a1).after(a2); //先后执行
        animSet.start(); 
        ```


-   ViewPropertyAnimator动画

    -   ViewPropertyAnimator提供了一种非常方便的方法为View的部分属性设置动画（切记，是部分属性），它可以直接使用一个Animator对象设置多个属性的动画；在多属性设置动画时，
        它比 上面的ObjectAnimator更加牛逼、高效，因为他会管理多个属性的invalidate方法统一调运触发，而不像上面分别调用，所以还会有一些性能优化。如下就是一个例子：

        ```java
        myView.animate().x(0f).y(100f).start();
        ```


-   LayoutAnimator容器布局动画

    -   Property动画系统还提供了对ViewGroup中View添加时的动画功能，我们可以用LayoutTransition对ViewGroup中的View进行动画设置显示。LayoutTransition的动画效果都是设置给ViewGroup，
            然后当被设置动画的ViewGroup中添加删除View时体现出来。该类用于当前布局容器中有View添加、删除、隐藏、显示等时候定义布局容器自身的动画和View的动画，
            也就是说当在一个LinerLayout中隐藏一个View的时候，我们可以自定义 整个由于LinerLayout隐藏View而改变的动画，同时还可以自定义被隐藏的View自己消失时候的动画等

    -   种类

        ```java
            LayoutTransition.APPEARING：当View出现或者添加的时候View出现的动画。
            LayoutTransition.CHANGE_APPEARING：当添加View导致布局容器改变的时候整个布局容器的动画。
            LayoutTransition.DISAPPEARING：当View消失或者隐藏的时候View消失的动画。
            LayoutTransition.CHANGE_DISAPPEARING：当删除或者隐藏View导致布局容器改变的时候整个布局容器的动画。
            LayoutTransition.CHANGE：当不是由于View出现或消失造成对其他View位置造成改变的时候整个布局容器的动画
        ```

    -   开启viewgroup动画

        ```xml
            android:animateLayoutChanges=”true”
        ```

    -   在使用LayoutTransition时，你可以自定义这几种事件类型的动画，也可以使用默认的动画，
            总之最终都是通过setLayoutTransition(LayoutTransition lt)方法把这些动画以一个LayoutTransition对象设置给一个ViewGroup。

        ```java
            mTransitioner = new LayoutTransition();
            ......
            ObjectAnimator anim = ObjectAnimator.ofFloat(this, "scaleX", 0, 1);
            ......//设置更多动画
            mTransition.setAnimator(LayoutTransition.APPEARING, anim);
            ......//设置更多类型的动画                
            mViewGroup.setLayoutTransition(mTransitioner);
        ```
