# Design Support Library

## SnackBar

- Snackbar提供了一个介于Toast和AlertDialog之间轻量级控件，它可以很方便的提供消息的提示和动作反馈

- 使用

```java
Snackbar.make(view, "Snack comes out", Snackbar.LENGTH_SHORT)
        .setAction("Confirm", new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Toast.makeText(CoordinatorActivity.this, "Toast", Toast.LENGTH_SHORT).show();
            }
        }).show();
```

- Snackbar**可以设置多个Action**


## TextInputLayout

- TextInputLayout作为一个父容器控件，包装了新的EditText。通常，单独的EditText会在用户输入第一个字母之后隐藏hint提示信息，
 但是现在你可以使用TextInputLayout 来将EditText封装起来，提示信息会变成一个显示在EditText之上的floating label，
 这样用户就始终知道他们现在输入的是什么。同时，如果给EditText增加监听，还可以给它增加更多的floating label

- TextInputLayout**不能够单独使用，必须配使EditText一起使用**

- 如果要更好的控制输入，可以使用TextInputEditText

- xml使用

```xml
<android.support.design.widget.TextInputLayout
         android:layout_width="match_parent"
         android:layout_height="wrap_content">

     <android.support.design.widget.TextInputEditText
             android:layout_width="match_parent"
             android:layout_height="wrap_content"
             android:hint="@string/form_username"/>

 </android.support.design.widget.TextInputLayout>
```

- 代码

```java
        final TextInputLayout textInputLayout = (TextInputLayout) findViewById(R.id.til_pwd);

        EditText editText = textInputLayout.getEditText();
        textInputLayout.setHint("Password");

        editText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
                if (s.length() > 4) {
                    textInputLayout.setError("Password error");
                    textInputLayout.setErrorEnabled(true);
                } else {
                    textInputLayout.setErrorEnabled(false);
                }
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });
    }
```

## Floating Action Button

- floating action button 是一个负责显示界面基本操作的圆形按钮

- FloatingActionButton继承自ImageView，你可以使用android:src或者ImageView的任意方法，比如setImageDrawable()来设置FloatingActionButton里面的图标

- xml

```xml
<android.support.design.widget.FloatingActionButton
        android:layout_height="wrap_content"
        android:layout_width="wrap_content"
        app:layout_anchor="@id/app_bar"
        app:layout_anchorGravity="bottom|right|end"
        android:src="@android:drawable/ic_done"
        android:layout_margin="15dp"
        android:clickable="true"
        app:fabSize="mini"/>
```

- **可以配合CoordinatorLayout， Snackbar使用**

## TabLayout

## NavigationView
