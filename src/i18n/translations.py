"""
翻译文本定义
"""

TRANSLATIONS = {
    # 简体中文
    "zh_CN": {
        # 窗口标题
        "app_name": "彗星星轨",
        "preview": "预览",

        # 文件选择区域
        "select_directory": "选择目录",
        "select_output_directory": "选择输出目录",
        "selected_directory": "已选择目录",
        "no_directory_selected": "未选择目录",
        "no_output_directory_selected": "未选择输出目录",
        "file_list": "文件列表",
        "drop_files_here": "拖放 RAW 文件到此处\n或点击上方按钮选择目录",

        # 参数设置
        "parameters": "参数设置",
        "stack_mode": "堆栈模式:",
        "mode_lighten": "Lighten (星轨)",
        "mode_comet": "Comet (彗星)",
        "mode_average": "Average (降噪)",
        "mode_darken": "Darken (去光污)",

        "comet_tail": "尾巴长度:",
        "tail_short": "短",
        "tail_medium": "中",
        "tail_long": "长",

        "brightness_stretch": "亮度拉伸:",
        "stretch_none": "无",
        "stretch_auto": "自动",
        "stretch_custom": "自定义",

        "gap_filling": "间隔填充",
        "gap_filling_checked": "✓ 间隔填充",
        "timelapse_video": "延时视频",
        "timelapse_checked": "✓ 延时视频",

        "white_balance": "白平衡:",
        "wb_camera": "相机",
        "wb_daylight": "日光",
        "wb_auto": "自动",
        "wb_manual": "手动色温",
        "color_temperature": "色温:",

        # 文件计数和目录
        "files_selected": "已选择 {count} 个文件",
        "files_selected_with_excluded": "已选择 {count} 个文件 ({active} 参与合成, {excluded} 已排除)",
        "output_to": "输出：{path}",
        "default_output": "默认：原片目录/StarTrail/",
        "tooltip_output_dir": "选择保存星轨照片和视频的目录\n默认：原片目录/StarTrail/",

        # 文件格式选择
        "choose_format_title": "选择文件格式",
        "choose_format_message": "检测到同名的 RAW 和 JPG 文件，请选择使用哪种格式：",
        "use_raw": "使用 RAW",
        "use_jpg": "使用 JPG",
        "no_image_files": "所选文件夹中没有找到支持的图片文件（RAW 或 JPG）",

        # 文件排除功能
        "exclude_from_stacking": "❌ 排除出星轨合成",
        "include_in_stacking": "✅ 恢复到星轨合成",
        "excluded_file_tooltip": "此文件已被排除，不会参与星轨合成",
        "all_files_excluded": "所有文件都已被排除，无法进行处理",
        "warning": "警告",

        # 菜单
        "menu_file": "文件(&F)",
        "menu_open_folder": "打开图片目录...(&O)",
        "menu_select_output": "选择输出目录...(&D)",
        "menu_exit": "退出(&Q)",

        "menu_edit": "编辑(&E)",
        "menu_preferences": "偏好设置...(&P)",

        "menu_process": "处理(&P)",
        "menu_start": "开始处理(&S)",
        "menu_stop": "停止处理(&T)",
        "menu_save": "保存结果...(&V)",

        "menu_window": "窗口(&W)",
        "menu_minimize": "最小化(&M)",
        "menu_zoom": "缩放(&Z)",

        "menu_help": "帮助(&H)",
        "menu_guide": "使用指南(&G)",
        "menu_about": "关于 彗星星轨(&A)",

        # 控制按钮
        "start": "✨ 开始合成",
        "stop": "⏹ 停止",
        "ready": "✓ 就绪",
        "processing": "⏳ 处理中 - 预计剩余: {time}",
        "completed": "✅ 合成完成",
        "failed": "❌ 处理失败",
        "error": "❌ 合成完成但保存失败",

        # 状态消息
        "loading_preview": "正在加载预览: {filename}",
        "preview_file": "预览: {filename}",
        "preview_failed": "预览失败: {error}",
        "preparing": "准备开始...",
        "processing_images": "开始处理 {total} 张图片...",

        # 日志消息
        "log_start_stacking": "开始星轨合成",
        "log_file_count": "文件数量: {count}",
        "log_stack_mode": "堆栈模式: {mode}",
        "log_white_balance": "白平衡: {wb}",
        "log_alignment": "图像对齐: {status}",
        "log_gap_filling": "间隔填充: {status}",
        "log_gap_method": "填充方法: {method}, 间隔大小: {size}",
        "log_timelapse": "延时视频: {status}",
        "log_total_time": "总耗时: {time:.2f} 秒",
        "log_avg_speed": "平均速度: {speed:.2f} 秒/张",
        "log_applying_gap_fill": "正在应用间隔填充...",
        "log_gap_fill_done": "间隔填充完成，耗时: {time:.2f} 秒",
        "log_generating_video": "正在生成延时视频...",
        "log_video_saved": "视频保存至: {filename}",
        "log_video_done": "延时视频生成完成，耗时: {time:.2f} 秒",
        "log_video_path": "视频保存至: {path}",
        "log_video_failed": "延时视频生成失败",
        "status_generating_video": "正在生成延时视频...",
        "enabled": "启用",
        "disabled": "禁用",
        "log_output_dir": "输出目录: {path}",
        "log_comet_mode": "彗星模式: 衰减因子 = {factor}",
        "user_cancelled": "用户取消处理",
        "log_update_preview": "更新预览 ({current}/{total})",
        "log_processing_failed": "处理失败: {error}",
        "log_complete_saved": "合成完成！文件已保存到: {path}",

        # 输出控制
        "output_controls": "输出控制",
        "play_video": "▶ 播放视频",
        "open_output_dir": "📁 打开输出目录",

        # 进度信息
        "progress": "进度",
        "progress_text": "{current}/{total} 张图片",

        # 处理日志
        "processing_log": "处理日志",

        # 设置窗口
        "settings": "设置",
        "language": "语言:",
        "language_zh": "简体中文",
        "language_en": "English",
        "video_fps": "延时视频帧率:",
        "fps": "fps",
        "stretch_lower": "拉伸下限 (%):",
        "stretch_upper": "拉伸上限 (%):",
        "restart_required": "语言设置将在重启应用后生效",

        # 对话框
        "dialog_complete_title": "完成",
        "dialog_complete_msg": "星轨合成完成！\n\n文件已保存至:\n{path}",
        "dialog_warning_title": "警告",
        "dialog_warning_msg": "星轨合成完成，但保存文件失败",
        "dialog_error_title": "错误",
        "dialog_error_msg": "处理失败:\n{error}",

        # 工具提示
        "tooltip_select_folder": "选择包含星轨照片的文件夹\n支持格式：RAW (CR2, NEF, ARW等)、TIFF、JPG、PNG",
        "tooltip_comet_tail": "控制彗星尾巴的长度\n短: 快速衰减\n中: 中等衰减\n长: 缓慢衰减",
        "tooltip_brightness": "自动拉伸图像亮度范围以增强对比度",
        "tooltip_gap_filling": "使用形态学算法填充星轨间的断点，产生连续星轨效果",
        "tooltip_timelapse": "生成星轨堆栈过程的延时视频（MP4格式）",

        # 对话框按钮
        "button_ok": "确定",
        "button_cancel": "取消",
        "button_close": "关闭",

        # 消息对话框
        "msg_complete_title": "完成",
        "msg_complete_text": "星轨合成完成！\n\n文件已保存至:\n{path}",
        "msg_save_failed_title": "警告",
        "msg_save_failed_text": "星轨合成完成，但保存文件失败",
        "msg_error_title": "错误",
        "msg_error_text": "处理失败:\n{error}",
        "msg_no_output_dir": "输出目录不存在",
        "msg_no_video_file": "延时视频文件不存在",
        "msg_no_result": "没有可保存的结果\n请先处理图片",
        "msg_save_success": "文件已保存至:\n{path}",
        "msg_save_error": "保存文件失败",
        "msg_save_exception": "保存文件时出错:\n{error}",

        # 关于窗口
        "about": "关于",
        "version": "版本",
        "description": "专业的星轨堆栈软件，支持多种堆栈模式和高级功能。",
        "features": "主要功能",
        "feature_modes": "多种堆栈模式：传统星轨、彗星效果、平均降噪、去除光污染",
        "feature_comet": "彗星模式：可调节尾巴长度",
        "feature_brightness": "亮度拉伸：自动或自定义拉伸",
        "feature_gap": "间隔填充：形态学算法填补星轨断点",
        "feature_timelapse": "延时视频：自动生成堆栈过程视频",
        "feature_preview": "实时预览：单击文件即可预览",

        # 帮助文档
        "help_title": "使用说明",
        "help_step1_title": "1. 选择文件",
        "help_step1_content": "点击「📁 选择目录」按钮，选择包含星轨照片的文件夹。<br>支持格式：RAW (CR2, NEF, ARW, DNG等)、TIFF、JPG、PNG。",

        "help_step2_title": "2. 选择堆栈模式",
        "help_step2_content": """• <b>Lighten (星轨)</b>：传统的星轨叠加效果，保留每张照片中最亮的像素<br>
• <b>Comet (彗星)</b>：创造渐变尾巴效果，模拟彗星划过天空<br>
• <b>Average (降噪)</b>：平均多张照片的像素值，用于降噪和拍摄静态场景<br>
• <b>Darken (去光污)</b>：保留最暗的像素，可用于去除光污染""",

        "help_step3_title": "3. 调整参数",
        "help_step3_content": """• <b>彗星尾巴长度</b>：短(0.96)/中(0.97)/长(0.98)，控制尾巴的衰减速度<br>
• <b>亮度拉伸</b>：<br>
  - 无：不进行拉伸<br>
  - 自动：自动调整亮度范围以增强对比度<br>
  - 自定义：在设置中手动指定拉伸上下限<br>
• <b>间隙填充</b>：使用形态学算法填补星轨间的断点，产生连续轨迹<br>
• <b>延时视频</b>：生成展示星轨形成过程的视频（MP4格式）<br>
• <b>白平衡</b>：选择相机、日光、自动或 RAW 手动色温""",

        "help_step4_title": "4. 选择输出目录（可选）",
        "help_step4_content": "点击「💾 输出目录」选择保存位置。<br>默认保存到：原片目录/StarTrail/",

        "help_step5_title": "5. 开始处理",
        "help_step5_content": "点击「🚀 开始」按钮开始处理。<br>处理过程中可以在预览窗口查看实时进度。<br>完成后会显示「✅ 合成完成」。",

        "help_tips_title": "💡 使用技巧",
        "help_tips_content": """• 推荐使用 RAW 格式以获得最佳画质和后期空间<br>
• 彗星模式「中」尾巴长度适合大多数场景<br>
• 启用亮度拉伸可以增强暗部细节和整体对比度<br>
• 间隙填充适合拍摄间隔较大的星轨序列<br>
• 延时视频会增加约 30-60 秒的处理时间<br>
• 100 张照片约生成 4 秒视频（25fps）""",

        "help_output_title": "📁 输出文件",
        "help_output_content": """• 星轨图片：StarTrail_YYYYMMDD_HHMMSS.jpg/tif<br>
• 延时视频：StarTrail_Timelapse_YYYYMMDD_HHMMSS.mp4<br>
• 处理完成后可点击「📁 打开输出目录」查看结果""",
    },

    # English
    "en_US": {
        # Window titles
        "app_name": "Comet Star Trail",
        "preview": "Preview",

        # File selection
        "select_directory": "Select Directory",
        "select_output_directory": "Select Output Directory",
        "selected_directory": "Selected Directory",
        "no_directory_selected": "No Directory Selected",
        "no_output_directory_selected": "No Output Directory Selected",
        "file_list": "File List",
        "drop_files_here": "Drop RAW files here\nor click button above to select directory",

        # Parameters
        "parameters": "Parameters",
        "stack_mode": "Stack Mode:",
        "mode_lighten": "Lighten (Star Trail)",
        "mode_comet": "Comet",
        "mode_average": "Average (Denoise)",
        "mode_darken": "Darken (Light Pollution)",

        "comet_tail": "Tail Length:",
        "tail_short": "Short",
        "tail_medium": "Medium",
        "tail_long": "Long",

        "brightness_stretch": "Brightness Stretch:",
        "stretch_none": "None",
        "stretch_auto": "Auto",
        "stretch_custom": "Custom",

        "gap_filling": "Gap Filling",
        "gap_filling_checked": "✓ Gap Filling",
        "timelapse_video": "Timelapse Video",
        "timelapse_checked": "✓ Timelapse Video",

        "white_balance": "White Balance:",
        "wb_camera": "Camera",
        "wb_daylight": "Daylight",
        "wb_auto": "Auto",
        "wb_manual": "Manual Temperature",
        "color_temperature": "Temperature:",

        # File count and directories
        "files_selected": "{count} files selected",
        "files_selected_with_excluded": "{count} files selected ({active} active, {excluded} excluded)",
        "output_to": "Output: {path}",
        "default_output": "Default: Source dir/StarTrail/",
        "tooltip_output_dir": "Select directory to save star trail photos and videos\nDefault: Source dir/StarTrail/",

        # File format selection
        "choose_format_title": "Choose File Format",
        "choose_format_message": "Detected RAW and JPG files with same names. Please choose which format to use:",
        "use_raw": "Use RAW",
        "use_jpg": "Use JPG",
        "no_image_files": "No supported image files found in the selected folder (RAW or JPG)",

        # File exclusion feature
        "exclude_from_stacking": "❌ Exclude from Stacking",
        "include_in_stacking": "✅ Include in Stacking",
        "excluded_file_tooltip": "This file is excluded and will not be used in stacking",
        "all_files_excluded": "All files are excluded, cannot proceed with processing",
        "warning": "Warning",

        # Menus
        "menu_file": "&File",
        "menu_open_folder": "&Open Image Directory...",
        "menu_select_output": "Select Output &Directory...",
        "menu_exit": "&Quit",

        "menu_edit": "&Edit",
        "menu_preferences": "&Preferences...",

        "menu_process": "&Process",
        "menu_start": "&Start Processing",
        "menu_stop": "S&top Processing",
        "menu_save": "Sa&ve Result...",

        "menu_window": "&Window",
        "menu_minimize": "&Minimize",
        "menu_zoom": "&Zoom",

        "menu_help": "&Help",
        "menu_guide": "User &Guide",
        "menu_about": "&About Comet Star Trail",

        # Control buttons
        "start": "✨ Start Processing",
        "stop": "⏹ Stop",
        "ready": "✓ Ready",
        "processing": "⏳ Processing - ETA: {time}",
        "completed": "✅ Completed",
        "failed": "❌ Failed",
        "error": "❌ Completed with Save Error",

        # Status messages
        "loading_preview": "Loading preview: {filename}",
        "preview_file": "Preview: {filename}",
        "preview_failed": "Preview failed: {error}",
        "preparing": "Preparing...",
        "processing_images": "Processing {total} images...",

        # Log messages
        "log_start_stacking": "Starting star trail stacking",
        "log_file_count": "File count: {count}",
        "log_stack_mode": "Stack mode: {mode}",
        "log_white_balance": "White balance: {wb}",
        "log_alignment": "Image alignment: {status}",
        "log_gap_filling": "Gap filling: {status}",
        "log_gap_method": "Fill method: {method}, gap size: {size}",
        "log_timelapse": "Timelapse video: {status}",
        "log_total_time": "Total time: {time:.2f} sec",
        "log_avg_speed": "Average speed: {speed:.2f} sec/image",
        "log_applying_gap_fill": "Applying gap filling...",
        "log_gap_fill_done": "Gap filling completed, time: {time:.2f} sec",
        "log_generating_video": "Generating timelapse video...",
        "log_video_saved": "Video saved as: {filename}",
        "log_video_done": "Timelapse video completed, time: {time:.2f} sec",
        "log_video_path": "Video saved to: {path}",
        "log_video_failed": "Timelapse video generation failed",
        "status_generating_video": "Generating timelapse video...",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "log_output_dir": "Output directory: {path}",
        "log_comet_mode": "Comet mode: fade factor = {factor}",
        "user_cancelled": "User cancelled processing",
        "log_update_preview": "Update preview ({current}/{total})",
        "log_processing_failed": "Processing failed: {error}",
        "log_complete_saved": "Stacking completed! Files saved to: {path}",

        # Output controls
        "output_controls": "Output Controls",
        "play_video": "▶ Play Video",
        "open_output_dir": "📁 Open Output Directory",

        # Progress
        "progress": "Progress",
        "progress_text": "{current}/{total} Images",

        # Processing log
        "processing_log": "Processing Log",

        # Settings window
        "settings": "Settings",
        "language": "Language:",
        "language_zh": "简体中文",
        "language_en": "English",
        "video_fps": "Timelapse Video FPS:",
        "fps": "fps",
        "stretch_lower": "Stretch Lower (%):",
        "stretch_upper": "Stretch Upper (%):",
        "restart_required": "Language changes will take effect after restarting the app",

        # Dialogs
        "dialog_complete_title": "Complete",
        "dialog_complete_msg": "Star trail stacking completed!\n\nFiles saved to:\n{path}",
        "dialog_warning_title": "Warning",
        "dialog_warning_msg": "Star trail stacking completed, but failed to save files",
        "dialog_error_title": "Error",
        "dialog_error_msg": "Processing failed:\n{error}",

        # Tooltips
        "tooltip_select_folder": "Select folder containing star trail photos\nSupported formats: RAW (CR2, NEF, ARW, etc.), TIFF, JPG, PNG",
        "tooltip_comet_tail": "Control comet tail length\nShort: Fast decay\nMedium: Medium decay\nLong: Slow decay",
        "tooltip_brightness": "Automatically stretch image brightness range to enhance contrast",
        "tooltip_gap_filling": "Fill gaps in star trails using morphological algorithms for continuous trails",
        "tooltip_timelapse": "Generate timelapse video (MP4) of the stacking process",

        # Dialog buttons
        "button_ok": "OK",
        "button_cancel": "Cancel",
        "button_close": "Close",

        # Message dialogs
        "msg_complete_title": "Complete",
        "msg_complete_text": "Star trail stacking completed!\n\nFiles saved to:\n{path}",
        "msg_save_failed_title": "Warning",
        "msg_save_failed_text": "Star trail stacking completed, but failed to save files",
        "msg_error_title": "Error",
        "msg_error_text": "Processing failed:\n{error}",
        "msg_no_output_dir": "Output directory does not exist",
        "msg_no_video_file": "Timelapse video file does not exist",
        "msg_no_result": "No result to save\nPlease process images first",
        "msg_save_success": "File saved to:\n{path}",
        "msg_save_error": "Failed to save file",
        "msg_save_exception": "Error occurred while saving file:\n{error}",

        # About window
        "about": "About",
        "version": "Version",
        "description": "Professional star trail stacking software with multiple modes and advanced features.",
        "features": "Key Features",
        "feature_modes": "Multiple stacking modes: Traditional, Comet, Average, Darken",
        "feature_comet": "Comet mode with adjustable tail length",
        "feature_brightness": "Brightness stretch: Auto or custom",
        "feature_gap": "Gap filling: Morphological algorithm for seamless trails",
        "feature_timelapse": "Timelapse video: Auto-generate stacking process video",
        "feature_preview": "Live preview: Click file to preview",

        # Help documentation
        "help_title": "User Guide",
        "help_step1_title": "1. Select Files",
        "help_step1_content": "Click the '📁 Select Directory' button and choose a folder containing star trail photos.<br>Supported formats: RAW (CR2, NEF, ARW, DNG, etc.), TIFF, JPG, PNG.",

        "help_step2_title": "2. Choose Stack Mode",
        "help_step2_content": """• <b>Lighten (Star Trail)</b>: Traditional star trail effect, keeps the brightest pixels from each image<br>
• <b>Comet</b>: Creates a gradient tail effect, simulating a comet passing through the sky<br>
• <b>Average (Denoise)</b>: Averages pixel values across images for noise reduction and static scenes<br>
• <b>Darken (Light Pollution)</b>: Keeps the darkest pixels, useful for removing light pollution""",

        "help_step3_title": "3. Adjust Parameters",
        "help_step3_content": """• <b>Comet Tail Length</b>: Short(0.96)/Medium(0.97)/Long(0.98), controls tail fade speed<br>
• <b>Brightness Stretch</b>:<br>
  - None: No stretching applied<br>
  - Auto: Automatically adjusts brightness range to enhance contrast<br>
  - Custom: Manually specify stretch limits in settings<br>
• <b>Gap Filling</b>: Uses morphological algorithms to fill gaps in star trails for continuous tracks<br>
• <b>Timelapse Video</b>: Generates a video (MP4) showing the stacking process<br>
• <b>White Balance</b>: Choose Camera, Daylight, or Auto white balance""",

        "help_step4_title": "4. Select Output Directory (Optional)",
        "help_step4_content": "Click '💾 Output Directory' to choose save location.<br>Default: Source directory/StarTrail/",

        "help_step5_title": "5. Start Processing",
        "help_step5_content": "Click the '🚀 Start' button to begin processing.<br>You can monitor real-time progress in the preview window.<br>When complete, '✅ Completed' will be displayed.",

        "help_tips_title": "💡 Tips",
        "help_tips_content": """• Recommended to use RAW format for best quality and post-processing flexibility<br>
• Comet mode 'Medium' tail length works well for most scenarios<br>
• Enable brightness stretch to enhance shadow details and overall contrast<br>
• Gap filling is ideal for star trail sequences with large shooting intervals<br>
• Timelapse video adds approximately 30-60 seconds to processing time<br>
• 100 photos generate approximately 4 seconds of video (25fps)""",

        "help_output_title": "📁 Output Files",
        "help_output_content": """• Star trail image: StarTrail_YYYYMMDD_HHMMSS.jpg/tif<br>
• Timelapse video: StarTrail_Timelapse_YYYYMMDD_HHMMSS.mp4<br>
• Click '📁 Open Output Directory' to view results after completion""",
    }
}
