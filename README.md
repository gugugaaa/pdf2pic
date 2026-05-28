# pdf 2 pic

复习经常需要给AI发截图，只传入页号和长度，自动在pdf截图并且放在clipboard，用win+v查看

## 功能

- 图片：比如1-4面变成 1-3.png 和 4.png 两张长图并复制到了剪贴板
- index：保存(timestamp,start,end,label)到同级目录同名csv，追加

## 用法

```python
pdf2pic C:\Users\your-name\Documents\example.pdf
# 进入交互模式
> 13,8          # 默认每3页一张长图
> 13,8 -l2      # 每2页一张长图
> q             # 退出
```

