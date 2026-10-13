# imgtool

命令行图片处理工具，支持等比缩放、灰度转换、旋转和批量处理。

## 安装

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
```

## 参数

- `图片`：输入图片文件或文件夹路径。
- `--width N`：等比缩放到宽度 `N` 像素。
- `--grayscale`：转换为灰度图。
- `--rotate DEG`：逆时针旋转 `0` 到 `360` 度，自动扩大画布以保留完整内容。
- `--quality Q`：JPEG 输出质量，取值 `1` 到 `100`；PNG 输出忽略此参数并提示。
- `-o PATH`、`--output PATH`：指定单文件模式的输出路径。

未指定 `-o` 时，单文件输出会在原文件名旁生成 `_processed` 后缀的新文件。输入路径为文件夹时，所有 `.jpg`、`.jpeg` 和 `.png` 文件会输出到当前目录的 `output/` 子目录，文件名保持不变。

## 最小示例

```bash
python -m imgtool photo.png --width 800 --grayscale -o result.png
```
