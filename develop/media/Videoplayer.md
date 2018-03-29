# Videoplayer

## Window属性

### PixelFormat

```java
 // 设置window的属性和surfaceview的一致，
 // 避免首次进入时由于属性不一导致windowmanger销毁当前窗口重建而产生的闪屏
getWindow().setFormat(PixelFormat.TRANSPARENT);
```

## 屏幕亮度

- 获得屏幕亮度，**注意这个获得值是0~255**

```java
// The screen backlight brightness between 0 and 255.
private float getScreenBrightness() {
    int value = 0;
    ContentResolver cr = getContentResolver();
    try {
        value = Settings.System.getInt(cr, Settings.System.SCREEN_BRIGHTNESS);
    } catch (Settings.SettingNotFoundException e) {
        e.printStackTrace();
    }
    return value;
}
```

- 设置屏幕亮度，通过Window的属性设置的，**注意这个值是用0.0f 〜 1.0f**

```java
mWindowLp = getWindow().getAttributes();
// 值的范围是0.0f ~ 1.0f
mWindowLp.screenBrightness = mCurBrightness;
mWindow.setAttributes(mWindowLp);
```

## 音量

### 音量大小

```java
 mAudioManager = (AudioManager) this.getSystemService(Service.AUDIO_SERVICE);

 // 获得AudioManager.STREAM_MUSIC的大小
 mVolumeProgress = mAudioManager.getStreamVolume(AudioManager.STREAM_MUSIC);

 // 获得AudioManager.STREAM_MUSIC最大的音量
 mAudioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC);

 // 获得AudioManager.STREAM_MUSIC最小的音量
 mAudioManager.getStreamMinVolume(AudioManager.STREAM_MUSIC);

 // 设置音量的大小
 mAudioManager.setStreamVolume(AudioManager.STREAM_MUSIC, mVolumeProgress, 0);
```

### AudioFocus

- [Android中关于AudioFocus你所该知道的知识](https://blog.csdn.net/weixin_37077539/article/details/61202750)

- **requestAudioFocus应当与abandonAudioFocus成对出现**

```java
// 申请获得焦点
mAudioManager.requestAudioFocus(null, AudioManager.STREAM_MUSIC, AudioManager.AUDIOFOCUS_GAIN);
// 释放焦点
mAudioManager.abandonAudioFocus(null);
```

## IjkPlayer

- [视频直播技术（四）：使用Ijkplayer播放直播视频](http://www.cnblogs.com/renhui/p/6420140.html)

### 颜色格式

```java
m_MediaPlayer = new IjkMediaPlayer();

// 设置颜色格式
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "overlay-format", IjkMediaPlayer.SDL_FCC_RV32);
```

### 硬解码

- 是否开启硬解码

```java
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "mediacodec", mbHardwear ? 1 : 0);
```

- 如何判断是否支持硬解码

```java

```

### start on prepared

- 状态由prepared后自动start

```java
// 关闭prepared后自动start
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "start-on-prepared", 0);
```

### framedrop

- 对rtmp视频流进行播放，会出现严重的视频音频不同步现象，并且随着播放的时间越长，视频与音频的差距越大。具体原因是CPU在处理视频帧的时候处理得太慢，默认的音视频同步方案是视频同步到音频, 导致了音频播放过快，视频跟不上。
- framedrop 控制着允许丢帧的范围。可以通过修改 framedrop 的数值来解决不同步的问题，framedrop 是在视频帧处理不过来的时候丢弃一些帧达到同步的效果
- framedrop 的具体大小根据实际情况而定, 一般丢太多帧也不好，会影响用户的观看体验

```java
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "framedrop", 1);
```

### 视频延迟

```java

// 关闭播放器缓冲 (如果频繁卡顿，可以保留缓冲区)
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "packet-buffering", 0);

// 设置最大的缓冲区的大小
// 绝地求生等高分辨率OBS直播出现频繁卡顿，从去掉max-buffer-size设置
// 控制max_buffer_size，合理设置max_buffer_size，使得拉流端不会缓存太长时间的内容
// 经过测试，发现不是很实用，因为内容延时只有追赶或者丢弃当前播放的内容，快速跳播到最新数据才能达到低延时播放
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "max-buffer-size", 200 * 1024);

// 分析码流的时间, 单位为微秒，和首屏有关
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_FORMAT, "analyzeduration", 1000L);

// 加了这个nobuffer后启动黑屏会增加，先去掉
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_FORMAT, "fflags", "nobuffer");

//播放前的探测Size，默认是1M, 改小一点会出画面更快
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "probsize", 200 * 1024);
```

### 其它设置

```java
m_MediaPlayer.setOption(IjkMediaPlayer.OPT_CATEGORY_PLAYER, "min-frames", 20);
```
