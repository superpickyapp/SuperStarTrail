# Sky Mask Dual-Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 支持用户提供一张 PNG 蒙版，将图像分为天空（用户选择的堆栈模式）和地景（固定 Comet 模式）两个区域分别堆栈，最后按蒙版混合输出。

**Architecture:** 新增 `MaskProcessor` 类负责蒙版的加载/验证/旋转；`StackingEngine` 扩展为双轨模式（sky_result + fg_result），有蒙版时并行维护两套累积结果，`get_result()` 最终按蒙版混合；UI 在文件列表面板增加"选择蒙版"按钮，CLI 增加 `--mask` 参数。

**Tech Stack:** Python, NumPy, PIL/Pillow, PyQt5, rawpy

---

## 文件结构

| 操作 | 文件 | 职责 |
|---|---|---|
| 新建 | `src/core/mask_processor.py` | 加载PNG蒙版、验证尺寸、旋转、返回 float32 数组 |
| 新建 | `tests/test_mask_processor.py` | MaskProcessor 单元测试 |
| 修改 | `src/core/stacking_engine.py` | 双轨堆栈逻辑（sky/fg result + 混合） |
| 修改 | `tests/test_stacking_engine.py` | 补充双轨堆栈测试 |
| 修改 | `src/ui/panels/file_list_panel.py` | 增加蒙版选择按钮和 `get_mask_path()` |
| 修改 | `src/ui/main_window.py` | ProcessThread 和 PreviewThread 传入蒙版 |
| 修改 | `src/cli.py` | 增加 `--mask` 参数 |

---

## Task 1：MaskProcessor — 加载和预处理蒙版

**Files:**
- Create: `src/core/mask_processor.py`
- Create: `tests/test_mask_processor.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_mask_processor.py
import numpy as np
import pytest
from pathlib import Path
from PIL import Image
import tempfile

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mask_processor import MaskProcessor


@pytest.fixture
def tmp_mask(tmp_path):
    """创建一个 100x200 的渐变蒙版 PNG（上半白=天空，下半黑=地景）"""
    arr = np.zeros((100, 200), dtype=np.uint8)
    arr[:50, :] = 255  # 上半为天空
    img = Image.fromarray(arr, mode='L')
    p = tmp_path / "mask.png"
    img.save(str(p))
    return p


def test_load_returns_float32(tmp_mask):
    mask = MaskProcessor.load(tmp_mask, target_shape=(100, 200))
    assert mask.dtype == np.float32


def test_load_value_range(tmp_mask):
    mask = MaskProcessor.load(tmp_mask, target_shape=(100, 200))
    assert mask.min() >= 0.0
    assert mask.max() <= 1.0


def test_load_correct_values(tmp_mask):
    mask = MaskProcessor.load(tmp_mask, target_shape=(100, 200))
    assert mask[0, 0] == pytest.approx(1.0)   # 天空（白）
    assert mask[99, 0] == pytest.approx(0.0)  # 地景（黑）


def test_load_resizes_to_target(tmp_mask):
    mask = MaskProcessor.load(tmp_mask, target_shape=(200, 400))
    assert mask.shape == (200, 400)


def test_load_rotation_90(tmp_mask):
    """旋转 90° 后宽高互换"""
    mask = MaskProcessor.load(tmp_mask, target_shape=(200, 100), rotation=90)
    assert mask.shape == (200, 100)


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        MaskProcessor.load(Path("nonexistent.png"), target_shape=(100, 200))


def test_load_wrong_extension(tmp_path):
    p = tmp_path / "mask.jpg"
    Image.fromarray(np.zeros((10, 10), dtype=np.uint8)).save(str(p))
    with pytest.raises(ValueError, match="PNG"):
        MaskProcessor.load(p, target_shape=(10, 10))
```

- [ ] **Step 2: 运行确认失败**

