"""
文件列表管理面板
负责文件选择、输出目录选择、文件列表显示和文件排除功能
"""
import os
from pathlib import Path
from typing import List, Callable, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QListWidget, QFileDialog,
    QMenu, QMessageBox, QToolButton, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from i18n.translator import Translator
from ui.styles import (
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    INFO_LABEL_STYLE,
)
from utils.settings import get_settings


class FileListPanel(QWidget):
    """文件列表管理面板"""

    # 信号定义
    files_selected = pyqtSignal(list)  # 当文件列表改变时触发
    output_dir_changed = pyqtSignal(str)  # 当输出目录改变时触发
    file_clicked = pyqtSignal(object)  # 当文件被点击时触发（用于预览）
    open_output_clicked = pyqtSignal()  # 打开输出目录按钮点击
    rotation_changed = pyqtSignal(int)  # 旋转角度改变时触发（0/90/180/270）
    mask_path_changed = pyqtSignal(object)  # 蒙版路径改变时触发（Path 或 None）

    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self.tr = translator

        # 数据存储
        self.raw_files: List[Path] = []  # 所有 RAW 文件
        self.excluded_files: set = set()  # 被排除的文件索引
        self.output_dir: Optional[str] = None  # 输出目录
        self._output_dir_is_manual: bool = False  # 用户是否手动指定了输出目录
        self._rotation: int = 0  # 当前旋转角度（0/90/180/270）
        self._mask_path: Optional[Path] = None  # 蒙版 PNG 路径

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 文件选择组
        file_group = QGroupBox(self.tr.tr("file_list"))
        file_layout = QVBoxLayout()

        # 文件选择按钮 + 最近目录按钮
        folder_btn_layout = QHBoxLayout()

        self.btn_select_folder = QPushButton(self.tr.tr('select_directory'))
        self.btn_select_folder.clicked.connect(self.select_folder)
        self.btn_select_folder.setToolTip(self.tr.tr('tooltip_select_folder'))
        self.btn_select_folder.setStyleSheet(PRIMARY_BUTTON_STYLE)
        folder_btn_layout.addWidget(self.btn_select_folder, 1)

        self.btn_recent_dirs = QToolButton()
        self.btn_recent_dirs.setText("🕒")
        self.btn_recent_dirs.setToolTip("最近使用的目录")
        self.btn_recent_dirs.setPopupMode(QToolButton.InstantPopup)
        self.btn_recent_dirs.setStyleSheet(SECONDARY_BUTTON_STYLE + "padding: 6px 10px;")
        self._recent_menu = QMenu(self)
        self.btn_recent_dirs.setMenu(self._recent_menu)
        self._refresh_recent_menu()
        folder_btn_layout.addWidget(self.btn_recent_dirs)

        file_layout.addLayout(folder_btn_layout)

        # 输出目录选择
        output_dir_layout = QHBoxLayout()
        self.btn_select_output = QPushButton(self.tr.tr('select_output_directory'))
        self.btn_select_output.clicked.connect(self.select_output_dir)
        self.btn_select_output.setToolTip(
            self.tr.tr('tooltip_output_dir') if hasattr(self.tr, 'tr') else "Select output directory"
        )
        self.btn_select_output.setStyleSheet(SECONDARY_BUTTON_STYLE)
        output_dir_layout.addWidget(self.btn_select_output)

        self.label_output_dir = QLabel(self.tr.tr("no_output_directory_selected"))
        self.label_output_dir.setWordWrap(True)
        self.label_output_dir.setStyleSheet(INFO_LABEL_STYLE)
        output_dir_layout.addWidget(self.label_output_dir, 1)

        file_layout.addLayout(output_dir_layout)

        # 旋转设置
        rotation_layout = QHBoxLayout()
        rotation_label = QLabel("旋转:")
        rotation_layout.addWidget(rotation_label)
        self.combo_rotation = QComboBox()
        self.combo_rotation.addItems(["不旋转", "顺时针 90°", "180°", "逆时针 90°"])
        self.combo_rotation.setToolTip("对目录内所有图片统一旋转，用于竖拍素材")
        self.combo_rotation.currentIndexChanged.connect(self._on_rotation_changed)
        rotation_layout.addWidget(self.combo_rotation, 1)
        file_layout.addLayout(rotation_layout)

        # 蒙版选择
        mask_layout = QHBoxLayout()
        self.btn_select_mask = QPushButton("选择蒙版 PNG")
        self.btn_select_mask.setToolTip("选择 Photoshop 导出的天空蒙版（白=天空，黑=地景）")
        self.btn_select_mask.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.btn_select_mask.clicked.connect(self.select_mask)
        mask_layout.addWidget(self.btn_select_mask)

        self.btn_clear_mask = QPushButton("清除")
        self.btn_clear_mask.setToolTip("移除蒙版，恢复单轨堆栈")
        self.btn_clear_mask.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.btn_clear_mask.setEnabled(False)
        self.btn_clear_mask.clicked.connect(self.clear_mask)
        mask_layout.addWidget(self.btn_clear_mask)

        self.label_mask = QLabel("未选择蒙版")
        self.label_mask.setWordWrap(True)
        self.label_mask.setStyleSheet(INFO_LABEL_STYLE)
        mask_layout.addWidget(self.label_mask, 1)

        file_layout.addLayout(mask_layout)

        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.itemClicked.connect(self._on_file_clicked)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        file_layout.addWidget(self.file_list)

        # 文件计数标签
        self.label_file_count = QLabel(self.tr.tr("files_selected").format(count=0))
        self.label_file_count.setStyleSheet(INFO_LABEL_STYLE)
        file_layout.addWidget(self.label_file_count)

        # 打开输出目录按钮（底部）
        self.btn_open_output = QPushButton(self.tr.tr('open_output_dir'))
        self.btn_open_output.clicked.connect(self._on_open_output_clicked)
        self.btn_open_output.setEnabled(False)
        self.btn_open_output.setStyleSheet(SECONDARY_BUTTON_STYLE + "padding: 8px 16px;")
        file_layout.addWidget(self.btn_open_output)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

    def _refresh_recent_menu(self):
        """刷新最近目录菜单"""
        self._recent_menu.clear()
        recent_dirs = get_settings().get_recent_dirs()
        # 过滤掉不存在的目录
        recent_dirs = [d for d in recent_dirs if Path(d).exists()]
        if not recent_dirs:
            action = self._recent_menu.addAction("暂无最近目录")
            action.setEnabled(False)
        else:
            for path in recent_dirs:
                display = Path(path).name or path
                action = self._recent_menu.addAction(display)
                action.setToolTip(path)
                action.triggered.connect(lambda checked, p=path: self._load_folder(p))

    def select_folder(self):
        """选择包含图片文件的文件夹"""
        folder = QFileDialog.getExistingDirectory(self, self.tr.tr("select_directory"))
        if not folder:
            return
        self._load_folder(folder)

    def _load_folder(self, folder: str):
        """从指定路径加载图片文件"""
        folder_path = Path(folder)
        
        # 定义支持的扩展名
        raw_extensions = {'.cr2', '.nef', '.arw', '.dng', '.orf', '.rw2', '.raf', '.crw', '.cr3'}
        jpg_extensions = {'.jpg', '.jpeg'}
        
        # 扫描文件夹中的文件（排除隐藏文件）
        all_files = [f for f in folder_path.iterdir() if f.is_file() and not f.name.startswith('.')]
        
        # 分类 RAW 和 JPG 文件
        raw_files = sorted([f for f in all_files if f.suffix.lower() in raw_extensions])
        jpg_files = sorted([f for f in all_files if f.suffix.lower() in jpg_extensions])
        
        # 获取文件名前缀（不含扩展名）
        raw_stems = {f.stem for f in raw_files}
        jpg_stems = {f.stem for f in jpg_files}
        
        # 检查是否有同名对
        common_stems = raw_stems & jpg_stems
        
        if common_stems:
            # 有同名的 RAW+JPG 文件，让用户选择
            from PyQt5.QtWidgets import QMessageBox
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(
                self.tr.tr("choose_format_title") if hasattr(self.tr, 'tr') else "选择文件格式"
            )
            msg_box.setText(
                self.tr.tr("choose_format_message") if hasattr(self.tr, 'tr') 
                else f"检测到 {len(common_stems)} 对同名的 RAW 和 JPG 文件，请选择使用哪种格式："
            )
            msg_box.setIcon(QMessageBox.Question)
            
            btn_raw = msg_box.addButton(
                self.tr.tr("use_raw") if hasattr(self.tr, 'tr') else "使用 RAW",
                QMessageBox.AcceptRole
            )
            btn_jpg = msg_box.addButton(
                self.tr.tr("use_jpg") if hasattr(self.tr, 'tr') else "使用 JPG",
                QMessageBox.AcceptRole
            )
            
            msg_box.exec_()
            
            if msg_box.clickedButton() == btn_raw:
                files = raw_files
            else:
                files = jpg_files
        else:
            # 没有同名对，合并所有文件
            if raw_files and jpg_files:
                # 两种格式都有但没有同名，合并使用
                files = sorted(raw_files + jpg_files, key=lambda x: x.name)
            elif raw_files:
                files = raw_files
            elif jpg_files:
                files = jpg_files
            else:
                files = []

        if not files:
            QMessageBox.warning(
                self,
                self.tr.tr("warning") if hasattr(self.tr, 'tr') else "警告",
                self.tr.tr("no_image_files") if hasattr(self.tr, 'tr') else "所选文件夹中没有找到支持的图片文件（RAW 或 JPG）"
            )
            return

        # 更新文件列表
        self.raw_files = files
        self.excluded_files.clear()  # 清空排除列表
        self.refresh_file_list()

        # 新文件夹重置旋转
        self._rotation = 0
        self.combo_rotation.blockSignals(True)
        self.combo_rotation.setCurrentIndex(0)
        self.combo_rotation.blockSignals(False)

        # 若用户未手动指定输出目录，每次切换源文件夹时自动跟随更新
        if not self._output_dir_is_manual:
            self.output_dir = str(Path(folder) / "SuperStarTrail")
            self._update_output_dir_label()
            self.output_dir_changed.emit(self.output_dir)

        # 保存到最近目录并刷新菜单
        get_settings().add_recent_dir(str(folder))
        self._refresh_recent_menu()

        # 发射信号
        self.files_selected.emit(self.get_files_to_process())

        # 自动预览第一张图片
        if self.raw_files:
            self.file_clicked.emit(self.raw_files[0])

    def select_output_dir(self):
        """选择输出目录"""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr.tr("select_output_directory") if hasattr(self.tr, 'tr') else "选择输出目录",
            self.output_dir or str(Path.home())
        )

        if folder:
            self.output_dir = folder
            self._output_dir_is_manual = True
            self._update_output_dir_label()
            self.output_dir_changed.emit(self.output_dir)

    def _update_output_dir_label(self):
        """更新输出目录标签文本"""
        if self.output_dir:
            self.label_output_dir.setText(
                self.tr.tr("output_to").format(path=self.output_dir)
            )
        else:
            self.label_output_dir.setText(
                self.tr.tr("no_output_directory_selected")
            )

    def refresh_file_list(self):
        """刷新文件列表显示"""
        self.file_list.clear()

        for i, file_path in enumerate(self.raw_files):
            item_text = file_path.name
            if i in self.excluded_files:
                item_text = f"🚫 {item_text}"  # 被排除的文件显示禁止符号
            self.file_list.addItem(item_text)

        self.update_file_count_label()

    def update_file_count_label(self):
        """更新文件计数标签"""
        total_files = len(self.raw_files)
        excluded_count = len(self.excluded_files)
        valid_count = total_files - excluded_count

        if excluded_count > 0:
            count_text = self.tr.tr("files_selected_with_excluded").format(
                count=valid_count,
                active=valid_count,
                excluded=excluded_count
            ) if hasattr(self.tr, 'tr') else f"已选择 {valid_count}/{total_files} 个文件（{excluded_count} 个已排除）"
        else:
            count_text = self.tr.tr("files_selected").format(count=valid_count)

        self.label_file_count.setText(count_text)

    def show_context_menu(self, position):
        """显示文件列表右键菜单"""
        if not self.raw_files:
            return

        selected_indices = [item.row() for item in self.file_list.selectedIndexes()]
        if not selected_indices:
            return

        menu = QMenu(self)

        # 检查选中的文件是否都已被排除
        all_excluded = all(i in self.excluded_files for i in selected_indices)

        if all_excluded:
            # 如果已排除，显示"取消排除"
            action = menu.addAction(
                self.tr.tr("include_files") if hasattr(self.tr, 'tr') else "取消排除"
            )
            action.triggered.connect(lambda: self.toggle_file_exclusion(selected_indices, False))
        else:
            # 显示"排除"
            action = menu.addAction(
                self.tr.tr("exclude_files") if hasattr(self.tr, 'tr') else "排除"
            )
            action.triggered.connect(lambda: self.toggle_file_exclusion(selected_indices, True))

        menu.exec_(self.file_list.viewport().mapToGlobal(position))

    def toggle_file_exclusion(self, indices: List[int], exclude: bool):
        """切换文件的排除状态"""
        for i in indices:
            if exclude:
                self.excluded_files.add(i)
            else:
                self.excluded_files.discard(i)

        self.refresh_file_list()

        # 发射信号通知文件列表已更改
        self.files_selected.emit(self.get_files_to_process())

    def get_files_to_process(self) -> List[Path]:
        """获取需要处理的文件列表（排除已被排除的文件）"""
        return [
            file for i, file in enumerate(self.raw_files)
            if i not in self.excluded_files
        ]

    def get_all_files(self) -> List[Path]:
        """获取所有文件列表（包括已被排除的）"""
        return self.raw_files.copy()

    def get_output_dir(self) -> Optional[str]:
        """获取输出目录"""
        return self.output_dir

    def get_rotation(self) -> int:
        """获取当前旋转角度（0/90/180/270）"""
        return self._rotation

    def _on_rotation_changed(self, index: int):
        """旋转下拉框改变时更新状态并通知预览"""
        angle_map = {0: 0, 1: 90, 2: 180, 3: 270}
        self._rotation = angle_map[index]
        self.rotation_changed.emit(self._rotation)
        # 刷新当前预览图
        if self.raw_files:
            self.file_clicked.emit(self.raw_files[0])

    def has_files(self) -> bool:
        """检查是否有可处理的文件"""
        return len(self.get_files_to_process()) > 0

    def set_open_output_enabled(self, enabled: bool):
        """设置打开输出目录按钮是否可用"""
        self.btn_open_output.setEnabled(enabled)

    def _on_open_output_clicked(self):
        """打开输出目录按钮点击"""
        self.open_output_clicked.emit()

    def _on_file_clicked(self, item):
        """文件列表项被点击"""
        # 获取点击的文件索引
        index = self.file_list.row(item)
        if 0 <= index < len(self.raw_files):
            # 发射信号，传递文件路径
            self.file_clicked.emit(self.raw_files[index])

    def select_mask(self):
        """选择蒙版 PNG 文件"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择蒙版 PNG 文件",
            str(self._mask_path.parent) if self._mask_path else str(Path.home()),
            "PNG 文件 (*.png)"
        )
        if path:
            self._mask_path = Path(path)
            self.label_mask.setText(self._mask_path.name)
            self.btn_clear_mask.setEnabled(True)
            self.mask_path_changed.emit(self._mask_path)

    def clear_mask(self):
        """清除蒙版"""
        self._mask_path = None
        self.label_mask.setText("未选择蒙版")
        self.btn_clear_mask.setEnabled(False)
        self.mask_path_changed.emit(None)

    def get_mask_path(self) -> Optional[Path]:
        """获取当前蒙版路径（无蒙版返回 None）"""
        return self._mask_path
