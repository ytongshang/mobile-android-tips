#### TextView 的跑马灯效果

* 示例
```
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

* 注意点
  1. android:singleLine="true" 是必须的。否则，一行显示不了的话；会多行显示
  2. android:ellipsize="marquee" 是指定一行内容显示不下的情况下，使用跑马灯效果
  3. android:marqueeRepeatLimit="marquee_forever" 在 android:ellipsize="marquee" 情况下使用，跑马灯无限循环。当然，这里的"marquee_forever"可以是整数，表示循环次数
  4. android:focusableInTouchMode="true"和 android:focusable="true" 是为了让该TextView获取焦点
  5. 必须获取焦点，如果布局中有自动获取焦点的比如EditText的话，不会显示这种效果
  6. 因为焦点的问题，同一布局中只能有一个TextView有跑马灯的效果
  
