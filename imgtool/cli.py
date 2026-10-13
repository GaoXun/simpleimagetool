"""Command-line interface for imgtool."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import UnidentifiedImageError

from .core import process_image


SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imgtool",
        description="缩放、旋转图片或将图片转换为灰度图。",
    )
    parser.add_argument("input", metavar="图片", help="输入图片文件路径")
    parser.add_argument("--width", type=positive_int, metavar="N", help="等比缩放到指定宽度（像素）")
    parser.add_argument("--rotate", type=degrees, metavar="DEG", help="逆时针旋转角度（0-360）")
    parser.add_argument("--grayscale", action="store_true", help="转换为灰度图")
    parser.add_argument("--quality", type=quality_int, metavar="Q", help="JPEG 输出质量（1-100）")
    parser.add_argument("-o", "--output", metavar="PATH", help="输出图片文件路径")
    return parser


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("宽度必须是正整数") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("宽度必须是正整数")
    return parsed


def degrees(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("旋转角度必须是 0 到 360 之间的数字") from exc
    if not 0 <= parsed <= 360:
        raise argparse.ArgumentTypeError("旋转角度必须是 0 到 360 之间的数字")
    return parsed


def quality_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("质量必须是 1 到 100 之间的整数") from exc
    if not 1 <= parsed <= 100:
        raise argparse.ArgumentTypeError("质量必须是 1 到 100 之间的整数")
    return parsed


def _process_one(input_path: Path, output_path: Path, args: argparse.Namespace) -> tuple[Path | None, int]:
    try:
        output = process_image(
            input_path,
            output_path,
            width=args.width,
            grayscale=args.grayscale,
            rotate=args.rotate,
            quality=args.quality,
        )
    except UnidentifiedImageError:
        print(f"错误：无法识别的图片文件：{input_path}")
        return None, 2
    except OSError as exc:
        print(f"错误：图片处理失败：{exc}")
        return None, 1
    except ValueError as exc:
        print(f"错误：{exc}")
        return None, 2

    if args.quality is not None and output.suffix.lower() == ".png":
        print("提示：PNG 输出不使用 --quality 参数，已忽略。")
    print(f"已生成：{output}")
    return output, 0


def _process_directory(input_dir: Path, args: argparse.Namespace) -> int:
    candidates = sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    )
    if not candidates:
        print(f"提示：文件夹为空或没有可处理的图片：{input_dir}")
        return 2
    if args.output is not None:
        print("错误：批量模式输出固定为 ./output/，不能使用 -o。")
        return 2

    output_dir = Path("output")
    failed = False
    for input_path in candidates:
        _, status = _process_one(input_path, output_dir / input_path.name, args)
        if status != 0:
            failed = True
    return 2 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"错误：输入文件不存在：{input_path}")
        return 2
    if input_path.is_dir():
        return _process_directory(input_path, args)
    if not input_path.is_file():
        print(f"错误：输入路径不是文件：{input_path}")
        return 2

    _, status = _process_one(
        input_path,
        Path(args.output)
        if args.output
        else input_path.with_name(f"{input_path.stem}_processed{input_path.suffix}"),
        args,
    )
    return status
