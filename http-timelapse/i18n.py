DEFAULT_LANGUAGE = "en"

LANG_ATTRS = {"en": "en", "zh": "zh-Hans"}

STRINGS = {
    "en": {
        "text": {
            "gallery_title": "Timelapse",
            "capture_all": "Capture all now",
            "reload": "Refresh",
            "settings_link": "Settings",
            "no_sources": "No capture sources configured yet. Add them on the app configuration page.",
            "latest_capture": "Latest capture",
            "capture_now": "Capture now",
            "directory_outside_root": "Folder is outside the gallery root",
            "settings_title": "Timelapse - Settings",
            "settings_heading": "Capture schedule",
            "back_to_gallery": "Back to gallery",
            "settings_notice": "Pick the daily capture times for each source (multiple entries allowed). "
            "Saving restarts the app automatically; edit the other options on the app configuration page.",
            "save_restart": "Save and restart",
            "interval_note": "Capture interval: {minutes} min (edit on the app configuration page)",
            "add_time": "Add time",
            "remove": "Remove",
            "browse_suffix": "Captures",
            "back_to_home": "Back to home",
            "total_count": "{count} items",
            "view_grid": "Grid",
            "view_list": "List",
            "sort_label": "Sort",
            "per_page_label": "Per page",
            "per_page_option": "{size}",
            "per_page_all": "All",
            "sort_time_desc": "Time: newest first",
            "sort_time_asc": "Time: oldest first",
            "sort_name_asc": "File name: A → Z",
            "sort_name_desc": "File name: Z → A",
            "sort_size_desc": "Size: largest first",
            "sort_size_asc": "Size: smallest first",
            "latest_heading": "Latest capture",
            "column_name": "File name",
            "column_time": "Captured",
            "column_size": "Size",
            "empty_items": "No captures yet.",
            "pagination_first": "First",
            "pagination_prev": "Previous",
            "pagination_next": "Next",
            "pagination_last": "Last",
            "pagination_info": "Page {page} / {pages}",
            "lightbox_close": "Close",
            "lightbox_prev": "Previous image",
            "lightbox_next": "Next image",
            "lightbox_original": "Open original in a new tab",
        },
        "js": {
            "saved_prefix": "Saved ",
            "failed_prefix": "Failed: ",
            "unknown_error": "unknown error",
            "capturing": "Capturing…",
            "request_failed_prefix": "Request failed: ",
            "done_prefix": "Done ",
            "waiting_restart": "Restart timed out, refresh the page manually",
            "confirm_empty_before": "These sources have no daily times and no interval and will stop capturing automatically: ",
            "confirm_empty_after": ". Save anyway?",
            "list_separator": ", ",
            "saving": "Saving…",
            "save_failed_prefix": "Save failed: ",
            "saved_restarting": "Saved, restarting the app…",
            "saved_manual": "Saved, restart the app manually to apply",
        },
    },
    "zh": {
        "text": {
            "gallery_title": "延时摄影",
            "capture_all": "全部立即抓拍",
            "reload": "刷新",
            "settings_link": "设置",
            "no_sources": "还没有配置抓拍源，请在应用配置中添加。",
            "latest_capture": "最近抓拍",
            "capture_now": "立即抓拍",
            "directory_outside_root": "目录不在浏览根目录下",
            "settings_title": "延时摄影 - 设置",
            "settings_heading": "抓拍时间设置",
            "back_to_gallery": "返回浏览",
            "settings_notice": "为每个源选择每日抓拍时间点（可添加多个）。保存后应用会自动重启以生效；其他参数请在应用配置页修改。",
            "save_restart": "保存并重启",
            "interval_note": "抓拍间隔: {minutes} 分钟（在应用配置页修改）",
            "add_time": "添加时间点",
            "remove": "删除",
            "browse_suffix": "抓拍列表",
            "back_to_home": "返回首页",
            "total_count": "共 {count} 张",
            "view_grid": "网格",
            "view_list": "列表",
            "sort_label": "排序",
            "per_page_label": "每页",
            "per_page_option": "{size} 张",
            "per_page_all": "全部",
            "sort_time_desc": "时间：新 → 旧",
            "sort_time_asc": "时间：旧 → 新",
            "sort_name_asc": "文件名：A → Z",
            "sort_name_desc": "文件名：Z → A",
            "sort_size_desc": "大小：大 → 小",
            "sort_size_asc": "大小：小 → 大",
            "latest_heading": "最新抓拍",
            "column_name": "文件名",
            "column_time": "抓拍时间",
            "column_size": "大小",
            "empty_items": "还没有抓拍文件。",
            "pagination_first": "首页",
            "pagination_prev": "上一页",
            "pagination_next": "下一页",
            "pagination_last": "末页",
            "pagination_info": "第 {page} / {pages} 页",
            "lightbox_close": "关闭",
            "lightbox_prev": "上一张",
            "lightbox_next": "下一张",
            "lightbox_original": "在新标签打开原图",
        },
        "js": {
            "saved_prefix": "已保存 ",
            "failed_prefix": "失败: ",
            "unknown_error": "未知错误",
            "capturing": "抓拍中…",
            "request_failed_prefix": "请求失败: ",
            "done_prefix": "完成 ",
            "waiting_restart": "等待重启超时，请手动刷新页面",
            "confirm_empty_before": "以下源既没有时间点也没有间隔，将不再自动抓拍：",
            "confirm_empty_after": "。仍然保存？",
            "list_separator": "、",
            "saving": "保存中…",
            "save_failed_prefix": "保存失败: ",
            "saved_restarting": "已保存，正在重启应用…",
            "saved_manual": "已保存，请手动重启应用生效",
        },
    },
}


def negotiate(header):
    entries = []
    for index, part in enumerate(str(header or "").split(",")):
        part = part.strip()
        if not part:
            continue
        segments = part.split(";")
        tag = segments[0].strip().lower()
        quality = 1.0
        for segment in segments[1:]:
            key, _, value = segment.partition("=")
            if key.strip().lower() == "q":
                try:
                    quality = float(value.strip())
                except ValueError:
                    quality = 0.0
        if quality > 0:
            entries.append((quality, index, tag))

    entries.sort(key=lambda item: (-item[0], item[1]))
    for _, _, tag in entries:
        if tag == "*":
            continue
        if tag.startswith("zh"):
            return "zh"
        if tag.startswith("en"):
            return "en"
    return DEFAULT_LANGUAGE
