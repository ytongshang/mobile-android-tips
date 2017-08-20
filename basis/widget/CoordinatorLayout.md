# CoordinatorLayout相关内容

## AppBarLayout

- 实际上是一个**Vertical的LinearLayout**, 它把容器类的所有组件全部作为AppBar

- 一般要配合CoordinatorLayout一起使用,AppBarLayout中**ActionBar只能使用ToolBar**

- AppBarLayout中的每一个子View要通过**setScrollFlags(int)**或者xml属性**app:layout_scrollFlags**指定scrolling behavior

- AppBarLayout还要与Coordinaotor中的一个可以滑动的View绑定起来,用来指定什么时候AppbarLayout中的View可以滑动，
 指定**AppBarLayout.ScrollingViewBehavior**，或者通过xml指定**app:layout_behavior="@string/appbar_scrolling_view_behavior"**

```xml
<android.support.design.widget.CoordinatorLayout
         xmlns:android="http://schemas.android.com/apk/res/android"
         xmlns:app="http://schemas.android.com/apk/res-auto"
         android:layout_width="match_parent"
         android:layout_height="match_parent">

     <android.support.v4.widget.NestedScrollView
             android:layout_width="match_parent"
             android:layout_height="match_parent"
             app:layout_behavior="@string/appbar_scrolling_view_behavior">

         <!-- Your scrolling content -->

     </android.support.v4.widget.NestedScrollView>

     <android.support.design.widget.AppBarLayout
             android:layout_height="wrap_content"
             android:layout_width="match_parent">

        <android.support.v7.widget.Toolbar
            android:id="@+id/toolbar"
            android:layout_width="match_parent"
            android:layout_height="?attr/actionBarSize"
            android:background="?attr/colorPrimary"
            app:popupTheme="@style/ThemeOverlay.AppCompat.Light"
            app:layout_scrollFlags="scroll|enterAlways"/>

         <android.support.design.widget.TabLayout
                 ...
                 app:layout_scrollFlags="scroll|enterAlways"/>

     </android.support.design.widget.AppBarLayout>

 </android.support.design.widget.CoordinatorLayout>
```

## CoordinatorLayout

## CollapsingToolbarLayout

## 特点

- 作为应用的顶层视图，是一个**super-powered 的frameLayout**
- 作为一个可以指定子views之间相互作用的容器，通过**给CoordinatorLayout的子View指定CoordinatorLayout.Behavior来提供子view之间不同的相互作用**，
 也就是说可以通过自定义CoordinatorLayout.Behavior来定义子views之间的相互作用