```bash
cd /Users/jameszhenyu/Documents/JamesAPPS/SuperStarTrail
python -m pytest tests/test_mask_processor.py -v
```
预期：`ModuleNotFoundError: No module named 'core.mask_processor'`

- [ ] **Step 3: 实现 MaskProcessor**

```python
# src/core/mask_processor.py
"""
蒙版处理模块

加载 PNG 灰度蒙版，验证格式，缩放到目标分辨率，应用旋转。
蒙版约定：白色(255) = 天空，黑色(0) = 地景。
返回 float32 数组 (H, W)，值域 0.0～1.0。
"""

from pathlib import Path
import numpy as np
from PIL import Image


class MaskProcessor:
    """PNG 蒙版加载与预处理"""

    @staticmethod
    def load(mask_path: Path, target_shape: tuple, rotation: int = 0) -> np.ndarray:
        """
        加载 PNG 蒙版并预处理。

        Args:
            mask_path:    PNG 文件路径
            target_shape: 目标分辨率 (H, W)，与处理后图像一致（已含旋转）
            rotation:     顺时针旋转角度（0/90/180/270），与图像旋转保持一致

        Returns:
            float32 数组 (H, W)，0.0=地景，1.0=天空

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件不是 PNG
        """
        mask_path = Path(mask_path)

        if not mask_path.exists():
            raise FileNotFoundError(f"蒙版文件不存在: {mask_path}")

        if mask_path.suffix.lower() != ".png":
            raise ValueError(f"蒙版必须是 PNG 格式，收到: {mask_path.suffix}")

        img = Image.open(mask_path).convert("L")  # 转为单通道灰度

        # 先旋转（与图像旋转保持一致），再缩放到目标尺寸
        if rotation:
            # PIL rotate 是逆时针，顺时针 N° = 逆时针 (360-N)°
            img = img.rotate(360 - rotation, expand=True)

        target_h, target_w = target_shape
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.LANCZOS)

        mask = np.array(img, dtype=np.float32) / 255.0
        return mask
```

- [ ] **Step 4: 运行确认通过**

```bash
python -m pytest tests/test_mask_processor.py -v
```
预期：全部 `PASSED`

- [ ] **Step 5: 提交**

```bash
git add src/core/mask_processor.py tests/test_mask_processor.py
git commit -m "feat: 新增 MaskProcessor，加载/验证/旋转 PNG 蒙版"
```

---

## Task 2：StackingEngine 双轨堆栈模式

**Files:**
- Modify: `src/core/stacking_engine.py`
- Modify: `tests/test_stacking_engine.py`

**设计要点：**
- 有蒙版时，`self.result` 照常维护（用于延时预览帧）
- 额外维护 `self.sky_result`（用户选模式）和 `self.fg_result`（固定 Comet fade=0.97）
- `get_result()` 有蒙版时用 `sky * mask + fg * (1-mask)` 混合后返回
- `self.sky_mask` 是 float32 (H,W)，在 `__init__` 传入

- [ ] **Step 1: 写失败测试**

