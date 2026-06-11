# pdf 2 pic

> 复习时，经常需要给AI发连续多页的截图，缩放尺寸耽误复习。

使用本工具，只传入页号和长度，自动在pdf截图并且放在clipboard，用win+v查看

## 功能

- **图片**：比如1-4面变成 1-3.png 和 4.png 两张长图并复制到了剪贴板
- **index**：保存(timestamp,start,end,label)到同级目录同名csv，追加

> 也许这是人工对重点/分段的划分？看上去是不错的corpus...默认关闭

<img src="https://i.ibb.co/FLFDnPSJ/1234324.png" alt="win+v的效果图">

## 用法

### 安装

```powershell
.\install.ps1
```
会自动 uv，注册到 %LOCALAPPDATA%/pdf2pic，添加 PATH，无需 UAC

### 使用

```python
pdf2pic C:\Users\your-name\Documents\example.pdf
# 进入交互模式
> 13,8          # 默认每3页一张长图
> 13,8 -l2      # 每2页一张长图
> q             # 退出

# 保存 index
pdf2pic C:\Users\your-name\Documents\example.pdf -i
```

## 说明
- 只支持windows，因为是pwsh练手用的
- 我没有写打印pdf，因为兼容性差。建议手动打印。
