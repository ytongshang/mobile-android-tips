# Storage

- android 存储方式有：
    - Shared Preferences
    - Internal Storage
    - External Storage
    - SQLite Databases
    - Network Connection

## 参考文档

- [彻底搞懂Android文件存储---内部存储，外部存储以及各种存储路径解惑](https://blog.csdn.net/u010937230/article/details/73303034)

## Shared preferences

- getSharedPreferences(),根据文件名返回不同的文件
- getPreferences()，唯一的一个，没有指定名字

## Internal Storage

- 保存后的文件默认专属于app,其它应用和用户都不能够查看的

### 私有文件的读写

- **保存方法**：调用openFileOutput()得到FileOutputStream.，调用write(),最后关闭close()

```java
String FILENAME = "hello_file";
String string = "hello world!";
FileOutputStream fos = mContext.openFileOutput(FILENAME, Context.MODE_PRIVATE);
fos.write(string.getBytes());
fos.close();
```

- **读取方法**：调用openFileInput()得到FileInputStream然后读取对应的内容
- 如果想要保存一个静态的文件，可以保存在res/raw/目录下，读取采用openRawResource()，参数为R.raw.<filename>，得到inputStream,但是该文件不能写

### 文件模式

- 文件的模式有MODE_PRIVATE，MODE_APPEND, MODE_WORLD_READABLE,MODE_WORLD_WRITEABLE.这四种
- **MODE_PRIVATE**,总是创建一个新的文件，如果已经存在，则删除原来存在的
- MODE_PRIVATE模式，相同userid(通过sharedUserId），都可以读取
- **MODE_APPEND，是追加模式**，对于Shared preferences来说，和MODE_PRIVATE一样，因为shared preference是一个xml,总是向里面插入数据，不存在追加说法
- **MODE_WORLD_READABLE，MODE_WORLD_WRITEABLE因为安全性的问题一般不要使用，可以考虑FileProvider代替**

### Saving cache files

- 如果缓存文件，而不是永久存储的话，采用getCacheDir()
- 存储在这其中的文件，可能会因为存储不足，而被删除掉

### 常用函数

- **File getFilesDir()**，Returns the absolute path to the directory on the filesystem where files created with openFileOutput(String, int) are stored.
- **File getDir()**，Creates (or opens an existing) directory within your internal storage space.
- **boolean deleteFile(String name)**，Deletes a file saved on the internal storage.
- **String[] fileList()**，Returns an array of files currently saved by your application.
- **File getDataDir()**,某个应用在内部存储中的缓存路径

## External Storage

- 使用外部存储需要检查权限READ_EXTERNAL_STORAGE或者WRITE_EXTERNAL_STORAGE
- 检查是否可用

```java
public boolean isExternalStorageWritable() {
    String state = Environment.getExternalStorageState();
    if (Environment.MEDIA_MOUNTED.equals(state)) {
        return true;
    }
    return false;
}
/* Checks if external storage is available to at least read */
public boolean isExternalStorageReadable() {
    String state = Environment.getExternalStorageState();
    if (Environment.MEDIA_MOUNTED.equals(state) ||
        Environment.MEDIA_MOUNTED_READ_ONLY.equals(state)) {
        return true;
    }
    return false;
}
```

- **Environment.getExternalStorageDirectory().getAbsolutePath(), 获取外部存储的根目录**
- **Environment.getExternalStoragePublicDirectory(),返回external storage中的公共的目录**，传入类型DIRECTORY_MUSIC,DIRECTORY_PICTURES, DIRECTORY_RINGTONES，可以让文件保存在对应的media-type的目录中，这样可以自media scanner动扫描到并组织这些文件

```java
public File getAlbumStorageDir(String albumName) {
    // Get the directory for the user's public pictures directory.
    File file = new File(Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_PICTURES), albumName);
    if (!file.mkdirs()) {
        Log.e(LOG_TAG, "Directory not created");
    }
    return file;
}
```

### getExternalFilesDir()

- 在外部存储中保存本app有关的数据，getExternalFilesDir()并且传入对应的文件类型，如果传入null,则返回根目录
- 当用户卸载app时，保存在getExternalFilesDir()其中的文件也会被卸载
- **保存在getExternalFilesDir()中的文件，不会被media scanner扫描到，通过MediaStore是查找不到的**，所以如果是原本属于用户，但是只是通过本App编辑的，比如用户的照片，不应当保存在getExternalFilesDir()目录中，而应当保存到getExternalStoragePublicDirectory()中
- **虽然是属于应用自身的数据，不会被MediaStore扫描到，但是由于是保存在外部存储，任何有WRITE_EXTERNAL_STORAGE权限的应用也是可以修改这些文件的**

### getExternalFilesDirs

- Android系统会分配一部分的Internal storage当作external Storage来使用，但是用户也可能安装了sd卡，这样在android 4.3或者更低，通过getExternalFilesDir()返回的目录只能读写当作external storage的internal storage,。Android 4.4或更高，可以能过getExternalFilesDirs()返回一个文件列表，包括当作external storage的internal storage,和外部的sd卡，
- 一般情况返回的array的第一个file是主要的目录，为了兼容性，可以使用ContextCompat.getExternalFilesDirs()
- getExternalFilesDir() and getExternalFilesDirs()这两个返回的目录，虽然是external storage中的属于app-private的目录，不能够被MediaStore查找到，但是，对于拥有READ_EXTERNAL_STORAGE仍然可以读取
- **兼容性考虑，使用ContextCompat.getExternalCacheDirs()**