# Scroll

## scrollTo 与scrollBy

- 任何一个控件都是可以滚动的，因为在View类当中有scrollTo()和scrollBy()这两个方法

- 两个scroll方法中传入的参数，第一个参数x表示相对于当前位置横向移动的距离，正值向左移动，负值向右移动， 单位是像素。第二个参数y表示相对于当前位置纵向移动的距离，正值向上移动，负值向下移动，单位是像素

- scrollTo()方法是让View相对于初始的位置滚动某段距离，由于View的初始位置是不变的，因此不管我们点击多少次scrollTo按钮滚动到的都将是同一个位置。而scrollBy()方法则是让View相对于当前的位置滚动某段距离，那每当我们点击一次scrollBy按钮，View的当前位置都进行了变动，因此不停点击会一直向右下方移动

## Scroller

- View调用ScrollTo/ScrollBy方法进行滑动时，其过程是瞬时完成的
- 如果要实现滑动的过渡效果，可以使用Scroller结合View的computeScroll配合完成

```java

Scroller scroller = new Scroller()

```