```python
# 追加到 tests/test_stacking_engine.py 末尾
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from core.stacking_engine import StackingEngine, StackMode


class TestDualStackWithMask:

    def setup_method(self):
        # 4x4 图像，2 张，各通道值不同
        self.img1 = np.full((4, 4, 3), 1000, dtype=np.uint16)
        self.img2 = np.full((4, 4, 3), 3000, dtype=np.uint16)
        # 蒙版：左半=天空(1.0)，右半=地景(0.0)
        mask = np.zeros((4, 4), dtype=np.float32)
        mask[:, :2] = 1.0
        self.mask = mask

    def test_get_result_without_mask_unchanged(self):
        """无蒙版时行为与之前完全一致"""
        engine = StackingEngine(StackMode.LIGHTEN)
        engine.add_image(self.img1)
        engine.add_image(self.img2)
        result = engine.get_result()
        assert result[0, 0, 0] == 3000  # Lighten 取最大

    def test_sky_uses_user_mode_lighten(self):
        """天空区域使用 Lighten 模式"""
        engine = StackingEngine(StackMode.LIGHTEN, sky_mask=self.mask)
        engine.add_image(self.img1)
        engine.add_image(self.img2)
        result = engine.get_result()
        # 左列=天空，Lighten → max(1000, 3000) = 3000
        assert result[0, 0, 0] == 3000

    def test_foreground_uses_comet(self):
        """地景区域固定使用 Comet 模式（fade=0.97），不受用户模式影响"""
        engine = StackingEngine(StackMode.LIGHTEN, sky_mask=self.mask)
        engine.add_image(self.img1)
        engine.add_image(self.img2)
        result = engine.get_result()
        # 右列=地景，Comet: 1000*0.97 + 3000*0.03 = 970 + 90 = 1060
        expected = int(1000 * 0.97 + 3000 * 0.03)
        assert abs(int(result[0, 3, 0]) - expected) <= 1  # 允许 1 的舍入误差

    def test_mask_shape_mismatch_raises(self):
        """蒙版尺寸与图像不匹配时抛出 ValueError"""
        wrong_mask = np.ones((10, 10), dtype=np.float32)
        engine = StackingEngine(StackMode.LIGHTEN, sky_mask=wrong_mask)
        with pytest.raises(ValueError, match="蒙版尺寸"):
            engine.add_image(self.img1)

    def test_result_shape_preserved(self):
        """有蒙版时输出形状不变"""
        engine = StackingEngine(StackMode.LIGHTEN, sky_mask=self.mask)
        engine.add_image(self.img1)
        result = engine.get_result()
        assert result.shape == (4, 4, 3)
```

- [ ] **Step 2: 运行确认失败**

```bash
python -m pytest tests/test_stacking_engine.py::TestDualStackWithMask -v
```
预期：`TypeError` 或 `unexpected keyword argument 'sky_mask'`

- [ ] **Step 3: 修改 StackingEngine**

在 `__init__` 参数列表末尾加 `sky_mask`:

```python
# src/core/stacking_engine.py  __init__ 参数末尾追加
def __init__(
    self,
    mode: StackMode = StackMode.LIGHTEN,
    enable_gap_filling: bool = False,
    gap_fill_method: str = "morphological",
    gap_size: int = 3,
    enable_timelapse: bool = False,
    timelapse_output_path: Optional[Path] = None,
    video_fps: int = 30,
    sky_mask: Optional[np.ndarray] = None,   # ← 新增
):
```

在 `self.count = 0` 后面追加双轨状态：

```python
        # 双轨堆栈（有蒙版时启用）
        self.sky_mask: Optional[np.ndarray] = sky_mask  # float32 (H,W), 1=天空 0=地景
        self.sky_result: Optional[np.ndarray] = None    # 天空累积（用户选模式）
        self.fg_result: Optional[np.ndarray] = None     # 地景累积（固定 Comet fade=0.97）
        self._FG_FADE = 0.97
```

`reset()` 方法追加清空：

```python
    def reset(self):
        self.result = None
        self.count = 0
        self.sky_result = None
        self.fg_result = None
```

在 `add_image` 的 shape 校验之后、模式分支之前插入双轨逻辑：

```python
        # ── 双轨堆栈（有蒙版时）──────────────────────────────
        if self.sky_mask is not None:
            if self.sky_result is None:
                # 第一张：校验蒙版尺寸
                if self.sky_mask.shape != img_float.shape[:2]:
                    raise ValueError(
                        f"蒙版尺寸 {self.sky_mask.shape} 与图像 {img_float.shape[:2]} 不匹配"
                    )
                self.sky_result = img_float.copy()
                self.fg_result = img_float.copy()
            else:
                # 天空：用用户选定的模式
                if self.mode == StackMode.LIGHTEN:
                    self.sky_result = _fast_maximum(self.sky_result, img_float)
                elif self.mode == StackMode.AVERAGE:
                    self.sky_result = (
                        self.sky_result * self.count + img_float
                    ) / (self.count + 1)
                elif self.mode == StackMode.COMET:
                    self.sky_result = (
                        self.sky_result * self.comet_fade_factor
                        + img_float * (1 - self.comet_fade_factor)
                    )
                # 地景：固定 Comet fade=0.97
                self.fg_result = (
                    self.fg_result * self._FG_FADE
                    + img_float * (1 - self._FG_FADE)
                )
        # ── 原有单轨逻辑（无蒙版时）保持不变 ──────────────
```

