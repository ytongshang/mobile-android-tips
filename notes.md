# tips

- [android:screenOrientation](#androidscreenorientation)
- [Fragment的显示与否监听](#fragment的显示与否监听)
- [android stuido找不到源码](#android-stuido找不到源码)

## android:screenOrientation

- "unspecified", 默认值. 由系统选择显示方向. 在不同的设备可能会有所不同..
- "landscape" 横向
- "portrait" 纵向
- "user" 用户当前的首选方向
- **"behind"** 与在活动堆栈下的活动相同方向
- "sensor" 根据物理方向传感器确定方向. 取决于用户手持的方向, 当用户转动设备, 它跟随改变
- "nosensor" 不经物理方向传感器确定方向. 该传感器被忽略, 所以当用户转动设备, 显示不会跟随改变. 除了这个区别，系统选择使用相同的政策取向对于"未指定"设置. 系统根据"未指定"("unspecified")设定选择相同显示方向.


## Fragment的显示与否监听

- 当Fragment配合ViewPager使用时，使用setUserVisibleHint()判断Fragment是显示还是隐藏。
- 当Fragment配合FragmentTransition使用时，使用onHiddenChanged()来判断Fragment是显示还是隐藏，但是第一次显示要在onResume()里判断.


