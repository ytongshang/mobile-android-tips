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

## 常用的Span

### Span的分类

- 修改字符文本格式时 使用 **CharacterStyle**
- 修改字符外观时 使用 **UpdateAppearance**
- 修改文字段落格式时 使用 **ParagraphStyle**
- 修改文字大小度量时 使用 **UpdateLayout**

### 删除线

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

### 同一个textview中设置字体大小不一样

- 使用AbsoluteSizeSpan

```java
private void initGiftList() {
  TextView[] gifts = new TextView[]{mTvgift01, mTvgift02, mTvgift03};
  TextView[] coins = new TextView[]{mTvGiftCoin01, mTvGiftCoin02, mTvGiftCoin03};
  int sp11 = (int) AppUtils.getRawSize(TypedValue.COMPLEX_UNIT_SP, 11, mContext);
  int sp10 = (int) AppUtils.getRawSize(TypedValue.COMPLEX_UNIT_SP, 10, mContext);

  for (int i = 0; i < coins.length; ++i) {
    Spanny wave = new Spanny();
    wave.append(String.valueOf(WAVES[i]))
        .append(" ")
        .append(mContext.getString(R.string.video_send_gift_wave));
    gifts[i].setText(wave);

    Spanny coin = new Spanny();
    coin.append(String.valueOf(WAVES[i] * WAVE_TO_COIN), new ForegroundColorSpan(mRed), new AbsoluteSizeSpan(sp11))
        .append(mContext.getString(R.string.video_send_gift_coin_unit), new ForegroundColorSpan(mGray), new AbsoluteSizeSpan(sp10));
    coins[i].setText(coin);
        }
    }
```

## TextView阴影效果

- 字体阴影需要四个相关参数：
  - android:shadowColor：阴影的颜色
  - android:shadowDx：水平方向上的偏移量
  - android:shadowDy：垂直方向上的偏移量
  - Android:shadowRadius：是阴影的的半径大小

- 例子

```xml
<TextView
  android:id="@+id/tv_fans_list"
  android:layout_width="wrap_content"
  android:layout_height="wrap_content"
  android:paddingEnd="@dimen/normal_horizonal_padding"
  android:paddingLeft="@dimen/normal_horizonal_padding"
  android:paddingRight="@dimen/normal_horizonal_padding"
  android:paddingStart="@dimen/normal_horizonal_padding"
  android:textColor="@color/white"
  android:shadowColor="@color/kas_black"
  android:shadowRadius="2"
  android:shadowDx="0"
  android:shadowDy="0"
  android:textSize="14sp" />
```