在 `get_result` 的 `if self.result is None` 校验后、`needs_modification` 之前插入混合逻辑：

```python
        # 有蒙版：混合天空和地景两个结果
        if self.sky_mask is not None and self.sky_result is not None:
            mask3 = self.sky_mask[:, :, np.newaxis]
            blended = self.sky_result * mask3 + self.fg_result * (1 - mask3)
            blended = np.clip(blended, 0, 65535).astype(np.uint16)
            # 间隔填充仍然适用
            if apply_gap_filling and self.enable_gap_filling and self.gap_filler is not None:
                return self.gap_filler.fill_gaps(
                    blended, gap_size=self.gap_size, intensity_threshold=0.1
                )
            return blended
```

- [ ] **Step 4: 运行确认通过**

```bash
python -m pytest tests/test_stacking_engine.py -v
```
预期：全部 `PASSED`（包括原有测试）

- [ ] **Step 5: 提交**

```bash
git add src/core/stacking_engine.py tests/test_stacking_engine.py
git commit -m "feat: StackingEngine 支持双轨蒙版堆栈（天空用户模式+地景固定 Comet）"
```

---

## Task 3：FileListPanel — 蒙版选择按钮

**Files:**
- Modify: `src/ui/panels/file_list_panel.py`

- [ ] **Step 1: 增加信号、状态和 UI**

在信号定义区追加：

```python
mask_path_changed = pyqtSignal(object)  # 蒙版路径改变（Path 或 None）
```

在 `self._rotation` 下方追加状态：

```python
self._mask_path: Optional[Path] = None  # 当前蒙版文件路径
```

在旋转行下方、文件列表前插入蒙版行：

```python
        # 蒙版选择
        mask_layout = QHBoxLayout()
        self.btn_select_mask = QPushButton("选择蒙版")
        self.btn_select_mask.setToolTip(
            "选择 PNG 灰度蒙版文件（白色=天空，黑色=地景）\n"
            "天空区域使用你选择的堆栈模式\n"
            "地景区域自动使用彗星模式降噪"
        )
        self.btn_select_mask.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.btn_select_mask.clicked.connect(self._select_mask)
        mask_layout.addWidget(self.btn_select_mask)

        self.label_mask = QLabel("未选择蒙版（单一模式）")
        self.label_mask.setStyleSheet(INFO_LABEL_STYLE)
        self.label_mask.setWordWrap(True)
        mask_layout.addWidget(self.label_mask, 1)

        self.btn_clear_mask = QPushButton("清除")
        self.btn_clear_mask.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.btn_clear_mask.setEnabled(False)
        self.btn_clear_mask.clicked.connect(self._clear_mask)
        mask_layout.addWidget(self.btn_clear_mask)

        file_layout.addLayout(mask_layout)
```

- [ ] **Step 2: 增加方法**

在 `get_rotation()` 下方追加：

```python
    def get_mask_path(self) -> Optional[Path]:
        """获取当前蒙版文件路径，未选择时返回 None"""
        return self._mask_path

    def _select_mask(self):
        """打开文件对话框选择 PNG 蒙版"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择蒙版文件", "", "PNG 文件 (*.png)"
        )
        if path:
            self._mask_path = Path(path)
            self.label_mask.setText(self._mask_path.name)
            self.btn_clear_mask.setEnabled(True)
            self.mask_path_changed.emit(self._mask_path)

    def _clear_mask(self):
        """清除蒙版"""
        self._mask_path = None
        self.label_mask.setText("未选择蒙版（单一模式）")
        self.btn_clear_mask.setEnabled(False)
        self.mask_path_changed.emit(None)
```

