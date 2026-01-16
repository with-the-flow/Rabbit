# Rabbit语言设计规范

## 语言哲学
"默认即合理" - 让90%的日常使用场景覆盖成为语言语法的一部分

## 核心特性

### 内置功能范围
✅ **默认内置** (高频基础操作):

#### 基础IO
- `print(...values)` - 格式化输出
- `input(prompt?)` - 控制台输入
- `readline()` - 读取单行

#### 字符串处理
- `len(s)` - 长度
- `split(sep)`, `join(list)` - 分割/连接
- `trim()`, `startsWith()`, `endsWith()` - 常用操作
- `toUpper()`, `toLower()` - 大小写转换
- `substr(start, end)` - 子字符串

#### 数学计算
- 常量: `pi`, `e`, `inf`
- 基础运算: `sqrt()`, `pow()`, `abs()`
- 三角函数: `sin()`, `cos()`, `tan()`
- 随机数: `rand()`, `randint(min,max)`
- 统计: `max()`, `min()`, `sum()`

#### 集合操作
- `map(fn)`, `filter(fn)`, `reduce(fn)`
- `sort()`, `reverse()`
- `includes(item)`, `indexOf(item)`

#### 数据格式
- `json.parse()`, `json.stringify()`
- `base64.encode()`, `base64.decode()`

#### 网络请求
- `http.get(url)`, `http.post(url, data)`
- `http.fetch(url, options)` - 统一请求接口

⏏️ **标准库** (use std/xxx):

#### 数学与科学计算
- `use std/math` - 高级数学函数
- `use std/stat` - 统计分析
- `use std/matrix` - 矩阵运算

#### 数据处理
- `use std/csv` - CSV文件处理
- `use std/json` - JSON增强功能
- `use std/xml` - XML解析

#### 网络与通信
- `use std/websocket` - WebSocket客户端
- `use std/http` - HTTP服务器功能
- `use std/smtp` - 邮件发送

#### 系统操作
- `use std/fs` - 文件系统操作
- `use std/os` - 操作系统接口
- `use std/process` - 进程管理

#### 并发编程
- `use std/thread` - 线程操作
- `use std/async` - 异步编程

### 设计参考
👍 **正面参考**:
```python
# Python风格内置
print("Hello")  # 无需导入
```

```javascript
// JavaScript风格函数直接可用
const len = "abc".length;
```

👎 **避免方式**:
```c++
// C++风格显式导入
#include <math.h>
double r = sqrt(2.0);
```

### 实现路线图

#### 阶段一：原型开发 (1-3个月)
- **目标**: 验证语言设计可行性
- **技术栈**: Python + PLY/Lark
- **里程碑**:
  - 基础语法解析器
  - AST生成器
  - 简单解释执行器
  - 内置函数实现(print, len, math等)

#### 阶段二：性能优化 (4-6个月)
- **目标**: 实现JIT编译和性能优化
- **技术栈**: llvmlite + Python
- **里程碑**:
  - llvmlite集成实现JIT
  - 类型推导系统
  - 基础标准库实现
  - 性能基准测试

#### 阶段三：生产化 (7-12个月)
- **目标**: 构建生产级运行时
- **技术栈**: C语言重写
- **里程碑**:
  - C语言运行时核心
  - 独立二进制生成
  - .rabbitc缓存格式设计
  - 完整标准库移植

### 错误处理机制

#### 统一错误类型
```rabbit
# 内置错误类型
try {
    data = json.parse(invalid_json)
} catch ParseError as e {
    print("JSON解析失败:", e.message)
}

# 自定义错误
def divide(a, b) {
    if b == 0 {
        throw ValueError("除数不能为零")
    }
    a / b
}
```

#### 错误传播
```rabbit
# 可选类型 (Option<T>)
result = maybe_divide(10, 0)
match result {
    Some(value) => print("结果:", value),
    None => print("计算失败")
}

# 结果类型 (Result<T, E>)
result = safe_divide(10, 0)
match result {
    Ok(value) => print("结果:", value),
    Err(error) => print("错误:", error)
}
```

## 核心语法设计

