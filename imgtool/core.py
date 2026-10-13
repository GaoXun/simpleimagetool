"""Image processing operations used by the command-line interface."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def default_output_path(input_path: Path) -> Path:
    """Return the default output path next to ``input_path``."""

    return input_path.with_name(f"{input_path.stem}_processed{input_path.suffix}")


def process_image(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    width: int | None = None,
    grayscale: bool = False,
    rotate: float | None = None,
    quality: int | None = None,
) -> Path:
    """Process an image and return the written output path."""

    source = Path(input_path)
    destination = Path(output_path) if output_path is not None else default_output_path(source)

    with Image.open(source) as image:
        source_format = image.format
        processed = image.copy()

    if rotate is not None:
        if not 0 <= rotate <= 360:
            raise ValueError("旋转角度必须在 0 到 360 之间")
        # expand=True makes Pillow compute a canvas containing the full rotated image.
        rotated = processed.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)
        processed.close()
        processed = rotated

    if width is not None:
        if width <= 0:
            raise ValueError("宽度必须是正整数")
        # Round the proportional height to the nearest whole pixel.
        height = max(1, round(processed.height * width / processed.width))
        resized = processed.resize((width, height), Image.Resampling.LANCZOS)
        processed.close()
        processed = resized

    if grayscale:
        grayscale_image = processed.convert("L")
        processed.close()
        processed = grayscale_image

    destination.parent.mkdir(parents=True, exist_ok=True)
    save_kwargs: dict[str, object] = {}
    if destination.suffix == "" and source_format:
        save_kwargs["format"] = source_format
    if quality is not None:
        if not 1 <= quality <= 100:
            raise ValueError("质量必须是 1 到 100 之间的整数")
        output_format = source_format if destination.suffix == "" else destination.suffix[1:]
        if output_format.lower() in {"jpg", "jpeg"}:
            save_kwargs["quality"] = quality
    processed.save(destination, **save_kwargs)
    processed.close()
    return destination