在 `_load_folder` 的旋转重置代码后追加：

```python
        # 新文件夹不自动清除蒙版（蒙版通常跨目录复用）
```

（说明：刻意不重置蒙版，用户换目录时蒙版保留，方便同一组素材多次处理）

- [ ] **Step 3: 运行现有测试确认不破坏**

```bash
python -m pytest tests/ -q
```
预期：49 passed

- [ ] **Step 4: 提交**

```bash
git add src/ui/panels/file_list_panel.py
git commit -m "feat: FileListPanel 新增蒙版选择按钮和 get_mask_path()"
```

---

## Task 4：MainWindow / ProcessThread — 蒙版传递

**Files:**
- Modify: `src/ui/main_window.py`

- [ ] **Step 1: ProcessThread 加 mask_path 参数**

在 `rotation: int = 0` 后追加：

```python
mask_path: Optional[Path] = None,
```

在 `self.rotation = rotation` 后追加：

```python
self.mask_path = mask_path
```

- [ ] **Step 2: ProcessThread.run() 加载蒙版并传给引擎**

在 `engine = StackingEngine(...)` 前插入蒙版加载：

```python
            # 加载蒙版（如果指定）
            sky_mask = None
            if self.mask_path is not None:
                from core.mask_processor import MaskProcessor
                # 先处理一张图得到 target_shape
                sample_img = processor.process(
                    self.file_paths[0], rotation=self.rotation
                )
                try:
                    sky_mask = MaskProcessor.load(
                        self.mask_path,
                        target_shape=sample_img.shape[:2],
                        rotation=self.rotation,
                    )
                    self.log_message.emit(f"蒙版已加载: {self.mask_path.name}")
                    self.log_message.emit("天空→用户模式  地景→彗星模式（自动降噪）")
                except Exception as e:
                    self.log_message.emit(f"⚠️  蒙版加载失败，使用单一模式: {e}")
                    sky_mask = None
```

在 `engine = StackingEngine(...)` 调用中追加 `sky_mask=sky_mask`：

```python
            engine = StackingEngine(
                self.stack_mode,
                enable_gap_filling=self.enable_gap_filling,
                gap_fill_method=self.gap_fill_method,
                gap_size=self.gap_size,
                enable_timelapse=self.enable_timelapse,
                timelapse_output_path=timelapse_output_path,
                video_fps=self.video_fps,
                sky_mask=sky_mask,      # ← 新增
            )
```

- [ ] **Step 3: start_processing() 传入 mask_path**

在 `rotation=self.file_list_panel.get_rotation(),` 后追加：

```python
            mask_path=self.file_list_panel.get_mask_path(),
```

- [ ] **Step 4: 运行测试确认不破坏**

```bash
python -m pytest tests/ -q
```
预期：49 passed

- [ ] **Step 5: 提交**

```bash
git add src/ui/main_window.py
git commit -m "feat: ProcessThread 支持蒙版传递，自动加载并传给 StackingEngine"
```

---

## Task 5：CLI — `--mask` 参数

**Files:**
- Modify: `src/cli.py`

- [ ] **Step 1: 增加参数**

在 `--rotation` 参数后追加：

```python
    p_stack.add_argument("--mask", default=None,
                         help="PNG 灰度蒙版路径（白=天空/用户模式，黑=地景/彗星模式）")
```

- [ ] **Step 2: cmd_stack() 加载蒙版**

在 `start_time = time.time()` 前插入蒙版加载：

