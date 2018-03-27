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
