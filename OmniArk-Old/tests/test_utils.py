"""工具函数测试。"""

from omniark.utils.formatting import human_readable_size, round_half_up
from omniark.utils.files import find_files_with_extension, directory_size
from omniark.utils.timeutil import storage_snapshot_time, detailed_time


class TestFormatting:
    def test_human_readable_size(self):
        assert human_readable_size(500) == "500.0B"
        assert human_readable_size(2048) == "2.0KB"
        assert human_readable_size(1024 ** 2) == "1.0MB"
        assert human_readable_size(int(54.89 * 1024 ** 2)).startswith("54.")
        # 超过 TB 不再返回 None（旧版 bug）
        assert human_readable_size(1024 ** 5).endswith("PB")

    def test_round_half_up(self):
        assert round_half_up(2.5) == 3
        assert round_half_up(2.4) == 2
        assert round_half_up(1.005, 2) == 1.01


class TestFiles:
    def test_find_with_extension(self, tmp_path):
        (tmp_path / "a.jar").touch()
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "b.jar").touch()
        (tmp_path / "c.txt").touch()
        jars = find_files_with_extension(tmp_path, ".jar")
        assert len(jars) == 2
        all_files = find_files_with_extension(tmp_path, "")
        assert len(all_files) == 3

    def test_find_in_missing_dir(self, tmp_path):
        assert find_files_with_extension(tmp_path / "nope", ".jar") == []

    def test_directory_size(self, tmp_path):
        (tmp_path / "a.bin").write_bytes(b"x" * 100)
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "b.bin").write_bytes(b"y" * 50)
        assert directory_size(tmp_path) == 150


class TestTimeUtil:
    def test_detailed_time_format(self):
        import re
        assert re.fullmatch(r"\d{4}/\d{2}/\d{2}/\d{2}:\d{2}:\d{2}",
                            detailed_time())

    def test_snapshot_time_all_ranges(self):
        """覆盖旧版 Auto_Time 返回 None 的区间（60、>=31536000）。"""
        assert storage_snapshot_time(30).endswith("秒")
        assert storage_snapshot_time(60)  # 旧版此处返回 None
        assert storage_snapshot_time(3600).endswith("时")
        assert storage_snapshot_time(86400 * 2).endswith("日")
        assert storage_snapshot_time(86400 * 40)  # 不再为 None
        assert storage_snapshot_time(99999999)  # 不再为 None
