# TextView

## TextView 的跑马灯效果

- 示例

  ```xml
  <TextView
    android:id="@+id/tv_marque"
    android:layout_width="fill_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="40dp"
    android:singleLine="true"
    android:ellipsize="marquee"
    android:marqueeRepeatLimit="marquee_forever"
    android:focusableInTouchMode="true"
    android:focusable="true"
    android:textSize="24dp"
    android:text="一个很长的字符串..." />
  ```

- 注意点

  - android:singleLine="true" 是必须的。否则，一行显示不了的话；会多行显示
  - android:ellipsize="marquee" 是指定一行内容显示不下的情况下，使用跑马灯效果
  - android:marqueeRepeatLimit="marquee_forever" 在 android:ellipsize="marquee" 情况下使用，跑马灯无限循环。当然，这里的"marquee_forever"可以是整数，表示循环次数
  - android:focusableInTouchMode="true"和 android:focusable="true" 是为了让该TextView获取焦点
  - 必须获取焦点，如果布局中有自动获取焦点的比如EditText的话，不会显示这种效果
  - 因为焦点的问题，同一布局中只能有一个TextView有跑马灯的效果

## 复制粘贴

- 默认情况下，TextView是不能够选择的，如果要让其可以复制粘贴的话

  ```xml
  android:textIsSelectable="true"
  ```

## 文本的删除线

- 可以用Spannable实现

```java
private void addStrikeSpan() {
  SpannableString spanString = new SpannableString("删除线");
  StrikethroughSpan span = new StrikethroughSpan();
  spanString.setSpan(span, 0, 3, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
  mTextView.append(spanString);
}

private void addUnderLineSpan() {
  SpannableString spanString = new SpannableString("下划线");
  UnderlineSpan span = new UnderlineSpan();
  spanString.setSpan(span, 0, 3, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
  mTextView.append(spanString);
}
```

- 还可以用以下代码实现

```java
// 设置中划线并加清晰
textView.getPaint().setFlags(Paint.STRIKE_THRU_TEXT_FLAG | Paint.ANTI_ALIAS_FLAG);
textView.getPaint().setFlags(Paint.UNDERLINE_TEXT_FLAG);
//下划线
textView.getPaint().setFlags(0);
```
