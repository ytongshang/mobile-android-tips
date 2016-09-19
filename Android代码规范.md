# java代码命名规范

## 类名

- 采用大驼峰式命名法
- 尽量避免缩写，除非该缩写是众所周知的，比如HTML，URL,如果类名称包含单词缩写，则单词缩写的每个字母均应大写
- 具体类的命名规范
- 示例

  ```java
  Product
  ProductManager
  ProductListActivity
  ProductListAdapter
  JsonHTTPRequest
  ```

## 方法名

- 动词或动名词，采用小驼峰命名法

- 常用方法的名字

方法       | 说明
:------- | :---------------------------------------
initXX() | 初始化相关方法,使用init为前缀标识，如初始化布局initView()
isXX()   | checkXX()方法返回值为boolean型的请使用is或check为前缀标识