```python
    # 加载蒙版（如果指定）
    sky_mask = None
    if args.mask:
        from core.mask_processor import MaskProcessor
        mask_path = Path(args.mask)
        sample_img = processor.process(all_files[0], rotation=args.rotation)
        try:
            sky_mask = MaskProcessor.load(
                mask_path,
                target_shape=sample_img.shape[:2],
                rotation=args.rotation,
            )
            print(f"蒙版已加载: {mask_path.name}  天空→{args.mode}  地景→彗星模式")
        except Exception as e:
            print(f"⚠️  蒙版加载失败，使用单一模式: {e}")
```

将 `engine = StackingEngine(...)` 调用追加 `sky_mask=sky_mask`：

```python
    engine = StackingEngine(
        stack_mode,
        enable_gap_filling=args.fill_gaps,
        gap_fill_method=args.gap_method,
        gap_size=args.gap_size,
        enable_timelapse=args.timelapse,
        timelapse_output_path=timelapse_output_path,
        video_fps=args.fps,
        sky_mask=sky_mask,      # ← 新增
    )
```

- [ ] **Step 3: 运行测试**

```bash
python -m pytest tests/ -q
python src/cli.py stack --help  # 确认 --mask 出现在帮助里
```

- [ ] **Step 4: 提交**

```bash
git add src/cli.py
git commit -m "feat: CLI sst stack 新增 --mask 参数支持双轨蒙版堆栈"
```

---

## Task 6：集成验证（CLI 真实数据）

- [ ] **Step 1: 用 PIL 快速生成一个测试蒙版**

```bash
python -c "
from PIL import Image
import numpy as np
# 生成 5504x8256 的蒙版（Z9 裁剪分辨率）：上 40% 为天空，下 60% 为地景
h, w = 5520, 8280
arr = np.zeros((h, w), dtype=np.uint8)
arr[:int(h*0.4), :] = 255
Image.fromarray(arr).save('/tmp/test_mask.png')
print('蒙版已生成: /tmp/test_mask.png')
"
```

- [ ] **Step 2: 跑 5 张 + 蒙版验证双轨流程**

```bash
python src/cli.py stack /Volumes/990PRO4TB/2026/2026-03-07/315JMSZ9 \
    --limit 5 \
    --mask /tmp/test_mask.png \
    -o /tmp/sst_mask_test \
    2>&1 | grep -v "^20"
```

预期输出包含：
```
蒙版已加载: test_mask.png  天空→lighten  地景→彗星模式
✅ 全部 5 个文件处理成功
```

- [ ] **Step 3: 验证输出文件存在且大小合理**

```bash
ls -lh /tmp/sst_mask_test/
```
预期：有 `.tif` 文件，大小 200MB 以上

- [ ] **Step 4: 全测试套件通过**

```bash
python -m pytest tests/ -q
```
预期：全部 passed

- [ ] **Step 5: 最终提交**

```bash
git add docs/superpowers/plans/2026-04-02-sky-mask-dual-stack.md
git commit -m "docs: 新增天空蒙版双轨堆栈实施计划"
```

---

## 自审核

**Spec 覆盖：**
- ✅ PNG 蒙版选择按钮（Task 3）
- ✅ 天空使用用户选模式（Task 2）
- ✅ 地景固定 Comet fade=0.97（Task 2）
- ✅ 蒙版旋转与图像同步（Task 1 MaskProcessor）
- ✅ 蒙版软边（float32 天然支持渐变混合）
- ✅ CLI --mask 支持（Task 5）
- ✅ 无蒙版时行为完全不变（Task 2 测试覆盖）

**类型一致性：**
- `MaskProcessor.load()` → `np.ndarray float32 (H,W)` → `StackingEngine(sky_mask=...)` → `self.sky_mask` → 混合时 `mask[:,:,np.newaxis]` 全链路一致
- `get_mask_path()` → `Optional[Path]` → `ProcessThread(mask_path=...)` → `MaskProcessor.load(mask_path, ...)` 全链路一致

**无占位符：** 所有步骤均含完整代码。
