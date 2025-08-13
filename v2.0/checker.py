# coding=utf8
"""
启动一致性检查：
- 对 pixiv / bookmark 表各取最近 20 条记录，核对本地文件夹图片数量与 pageCount 是否一致；
- 使用 IsValidImage 校验图片完整性；
- 若不一致或存在损坏图片，则触发自动重下；重下后再次校验，仍失败则告警。
"""

import os
from typing import List, Tuple, Optional

from downer import Downloader
from folder import file_manager
from image_check import IsValidImage
from log_record import logger

TABLES = ["pixiv", "bookmark"]
LATEST_LIMIT = 20


def list_local_images(dir_path: str, pid: int) -> List[str]:
    if not dir_path or not os.path.isdir(dir_path):
        return []
    files = []
    try:
        for name in os.listdir(dir_path):
            if not name.lower().startswith(str(pid)):
                continue
            # 常见图片扩展
            lower = name.lower()
            if lower.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")):
                files.append(os.path.join(dir_path, name))
    except Exception:
        return []
    return files


def verify_folder(pid: int, path: str, page_count: int, illust_type: int) -> Tuple[bool, List[str]]:
    """返回 (是否通过, 需重下的文件列表)。
    - ugoira(type=2)：zip 或 gif 任一存在且 gif 可读视为通过
    - 单图/多图：图片数量需达到目标且每张校验通过
    """
    if not path or not os.path.isdir(path):
        return False, []

    # 动图：gif 或 zip 任一存在即可（gif 优先验证完整性）
    if illust_type == 2:
        gif = os.path.join(path, f"{pid}.gif")
        zipf = os.path.join(path, f"{pid}.zip")
        if os.path.exists(gif):
            ok = IsValidImage(gif)
            return (ok, [] if ok else [gif])
        if os.path.exists(zipf):
            return True, []
        return False, []

    images = list_local_images(path, pid)
    if page_count <= 1:
        if not images:
            return False, []
        # 任取第一张作为单图
        img = images[0]
        ok = IsValidImage(img)
        return (ok, [] if ok else [img])

    # 多图：至少 page_count 张，且全部有效
    if len(images) < page_count:
        return False, images
    invalid = [p for p in images if not IsValidImage(p)]
    return (len(invalid) == 0, invalid)


def redownload_one(d: Downloader, table: str, rec: dict) -> bool:
    """按表与记录重新下载该 PID，下载完成后再次校验。返回最终是否通过。"""
    pid = int(rec.get("pid"))
    illust_type = int(rec.get("illustType", 0))
    page_count = int(rec.get("pageCount", 1))

    # 推导保存目录（不写 DB）
    save_path = rec.get("path")
    if not save_path or save_path == "None":
        if table == "bookmark":
            user_dir = file_manager.bk_path
        else:
            uid = int(rec.get("uid", 0))
            user_name = rec.get("userName", "")
            user_dir = file_manager.select_user_path(uid, user_name)
        save_path = file_manager.mkdir_illusts(user_dir, pid)

    # 走 Downloader 获取信息与下载
    info = d.get_illust_info(pid, extra=("bookmark" if table == "bookmark" else "pixiv"))
    if not info or isinstance(info, str):
        logger.warning(f"[checker] 获取作品信息失败或不可访问: {pid} -> {info}")
        return False

    # 再次校验
    ok, invalid = verify_folder(pid, save_path, page_count, illust_type)
    if not ok:
        logger.warning(f"[checker] 重新下载后仍不一致/损坏: {pid} | invalid={len(invalid)}")
    return ok


def run_startup_check(d: Optional[Downloader] = None):
    d = d or Downloader()
    for table in TABLES:
        logger.info(f"[checker] 启动一致性检查 | 表: {table} | 最近 N: {LATEST_LIMIT}")
        try:
            latest = d.db.select_latest_records(table=table, limit=LATEST_LIMIT)
        except Exception:
            latest = []
        if not latest:
            logger.info(f"[checker] 表 {table} 无记录可检")
            continue

        total = 0
        ok_cnt = 0
        fix_cnt = 0
        fail_cnt = 0

        for rec in latest:
            pid = int(rec.get("pid"))
            path = rec.get("path")
            page_count = int(rec.get("pageCount", 1))
            illust_type = int(rec.get("illustType", 0))
            total += 1

            ok, invalid = verify_folder(pid, path, page_count, illust_type)
            if ok:
                ok_cnt += 1
                continue

            logger.warning(f"[checker] 不一致/疑似损坏，准备重下: {table} pid={pid} path={path}")
            ok2 = redownload_one(d, table, rec)
            if not ok2:
                fail_cnt += 1
                logger.warning(f"[checker] 重下失败：{table} pid={pid}")
            else:
                fix_cnt += 1
                logger.success(f"[checker] 重下完成 | 表:{table} PID:{pid} 再次校验通过")

        logger.info(
            f"[checker] 完成 | 表:{table} 总数:{total} 通过:{ok_cnt} 修复:{fix_cnt} 失败:{fail_cnt}"
        )


if __name__ == "__main__":
    run_startup_check()


