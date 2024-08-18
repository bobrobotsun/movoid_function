这个一个对函数进行各方面操作的包，包含了很多十分精妙的功能。

这个包分了几个大的模块，分别对应了不同的函数操作小玩法

## 装饰器

装饰器部分包含了常见一个装饰器所需的一些辅助类的装饰器函数

### wraps

这个装饰器本质就是为了替代functools.wraps而创建的。

它的作用和functools.wraps本质上是一样的，唯一的区别就是它在装饰了函数之后，会把函数的参数和注释全部保留，使得在运行过程中可以正确获得原函数的参数情况。


## 函数

函数是针对函数直接或间接的一些操作的功能


### replace_function

替代函数，其本身是为了解决需要直接改变builtin函数的逻辑（对，就是你，print），但是又希望这个函数的变动可以随时复原，或者能自由地调用原函数地功能。

不过现在这个函数已经被开发得可以任意替换任意包内定义的普通函数

```python
from movoid_function import replace_function

def special_print(text):
    return text

replace_function(print, special_print)

a = print("666") #此时不会打印任何信息，并且会给a赋值为'666'
```