### 变量与赋值
```rabbit
# 弱类型，动态推导
name = "Alice"  
age = 25
scores = [98, 87, 92]

# 多变量赋值
x, y = 10, 20
```

### 运算符
```rabbit
# 数学运算 (支持²³等Unicode运算符)
sum = 3 + 5 * 2²

# 字符串拼接
greeting = "Hello " + name

# 比较运算
is_adult = age >= 18
```

### 流程控制
```rabbit
# if表达式 (可直接返回值)
result = if x > 0 { 
    "positive" 
} else { 
    "non-positive" 
}

# 模式匹配
match value {
    1 => print("one"),
    2..5 => print("two to five"),
    _ => print("other")
}

# for循环
for score in scores {
    print(score * 2)
}
```

### 函数定义
```rabbit
# 基本函数
def greet(name) {
    "Hello, " + name
}

# 匿名函数
double = fn(x) { x * 2 }
```

## 语法示例
```rabbit
# 数学运算直接可用
area = pi * r²  # 无需导入math

# 常用功能直接调用
names = ["Alice", "Bob"]
random_name = choice(names)

# 特定功能显式导入
use std/csv
data = csv.load("data.csv")
```

## 性能优化策略

### JIT编译优化
```rabbit
# 热点代码自动JIT编译
def fibonacci(n) {
    if n <= 1 {
        return n
    }
    fibonacci(n-1) + fibonacci(n-2)
}

# 运行时检测热点函数
# 自动生成机器码优化
```

### .rabbitc缓存格式
```
.rabbitc文件结构:
- 头部: 魔数 + 版本号
- AST缓存: 序列化的抽象语法树
- 字节码缓存: 优化后的字节码
- JIT代码缓存: 热点函数机器码
- 元数据: 依赖关系、编译时间戳
```

### 类型推导优化
```rabbit
# 静态类型推导 (运行时优化)
def add(a: number, b: number) -> number {
    a + b
}

# 动态类型标记 (JIT优化)
x = 10          # 标记为int
y = "hello"     # 标记为string
```

## 完整语法示例

```rabbit
# Rabbit语言完整示例
# 无需导入即可使用90%日常功能

# 基础计算
radius = 5.0
area = pi * radius²
print("圆面积:", area)

# 数据处理
data = {
    "name": "Alice",
    "age": 30,
    "scores": [95, 88, 92]
}

# JSON处理 (内置)
json_str = json.stringify(data)
parsed = json.parse(json_str)

# 网络请求 (内置)
response = http.get("https://api.example.com/data")
if response.status == 200 {
    print("数据获取成功:", response.text)
}

# 集合操作 (内置)
scores = [85, 92, 78, 95]
high_scores = filter(scores, fn(score) { score > 90 })
average = sum(scores) / len(scores)

# 特定功能导入
use std/csv
use std/stat

# CSV处理
records = csv.load("data.csv")
stats = stat.summary(records["score"])

# 错误处理
try {
    result = 10 / 0
} catch DivisionError as e {
    print("计算错误:", e.message)
}

# 模式匹配
match response.status {
    200 => print("成功"),
    404 => print("未找到"),
    500 => print("服务器错误"),
    _ => print("未知状态")
}
```

## 技术约束
- ❌ 不使用C++/Java/Go作为核心实现
- ❌ 避免早期研究CPython源码
- ✅ JIT阶段精读ceval.c和object.c

## 总结
Rabbit语言通过"默认即合理"的设计哲学，将高频基础功能内置到语言核心，显著降低开发者的认知负担。相比传统语言需要频繁导入库文件，Rabbit让开发者专注于业务逻辑而非基础设施。

**核心优势**:
1. 开箱即用 - 90%日常功能无需导入
2. 渐进式学习 - 从简单脚本到复杂应用平滑过渡
3. 性能优化 - JIT编译 + 缓存机制
4. 现代语法 - 借鉴Python/JavaScript/Swift最佳实践

**下一步建议**:
1. 开始原型阶段开发，验证语法设计
2. 建立社区反馈机制，收集实际使用场景
3. 制定标准库API规范
4. 设计IDE插件和工具链支持
