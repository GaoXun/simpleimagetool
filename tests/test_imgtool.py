from pathlib import Path
from unittest.mock import patch

from PIL import Image

from imgtool.cli import main
from imgtool.core import process_image


def make_test_image(path: Path, size: tuple[int, int] = (8, 4)) -> None:
    image = Image.new("RGB", size)
    for x in range(size[0]):
        for y in range(size[1]):
            image.putpixel((x, y), (x * 20, y * 40, 120))
    image.save(path)


def test_resize_preserves_ratio(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    make_test_image(source, (8, 4))

    output = process_image(source, width=5)

    with Image.open(output) as result:
        assert result.size == (5, 2)


def test_grayscale_conversion(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    make_test_image(source)

    output = process_image(source, grayscale=True)

    with Image.open(output) as result:
        assert result.mode == "L"


def test_missing_file_returns_exit_code_2(capsys, tmp_path: Path) -> None:
    missing = tmp_path / "missing.png"

    assert main([str(missing)]) == 2
    assert "输入文件不存在" in capsys.readouterr().out


def test_unrecognized_file_returns_exit_code_2(capsys, tmp_path: Path) -> None:
    source = tmp_path / "not-an-image.bin"
    source.write_bytes(b"not an image")

    assert main([str(source)]) == 2
    assert "无法识别的图片文件" in capsys.readouterr().out


def test_default_output_name(tmp_path: Path) -> None:
    source = tmp_path / "photo.png"
    make_test_image(source)

    output = process_image(source)

    assert output == tmp_path / "photo_processed.png"
    assert output.exists()


def test_rotate_expands_canvas_without_cropping(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    make_test_image(source, (8, 4))

    output = process_image(source, rotate=90)

    with Image.open(output) as result:
        assert result.size == (4, 8)


def test_jpeg_quality_is_applied(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    make_test_image(source, (20, 20))
    output = tmp_path / "result.jpg"

    with patch.object(Image.Image, "save", autospec=True) as save:
        process_image(source, output, quality=25)

    assert save.call_args.kwargs["quality"] == 25


def test_png_quality_is_ignored_with_notice(capsys, tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    make_test_image(source)

    assert main([str(source), "--quality", "25"]) == 0
    assert "PNG 输出不使用 --quality 参数，已忽略" in capsys.readouterr().out


def test_batch_mode_writes_supported_images_to_output(monkeypatch, capsys, tmp_path: Path) -> None:
    input_dir = tmp_path / "images"
    input_dir.mkdir()
    make_test_image(input_dir / "one.png", (8, 4))
    make_test_image(input_dir / "two.jpg", (6, 3))
    (input_dir / "ignore.txt").write_text("not an image")
    monkeypatch.chdir(tmp_path)

    assert main([str(input_dir), "--width", "4"]) == 0
    assert (tmp_path / "output" / "one.png").exists()
    assert (tmp_path / "output" / "two.jpg").exists()
    assert "已生成" in capsys.readouterr().out


def test_empty_batch_directory_returns_exit_code_2(capsys, tmp_path: Path) -> None:
    input_dir = tmp_path / "empty"
    input_dir.mkdir()

    assert main([str(input_dir)]) == 2
    assert "文件夹为空或没有可处理的图片" in capsys.readouterr().out
