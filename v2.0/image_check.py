from os import PathLike
import os
from io import BytesIO
import argparse
from typing import Iterable, Tuple
from PIL import Image, ImageSequence, UnidentifiedImageError

# 判断文件是否为有效（完整且可解码）的图片
# 输入参数为文件路径，或二进制文件对象
def IsValidImage(file) -> bool:
    try:
        # 路径输入：优先走不读全文件的校验路径
        if isinstance(file, (str, PathLike)):
            file_path = str(file)
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                return False
            # 结构校验
            with Image.open(file_path) as im:
                im.verify()
            # 解码校验（重新打开；动图需逐帧解码）
            with Image.open(file_path) as im:
                if getattr(im, "is_animated", False):
                    for frame in ImageSequence.Iterator(im):
                        frame.load()
                else:
                    im.load()
            return True

        # 文件对象输入：复制到内存后双重校验
        try:
            file.seek(0)
        except Exception:
            pass
        buf = file.read()
        if not buf:
            return False
        with Image.open(BytesIO(buf)) as im:
            im.verify()
        with Image.open(BytesIO(buf)) as im:
            if getattr(im, "is_animated", False):
                for frame in ImageSequence.Iterator(im):
                    frame.load()
            else:
                im.load()
        return True
    except (UnidentifiedImageError, OSError, SyntaxError):
        return False


def _iter_image_files(root_dir: str, extensions: Tuple[str, ...]) -> Iterable[str]:
    for root, _, files in os.walk(root_dir):
        image_files = [fn for fn in files if fn.lower().endswith(extensions)]
        if not image_files:
            continue
        for filename in image_files:
            yield os.path.join(root, filename)


def main():
    parser = argparse.ArgumentParser(description="校验目录下图片文件是否损坏（Pillow verify+load 双重校验）")
    parser.add_argument(
        "path",
        nargs="?",
        default=os.environ.get("PIXIC_CHECK_PATH", r"E:\\BaiduNetdiskDownload\\pixic"),
        help="需要检测的根目录（默认读取环境变量 PIXIC_CHECK_PATH，若无则为示例路径）",
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=[".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"],
        help="需要检测的图片扩展名列表（不区分大小写）",
    )
    parser.add_argument(
        "--output",
        default="./corrupted_images.txt",
        help="输出损坏文件路径的文本文件",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="是否以追加模式写入输出文件（默认覆盖）",
    )
    args = parser.parse_args()

    extensions = tuple(ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in args.ext)

    if not args.append:
        # 覆盖清空旧结果
        with open(args.output, "w", encoding="utf-8") as f:
            pass

    total = 0
    broken = 0

    for img_file in _iter_image_files(args.path, extensions):
        total += 1
        if not IsValidImage(img_file):
            broken += 1
            print(img_file)
            with open(args.output, "a", encoding="utf-8") as output_file:
                output_file.write(img_file + "\n")

    print(f"checked: {total}, corrupted: {broken}, ok: {total - broken}")


if __name__ == "__main__":
    main()