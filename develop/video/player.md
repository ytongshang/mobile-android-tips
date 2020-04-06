# Player

## 相关文章

-   [ffplay Documentation](https://www.ffmpeg.org/ffplay-all.html)

## 缓存设计

### 读数据->解封装->帧缓冲区

-   抗网络抖动
-   解码抖动
-   避免丢帧导致的花屏
-   没有帧缓冲区，那么 io 网络抖动，或者解码抖动时，整个被卡住，另外网络抖动时，服务器缓存了太多的帧，网络恢复时，tcp 队列爆满，被动丢帧，数据不完整解码花屏

### 帧缓冲区->解码->显示缓冲区

-   音视频同步
-   抵抗渲染抖动
-   没有显示缓冲区，解码完的数据直接进入泻染模块，无法音画同步
-   如果渲染模块出现抖动，会导致无法异步去解码帧缓冲区中的数据，降低了效率

### 显示缓冲区->音画同步->渲染/播放

### 缓冲区大小的设置

-   缓冲区越大 -> 抗抖动能力越强
-   缓冲区越大 -> 内存占用越高
-   缓冲区越大 -> 播放延时越大
-   帧缓冲区，一般默认无限大，当达到一定的阀值，主动丢帧，或者倍数播放的方式
-   显示缓冲区，一般比较小

## 音视频同步

-   判断视频与音频帧的时间戳差值 pts，是不是在一定的 “阈值” 范围内，如果是，则可以渲染/播放，否则就 “等” 到合适的时间
-   pts 一定要注意是生产出来的时间，而不是后面比如经过美颜处理，编码后的时间戳

### RFC-1359

-   无法察觉：音频和视频的时间戳差值在：-100ms ~ +25ms 之间
-   能够察觉：音频滞后了 100ms 以上，或者超前了 25ms 以上
-   无法接受：音频滞后了 185ms 以上，或者超前了 90ms 以上

### 同步算法

-   音频帧持续送入扬声器以既定的速率播放，每播放一帧音频数据，则把该音频帧的时间戳更新到 Master Clock，作为主时钟，视频帧则参考 Master Clock 来决定自己是否渲染、何时渲染或者丢弃，算法如下
-   假设 min 为音画同步阈值（如：25ms），则当前视频时间戳如果与 master clock 的绝对差值在 25ms 阈值范围内则都可以送入渲染
-   如果 diff > 0，即 pts > m-clock，则代表视频帧提前准备好了。这种情况下，是可以通过 sleep 来等待主时钟的，但是为了防止异常时间戳导致 sleep 时间过长，可以设置一个 max 异常阈值（如：1000ms），如果 diff 超过这个 max 可以认为是异常帧，丢弃掉
-   如果 diff < 0，即 pts < m-clock，则代表视频帧滞后了。这种情况下，如果滞后超出约定阈值（如：25ms）的视频帧就应该被丢弃

## 常见问题

### seek 不准确

-   seek 的位置的视频帧， 不一定为 I 帧，因而需要移动到附近的 I 帧，所以不准确

## 一些 ijkPlayer 的参数设置

### skip_loop_filter

-   loop_filter 是指环路滤波, 主要是用于画面去块
-   skip_loop_filter 是指对指定帧不做环路滤波, 可以节省 CPU

| value              | des                                                |
| ------------------ | -------------------------------------------------- |
| AVDISCARD_ALL      | discard all                                        |
| AVDISCARD_BIDIR    | discard all bidirectional frames                   |
| AVDISCARD_DEFAULT  | discard useless packets like 0 size packets in avi |
| AVDISCARD_NONE     | discard nothing                                    |
| AVDISCARD_NONINTRA | discard all non intra frames                       |
| AVDISCARD_NONKEY   | discard all frames except keyframes                |
| AVDISCARD_NONREF   | discard all non reference                          |

### framedrop

-   framedrop 是在视频帧处理不过来的时候丢弃一些帧达到同步的效果
