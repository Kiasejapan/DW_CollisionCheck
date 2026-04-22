# -*- coding: utf-8 -*-
"""
DW_CollisionCheck.py
Polygon Collision Check Tool for Maya 2018-2025
Python 2.7 / 3.x compatible
"""
from __future__ import print_function, division, absolute_import
import sys
import os
import math
import time
import csv

# Version is rewritten by build.bat at every build
# Format: YYYY.MM.DD.HHMM
VERSION = "2026.04.22.1935"

# GitHub raw file URL for auto-update
_GITHUB_RAW_URL = "https://raw.githubusercontent.com/Kiasejapan/DW_CollisionCheck/main/DW_CollisionCheck.py"

PY2 = sys.version_info[0] == 2

# Python 2/3 compatible reload
if PY2:
    _reload = reload   # noqa: F821  (builtin in Py2)
else:
    import importlib
    _reload = importlib.reload

try:
    import maya.cmds as cmds
    import maya.OpenMaya as om
    import maya.OpenMayaUI as omui
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
        from shiboken6 import wrapInstance
    except ImportError:
        from PySide import QtWidgets, QtCore, QtGui
        from shiboken import wrapInstance


# ---------------------------------------------------------------------------
# Localization
# ---------------------------------------------------------------------------
LANG_EN = "en"
LANG_JP = "jp"
_current_lang = LANG_EN
_saved_geometry = None
_saved_lang = None

_STRINGS = {
    "window_title":         {"en": "DW Collision Check",            "jp": u"DW \u5e72\u6e09\u30c1\u30a7\u30c3\u30af"},
    "grp_static":           {"en": "Static Checks",                 "jp": u"\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u30c1\u30a7\u30c3\u30af"},
    "grp_anim":             {"en": "Animation Scan",                "jp": u"\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u30b9\u30ad\u30e3\u30f3"},
    "run_static":           {"en": "Run Static Checks",             "jp": u"\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u5b9f\u884c"},
    "btn_check":            {"en": "Check",                         "jp": u"\u30c1\u30a7\u30c3\u30af"},
    "btn_reload":           {"en": "Reload",                        "jp": u"\u30ea\u30ed\u30fc\u30c9"},
    "btn_update":           {"en": "Check for Updates",              "jp": u"\u66f4\u65b0\u3092\u78ba\u8a8d"},
    "btn_help":             {"en": "?",                             "jp": u"?"},
    "btn_lang":             {"en": "JP",                            "jp": u"EN"},
    "btn_static_results":   {"en": "Static Results",                "jp": u"\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u7d50\u679c"},
    "chk_intersection":     {"en": "Intersection Check",            "jp": u"\u4ea4\u5dee\u30c1\u30a7\u30c3\u30af"},
    "desc_intersection":    {"en": "Detects polygon faces penetrating each other at the current frame.",
                             "jp": u"\u73fe\u5728\u30d5\u30ec\u30fc\u30e0\u3067\u30dd\u30ea\u30b4\u30f3\u30d5\u30a7\u30fc\u30b9\u304c\u8cab\u901a\u3057\u3066\u3044\u308b\u7b87\u6240\u3092\u691c\u51fa\u3057\u307e\u3059\u3002"},
    "chk_overlap":          {"en": "Overlap Check",                 "jp": u"\u91cd\u306a\u308a\u30c1\u30a7\u30c3\u30af"},
    "desc_overlap":         {"en": "Detects coplanar overlapping faces (z-fighting / double faces).",
                             "jp": u"\u540c\u4e00\u5e73\u9762\u4e0a\u3067\u91cd\u306a\u3063\u3066\u3044\u308b\u30d5\u30a7\u30fc\u30b9\u3092\u691c\u51fa\u3057\u307e\u3059\u3002"},
    "chk_proximity":        {"en": "Proximity Check",               "jp": u"\u8fd1\u63a5\u30c1\u30a7\u30c3\u30af"},
    "desc_proximity":       {"en": "Detects faces closer than threshold without intersecting.",
                             "jp": u"\u95be\u5024\u4ee5\u5185\u306b\u8fd1\u63a5\u3057\u3066\u3044\u308b\u30d5\u30a7\u30fc\u30b9\u3092\u691c\u51fa\u3057\u307e\u3059\u3002"},
    "settings_title_static":{"en": "Static Check Settings",         "jp": u"\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u8a2d\u5b9a"},
    "settings_detection":   {"en": "Detection",                     "jp": u"\u691c\u51fa\u8a2d\u5b9a"},
    "settings_mesh_pairs":  {"en": "Mesh Pairs",                    "jp": u"\u30e1\u30c3\u30b7\u30e5\u30da\u30a2"},
    "chk_selected_only":    {"en": "Check selected meshes only",    "jp": u"\u9078\u629e\u30e1\u30c3\u30b7\u30e5\u306e\u307f\u30c1\u30a7\u30c3\u30af"},
    "chk_self_intersect":   {"en": "Include self-intersection",     "jp": u"\u81ea\u5df1\u4ea4\u5dee\u3082\u691c\u51fa"},
    "chk_self_intersect":   {"en": "Include self-intersection",     "jp": u"\u81ea\u5df1\u4ea4\u5dee\u3082\u691c\u51fa"},
    "lbl_proximity_thresh":  {"en": "Proximity threshold (mm):",    "jp": u"\u8fd1\u63a5\u95be\u5024 (mm):"},
    "lbl_add_pair":         {"en": "Add selected pair",             "jp": u"\u9078\u629e\u30da\u30a2\u3092\u8ffd\u52a0"},
    "lbl_remove_pair":      {"en": "Remove",                        "jp": u"\u524a\u9664"},
    "lbl_depth_threshold":  {"en": "Depth threshold:",              "jp": u"\u6df1\u5ea6\u95be\u5024:"},
    "result_title_static":  {"en": "Static Check Results",          "jp": u"\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u7d50\u679c"},
    "col_status":           {"en": "Status",                        "jp": u"\u30b9\u30c6\u30fc\u30bf\u30b9"},
    "col_check":            {"en": "Check",                         "jp": u"\u30c1\u30a7\u30c3\u30af"},
    "col_mesh_a":           {"en": "Mesh A",                        "jp": u"\u30e1\u30c3\u30b7\u30e5 A"},
    "col_mesh_b":           {"en": "Mesh B",                        "jp": u"\u30e1\u30c3\u30b7\u30e5 B"},
    "col_detail":           {"en": "Detail",                        "jp": u"\u8a73\u7d30"},
    "btn_select_faces":     {"en": "Select Faces",                  "jp": u"\u30d5\u30a7\u30fc\u30b9\u9078\u629e"},
    "btn_close":            {"en": "Close",                         "jp": u"\u9589\u3058\u308b"},
    "status_ready":         {"en": "Ready",                         "jp": u"\u6e96\u5099\u5b8c\u4e86"},
    "status_no_meshes":     {"en": "No meshes selected or available.", "jp": u"\u30e1\u30c3\u30b7\u30e5\u304c\u9078\u629e\u3055\u308c\u3066\u3044\u307e\u305b\u3093\u3002"},
    "status_no_anim":       {"en": "Selected meshes have no animation.", "jp": u"\u9078\u629e\u30e1\u30c3\u30b7\u30e5\u306b\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u304c\u3042\u308a\u307e\u305b\u3093\u3002"},
    "status_checking":      {"en": "Running checks...",             "jp": u"\u30c1\u30a7\u30c3\u30af\u5b9f\u884c\u4e2d..."},
    "status_done":          {"en": "Done: {count} issue(s) found.", "jp": u"\u5b8c\u4e86: {count} \u4ef6\u306e\u554f\u984c\u3092\u691c\u51fa\u3057\u307e\u3057\u305f\u3002"},
    "scope_label":          {"en": "Target: {scope}",               "jp": u"\u5bfe\u8c61: {scope}"},
    "no_mesh_selected":     {"en": "No mesh selected. Using all scene meshes.",
                             "jp": u"\u30e1\u30c3\u30b7\u30e5\u304c\u9078\u629e\u3055\u308c\u3066\u3044\u307e\u305b\u3093\u3002\u30b7\u30fc\u30f3\u5168\u4f53\u3092\u4f7f\u7528\u3057\u307e\u3059\u3002"},
    "no_pairs":             {"en": "No mesh pairs defined. Add pairs in settings.",
                             "jp": u"\u30e1\u30c3\u30b7\u30e5\u30da\u30a2\u304c\u672a\u8a2d\u5b9a\u3067\u3059\u3002\u8a2d\u5b9a\u304b\u3089\u30da\u30a2\u3092\u8ffd\u52a0\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "err_triangulate":      {"en": "Failed to triangulate: {mesh}", "jp": u"\u4e09\u89d2\u5316\u5931\u6557: {mesh}"},
    "pass_label":           {"en": "PASS",                          "jp": u"PASS"},
    "fail_label":           {"en": "FAIL",                          "jp": u"FAIL"},
    "run_anim":             {"en": "Run Animation Scan",            "jp": u"\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u30b9\u30ad\u30e3\u30f3\u5b9f\u884c"},
    "btn_stop_anim":        {"en": "Stop",                          "jp": u"\u505c\u6b62"},
    "btn_anim_results":     {"en": "Anim Results",                  "jp": u"\u30a2\u30cb\u30e1\u7d50\u679c"},
    "anim_settings_title":  {"en": "Animation Scan Settings",       "jp": u"\u30a2\u30cb\u30e1\u30b9\u30ad\u30e3\u30f3\u8a2d\u5b9a"},
    "lbl_frame_range":      {"en": "Frame range:",                  "jp": u"\u30d5\u30ec\u30fc\u30e0\u7bc4\u56f2:"},
    "lbl_frame_step":       {"en": "Step:",                         "jp": u"\u30b9\u30c6\u30c3\u30d7:"},
    "chk_use_timeline":     {"en": "Use timeline range",            "jp": u"\u30bf\u30a4\u30e0\u30e9\u30a4\u30f3\u7bc4\u56f2\u3092\u4f7f\u7528"},
    "chk_ignore_static":    {"en": "Ignore baseline frame collisions",
                             "jp": u"\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u30d5\u30ec\u30fc\u30e0\u306e\u5e72\u6e09\u3092\u7121\u8996"},
    "lbl_baseline_frame":   {"en": "Baseline frame:",               "jp": u"\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3:"},
    "lbl_vert_share_tol":   {"en": "Vertex-share tolerance:",       "jp": u"\u540c\u4e00\u9802\u70b9\u3068\u307f\u306a\u3059\u8ddd\u96e2:"},
    "tip_vert_share_tol":   {"en": "Triangles sharing a vertex within this distance are skipped from intersection testing.",
                             "jp": u"\u3053\u306e\u8ddd\u96e2\u4ee5\u5185\u3067\u9802\u70b9\u3092\u5171\u6709\u3059\u308b\u4e09\u89d2\u5f62\u30da\u30a2\u306f\u4ea4\u5dee\u5224\u5b9a\u3092\u30b9\u30ad\u30c3\u30d7\u3057\u307e\u3059\u3002"},

    # ---- Mesh Landing (Other tab) ------------------------------------
    "ml_grp_title":         {"en": "Face Snap",                     "jp": u"\u30d5\u30a7\u30fc\u30b9\u30b9\u30ca\u30c3\u30d7"},
    "ml_grp_desc":          {"en": "Click Launch to open the Face Snap dialog.",
                             "jp": u"\u300c\u8d77\u52d5\u300d\u3067\u30d5\u30a7\u30fc\u30b9\u30b9\u30ca\u30c3\u30d7\u30c0\u30a4\u30a2\u30ed\u30b0\u3092\u958b\u304d\u307e\u3059\u3002"},
    "ml_btn_launch":        {"en": u"\u25B6 Launch",                "jp": u"\u25B6 \u8d77\u52d5"},
    "ml_dlg_title":         {"en": "Face Snap",                     "jp": u"\u30d5\u30a7\u30fc\u30b9\u30b9\u30ca\u30c3\u30d7"},
    "ml_lbl_mesh_a":        {"en": "Mesh A (moves):",               "jp": u"\u30e1\u30c3\u30b7\u30e5 A (\u79fb\u52d5\u5074):"},
    "ml_lbl_mesh_b":        {"en": "Mesh B (ground):",              "jp": u"\u30e1\u30c3\u30b7\u30e5 B (\u5730\u9762):"},
    "ml_btn_set":           {"en": "Set",                           "jp": u"\u30bb\u30c3\u30c8"},
    "ml_btn_swap":          {"en": u"\u21C4 Swap A \u2194 B",       "jp": u"\u21C4 A \u2194 B \u5165\u308c\u66ff\u3048"},
    "ml_lbl_axis":          {"en": "Axis:",                         "jp": u"\u8ef8:"},
    "ml_lbl_direction":     {"en": "Direction:",                    "jp": u"\u65b9\u5411:"},
    "ml_dir_auto":          {"en": "Auto",                          "jp": u"\u81ea\u52d5"},
    "ml_dir_positive":      {"en": "+",                             "jp": u"+"},
    "ml_dir_negative":      {"en": u"\u2212",                       "jp": u"\u2212"},
    "ml_lbl_mode":          {"en": "Move mode:",                    "jp": u"\u79fb\u52d5\u30e2\u30fc\u30c9:"},
    "ml_mode_object":       {"en": "Object",                        "jp": u"\u30aa\u30d6\u30b8\u30a7\u30af\u30c8"},
    "ml_mode_component":    {"en": "Component",                     "jp": u"\u30b3\u30f3\u30dd\u30fc\u30cd\u30f3\u30c8"},
    "ml_lbl_offset":        {"en": "Offset:",                       "jp": u"\u30aa\u30d5\u30bb\u30c3\u30c8:"},
    "ml_tip_offset":        {"en": "Gap from the target surface. Positive = stop before contact; Negative = embed into target.",
                             "jp": u"\u30bf\u30fc\u30b2\u30c3\u30c8\u8868\u9762\u3068\u306e\u9694\u305f\u308a\u8ddd\u96e2\u3002\u6b63\u306e\u5024=\u624b\u524d\u3067\u505c\u6b62\u3001\u8ca0\u306e\u5024=\u30bf\u30fc\u30b2\u30c3\u30c8\u306b\u57cb\u3081\u8fbc\u307f\u3002"},
    "ml_tip_slider":        {"en": "Drag to adjust offset in the range -1.0 to +1.0. Use the spinbox for larger values.",
                             "jp": u"\u30c9\u30e9\u30c3\u30b0\u3067\u30aa\u30d5\u30bb\u30c3\u30c8\u3092 -1.0 \u301c +1.0 \u306e\u7bc4\u56f2\u3067\u8abf\u6574\u3002\u3088\u308a\u5927\u304d\u3044\u5024\u306f\u30b9\u30d4\u30f3\u30dc\u30c3\u30af\u30b9\u306b\u76f4\u63a5\u5165\u529b\u3002"},
    "ml_btn_preview":       {"en": u"\u25B6 Preview",               "jp": u"\u25B6 \u30d7\u30ec\u30d3\u30e5\u30fc"},
    "ml_btn_confirm":       {"en": u"\u2714 Confirm",               "jp": u"\u2714 \u78ba\u5b9a"},
    "ml_btn_revert":        {"en": u"\u21A9 Revert",                "jp": u"\u21A9 \u5143\u306b\u623b\u3059"},
    "ml_status_no_a":       {"en": "Mesh A is not set.",            "jp": u"\u30e1\u30c3\u30b7\u30e5 A \u304c\u672a\u8a2d\u5b9a\u3067\u3059\u3002"},
    "ml_status_no_b":       {"en": "Mesh B is not set.",            "jp": u"\u30e1\u30c3\u30b7\u30e5 B \u304c\u672a\u8a2d\u5b9a\u3067\u3059\u3002"},
    "ml_status_no_hit":     {"en": "No surface found along the axis.",
                             "jp": u"\u8ef8\u65b9\u5411\u306b\u8868\u9762\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002"},
    "ml_status_no_enclosed": {"en": "Component mode: select face(s), or 3+ vertices / edges that fully enclose a face.",
                              "jp": u"\u30b3\u30f3\u30dd\u30fc\u30cd\u30f3\u30c8\u30e2\u30fc\u30c9: \u30d5\u30a7\u30fc\u30b9\u3092\u9078\u629e\u3059\u308b\u304b\u3001\u30d5\u30a7\u30fc\u30b9\u3092\u56f2\u3080 3 \u70b9\u4ee5\u4e0a\u306e\u9802\u70b9 / \u30a8\u30c3\u30b8\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "ml_status_cancelled":   {"en": "Cancelled.", "jp": u"\u30ad\u30e3\u30f3\u30bb\u30eb\u3057\u307e\u3057\u305f\u3002"},
    "ml_confirm_expand_title": {"en": "Expand selection to enclosing faces?",
                                "jp": u"\u9078\u629e\u3092\u5185\u5305\u30d5\u30a7\u30fc\u30b9\u306b\u62e1\u5f35\u3057\u307e\u3059\u304b\uff1f"},
    "ml_confirm_expand_body":  {"en": "The current selection does not fully enclose any face.\n\nExpand to adjacent faces ({n_faces} face(s), {n_verts} vertex/vertices) and run the landing?\n\nMaya's selection will be updated to match.",
                                "jp": u"\u73fe\u5728\u306e\u9078\u629e\u3067\u306f\u30d5\u30a7\u30fc\u30b9\u3092\u5b8c\u5168\u306b\u56f2\u3081\u307e\u305b\u3093\u3002\n\n\u9694\u63a5\u3059\u308b\u30d5\u30a7\u30fc\u30b9\uff08{n_faces} \u30d5\u30a7\u30fc\u30b9\u3001{n_verts} \u9802\u70b9\uff09\u306b\u62e1\u5f35\u3057\u3066\u63a5\u5730\u3092\u5b9f\u884c\u3057\u307e\u3059\u304b\uff1f\n\nMaya \u306e\u9078\u629e\u72b6\u614b\u3082\u66f4\u65b0\u3055\u308c\u307e\u3059\u3002"},
    "ml_status_preview":    {"en": "Preview: moved {dist} along {axis}. Click Confirm or Revert.",
                             "jp": u"\u30d7\u30ec\u30d3\u30e5\u30fc: {axis}\u8ef8\u306b {dist} \u79fb\u52d5\u3002\u78ba\u5b9a\u307e\u305f\u306f\u5143\u306b\u623b\u3059\u3002"},
    "ml_status_confirmed":  {"en": "Confirmed: moved {dist} along {axis}.",
                             "jp": u"\u78ba\u5b9a: {axis}\u8ef8\u306b {dist} \u79fb\u52d5\u6e08\u307f\u3002"},
    "ml_status_reverted":   {"en": "Reverted.",                     "jp": u"\u5143\u306b\u623b\u3057\u307e\u3057\u305f\u3002"},
    "ml_status_swapped":    {"en": "Swapped A \u2194 B.",           "jp": u"A \u2194 B \u3092\u5165\u308c\u66ff\u3048\u307e\u3057\u305f\u3002"},

    # ---- Tabs --------------------------------------------------------
    "tab_check":            {"en": "Check",                         "jp": u"\u30c1\u30a7\u30c3\u30af"},

    "anim_scanning":        {"en": "Scanning frame {frame}/{total}...",
                             "jp": u"\u30d5\u30ec\u30fc\u30e0 {frame}/{total} \u3092\u30b9\u30ad\u30e3\u30f3\u4e2d..."},
    "anim_done":            {"en": "Animation scan done: {count} frame(s) with issues.",
                             "jp": u"\u30a2\u30cb\u30e1\u30b9\u30ad\u30e3\u30f3\u5b8c\u4e86: {count} \u30d5\u30ec\u30fc\u30e0\u3067\u554f\u984c\u691c\u51fa\u3002"},
    "anim_cancelled":       {"en": "Animation scan cancelled.",     "jp": u"\u30a2\u30cb\u30e1\u30b9\u30ad\u30e3\u30f3\u304c\u30ad\u30e3\u30f3\u30bb\u30eb\u3055\u308c\u307e\u3057\u305f\u3002"},
    "result_title_anim":    {"en": "Animation Scan Results",        "jp": u"\u30a2\u30cb\u30e1\u30b9\u30ad\u30e3\u30f3\u7d50\u679c"},
    "col_frame":            {"en": "Frame",                         "jp": u"\u30d5\u30ec\u30fc\u30e0"},
    "btn_goto_frame":       {"en": "Go to Frame",                   "jp": u"\u30d5\u30ec\u30fc\u30e0\u3078\u79fb\u52d5"},
    "lbl_anim_summary":     {"en": "{total} issues across {frames} frame(s)",
                             "jp": u"{frames} \u30d5\u30ec\u30fc\u30e0\u3067 {total} \u4ef6\u306e\u554f\u984c"},
    # ---- Help (per-tab) ----------------------------------------------
    "help_title":           {"en": "Help \u2014 DW Collision Check",
                             "jp": u"\u30d8\u30eb\u30d7 \u2014 DW \u5e72\u6e09\u30c1\u30a7\u30c3\u30af"},
    "help_body_check": {
        "en": "<h2>Check Tab</h2>"
              "<p>Detects polygon intersections and overlaps at the current frame "
              "or across an animation range.</p>"
              "<h3>Static Checks</h3>"
              "<ul>"
              "<li><b>Intersection Check</b>: Faces that physically penetrate each other.</li>"
              "<li><b>Overlap Check</b>: Coplanar overlapping faces (z-fighting / double faces).</li>"
              "</ul>"
              "<p><b>Depth threshold</b>: minimum penetration depth to report.<br>"
              "<b>Vertex-share tolerance</b>: triangles sharing a vertex within this distance are skipped.</p>"
              "<h3>Animation Scan</h3>"
              "<p>Sweeps a frame range and reports which frames contain collisions. "
              "Useful for finding problematic frames in cloth/hair animation without stepping through manually.</p>"
              "<ul>"
              "<li><b>Frame range</b>: Start / End / Step. Toggle <i>Use timeline range</i> "
              "to follow Maya's current playback range.</li>"
              "<li><b>Ignore baseline frame</b>: Excludes collisions that already exist at a reference frame "
              "(e.g. resting pose), so only animation-induced issues are reported.</li>"
              "<li><b>Baseline frame</b>: The frame treated as the clean reference.</li>"
              "<li><b>Stop</b>: Cancels the scan mid-run.</li>"
              "</ul>"
              "<h3>Usage</h3>"
              "<ol>"
              "<li>Select meshes in the viewport.</li>"
              "<li>Click [Check] on each item, or [Run Static Checks] to run all.</li>"
              "<li>Click a row in the Results window to select the problem faces.</li>"
              "<li>For animation: set the range and click [Run Animation Scan]. "
              "Click a frame row to jump the timeline there.</li>"
              "</ol>",
        "jp": u"<h2>\u30c1\u30a7\u30c3\u30af\u30bf\u30d6</h2>"
              u"<p>\u73fe\u5728\u30d5\u30ec\u30fc\u30e0\u307e\u305f\u306f\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u7bc4\u56f2\u5185\u3067\u30dd\u30ea\u30b4\u30f3\u306e\u4ea4\u5dee\u30fb\u91cd\u306a\u308a\u3092\u691c\u51fa\u3057\u307e\u3059\u3002</p>"
              u"<h3>\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u30c1\u30a7\u30c3\u30af</h3>"
              u"<ul>"
              u"<li><b>\u4ea4\u5dee\u30c1\u30a7\u30c3\u30af</b>\uff1a\u5b9f\u969b\u306b\u30dd\u30ea\u30b4\u30f3\u304c\u8cab\u901a\u3057\u3066\u3044\u308b\u30d5\u30a7\u30fc\u30b9\u3092\u691c\u51fa\u3002</li>"
              u"<li><b>\u91cd\u306a\u308a\u30c1\u30a7\u30c3\u30af</b>\uff1a\u540c\u4e00\u5e73\u9762\u4e0a\u3067\u91cd\u306a\u308b\u30d5\u30a7\u30fc\u30b9\uff08Z\u30d5\u30a1\u30a4\u30c8\u30fb\u4e8c\u91cd\u9762\uff09\u3092\u691c\u51fa\u3002</li>"
              u"</ul>"
              u"<p><b>\u6df1\u5ea6\u95be\u5024</b>\uff1a\u5831\u544a\u5bfe\u8c61\u3068\u3059\u308b\u6700\u5c0f\u8cab\u5165\u6df1\u3055\u3002<br>"
              u"<b>\u540c\u4e00\u9802\u70b9\u3068\u307f\u306a\u3059\u8ddd\u96e2</b>\uff1a\u3053\u306e\u8ddd\u96e2\u4ee5\u5185\u3067\u9802\u70b9\u3092\u5171\u6709\u3059\u308b\u4e09\u89d2\u5f62\u30da\u30a2\u306f\u4ea4\u5dee\u5224\u5b9a\u3092\u30b9\u30ad\u30c3\u30d7\u3002</p>"
              u"<h3>\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u30b9\u30ad\u30e3\u30f3</h3>"
              u"<p>\u30d5\u30ec\u30fc\u30e0\u7bc4\u56f2\u3092\u8d70\u67fb\u3057\u3001\u5e72\u6e09\u304c\u767a\u751f\u3057\u305f\u30d5\u30ec\u30fc\u30e0\u3092\u4e00\u89a7\u5316\u3057\u307e\u3059\u3002"
              u"\u5e03\u3084\u9aea\u306e\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u3067\u554f\u984c\u306e\u3042\u308b\u30d5\u30ec\u30fc\u30e0\u3092\u52b9\u7387\u7684\u306b\u898b\u3064\u3051\u3089\u308c\u307e\u3059\u3002</p>"
              u"<ul>"
              u"<li><b>\u30d5\u30ec\u30fc\u30e0\u7bc4\u56f2</b>\uff1a\u958b\u59cb / \u7d42\u4e86 / \u30b9\u30c6\u30c3\u30d7\u3002 <i>\u30bf\u30a4\u30e0\u30e9\u30a4\u30f3\u7bc4\u56f2\u3092\u4f7f\u7528</i> \u3067Maya\u306e\u518d\u751f\u7bc4\u56f2\u3068\u9023\u52d5\u3002</li>"
              u"<li><b>\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u30d5\u30ec\u30fc\u30e0\u306e\u5e72\u6e09\u3092\u7121\u8996</b>\uff1a\u57fa\u6e96\u30d5\u30ec\u30fc\u30e0\uff08\u5f85\u6a5f\u30dd\u30fc\u30ba\u7b49\uff09\u3067\u65e2\u306b\u767a\u751f\u3057\u3066\u3044\u308b\u5e72\u6e09\u3092\u9664\u5916\u3057\u3001\u30a2\u30cb\u30e1\u56fa\u6709\u306e\u554f\u984c\u3060\u3051\u3092\u691c\u51fa\u3002</li>"
              u"<li><b>\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3</b>\uff1a\u57fa\u6e96\u3068\u307f\u306a\u3059\u30af\u30ea\u30fc\u30f3\u306a\u30d5\u30ec\u30fc\u30e0\u3002</li>"
              u"<li><b>\u505c\u6b62</b>\uff1a\u30b9\u30ad\u30e3\u30f3\u9014\u4e2d\u3067\u30ad\u30e3\u30f3\u30bb\u30eb\u3002</li>"
              u"</ul>"
              u"<h3>\u4f7f\u3044\u65b9</h3>"
              u"<ol>"
              u"<li>\u30d3\u30e5\u30fc\u30dd\u30fc\u30c8\u3067\u30e1\u30c3\u30b7\u30e5\u3092\u9078\u629e\u3002</li>"
              u"<li>\u5404\u9805\u76ee\u306e [\u30c1\u30a7\u30c3\u30af]\u3001\u307e\u305f\u306f [\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u5b9f\u884c] \u3067\u4e00\u62ec\u691c\u67fb\u3002</li>"
              u"<li>\u7d50\u679c\u884c\u3092\u30af\u30ea\u30c3\u30af\u3059\u308b\u3068\u5bfe\u5fdc\u3059\u308b\u30d5\u30a7\u30fc\u30b9\u3092\u9078\u629e\u8868\u793a\u3002</li>"
              u"<li>\u30a2\u30cb\u30e1\u306f\u7bc4\u56f2\u3092\u8a2d\u5b9a\u3057 [\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u30b9\u30ad\u30e3\u30f3\u5b9f\u884c]\u3002\u30d5\u30ec\u30fc\u30e0\u884c\u3092\u30af\u30ea\u30c3\u30af\u3067\u305d\u306e\u30d5\u30ec\u30fc\u30e0\u306b\u79fb\u52d5\u3002</li>"
              u"</ol>",
    },
    "help_body_snap": {
        "en": "<h2>Snap Tab</h2>"
              "<h3>Vertex Snap</h3>"
              "<p>Distance-based vertex snap. Detects close vertex pairs and lets you snap them "
              "interactively. Useful for stitching separate mesh parts (hair, cloth, armor, etc.) "
              "without manually picking vertex pairs.</p>"
              "<h4>Workflow</h4>"
              "<ol>"
              "<li>Select mesh(es) in the viewport (groups OK &mdash; child meshes are auto-collected).</li>"
              "<li>Click [Launch]. The result window opens with all close vertex pairs detected.</li>"
              "<li>Adjust the threshold by dragging directly on the histogram:</li>"
              "<ul>"
              "<li>Bars show how vertex pairs are distributed by distance.</li>"
              "<li>Green = close, orange = medium, red = far.</li>"
              "<li>Blue line = current threshold. Only pairs within threshold are listed below.</li>"
              "</ul>"
              "<li>Click a table row to highlight the vertex pair in Maya.</li>"
              "<li>Select rows and choose a snap direction:</li>"
              "<ul>"
              "<li><b>Snap A\u2192B</b>: move Mesh A's vertex to Mesh B's position.</li>"
              "<li><b>Snap B\u2192A</b>: move Mesh B's vertex to Mesh A's position.</li>"
              "<li><b>Snap Mid</b>: move both vertices to the midpoint.</li>"
              "</ul>"
              "<li>Snapped rows are marked with \u2714 and remain visible for review.</li>"
              "<li>When finished, click [\u2714 Confirm] to finalize, or [\u21A9 Revert] to undo all snaps at once.</li>"
              "</ol>"
              "<h4>Options</h4>"
              "<ul>"
              "<li><b>Include same-mesh pairs</b> (default ON): also detect close vertices within the same mesh. "
              "Turn OFF to only detect pairs across different meshes.</li>"
              "<li><b>Hide coincident</b> (default ON): hide pairs that were already overlapping (distance near 0) "
              "so the table stays focused on pairs that need action.</li>"
              "</ul>"
              "<h4>Merge (Maya)</h4>"
              "<p>Opens Maya's native <i>Merge Vertices</i> option box for conventional vertex merging "
              "after snapping is complete.</p>"
              "<hr>"
              "<h3>Face Snap</h3>"
              "<p>Lands <b>Mesh A</b> onto <b>Mesh B</b> along a chosen axis. "
              "Raycasts every Mesh A vertex toward Mesh B, verifies with polygon-level collision, "
              "and moves Mesh A so it touches Mesh B without penetrating.</p>"
              "<h4>Workflow</h4>"
              "<ol>"
              "<li>Click <b>[Launch]</b> in the Face Snap group to open the dialog.</li>"
              "<li>Select the mesh(es) to move and click <b>[Set]</b> on the <b>Mesh A</b> row.</li>"
              "<li>Select the ground mesh(es) and click <b>[Set]</b> on the <b>Mesh B</b> row.</li>"
              "<li>Use <b>[\u21C4 Swap A \u2194 B]</b> if you picked them in the wrong order.</li>"
              "<li>Adjust <b>Axis</b>, <b>Direction</b>, <b>Move mode</b>, and <b>Offset</b>.</li>"
              "<li>Click <b>[\u25B6 Preview]</b>. Mesh A moves in-place for visual confirmation.</li>"
              "<li>Change any parameter and click <b>[Preview]</b> again to retry \u2014 the previous preview is automatically reverted first.</li>"
              "<li>When satisfied, click <b>[\u2714 Confirm]</b> to keep the result, or <b>[\u21A9 Revert]</b> to cancel.</li>"
              "</ol>"
              "<p><i>Closing the dialog while a preview is unconfirmed automatically reverts it.</i></p>"
              "<h4>Parameters</h4>"
              "<ul>"
              "<li><b>Axis</b> \u2014 X / Y / Z. Landing is constrained to this axis.</li>"
              "<li><b>Direction</b>"
              "<ul>"
              "<li><b>Auto</b> \u2014 picks direction from A and B center positions.</li>"
              "<li><b>+</b> / <b>\u2212</b> \u2014 force the sign explicitly.</li>"
              "</ul></li>"
              "<li><b>Move mode</b>"
              "<ul>"
              "<li><b>Object</b> \u2014 moves the whole Mesh A transform.</li>"
              "<li><b>Component</b> \u2014 moves only the currently selected vertices / edges / faces of Mesh A. "
              "The selection must fully enclose one or more faces (e.g. all four vertices of a quad). "
              "If the selection doesn't enclose a face, a dialog asks whether to expand to the adjacent faces.</li>"
              "</ul></li>"
              "<li><b>Offset</b> \u2014 gap to keep between A and B after landing. "
              "0 means the surfaces touch; negative values embed Mesh A into Mesh B.</li>"
              "</ul>"
              "<h4>Algorithm</h4>"
              "<p>A raycast gives an initial upper-bound distance. If Mesh A still collides with Mesh B at that "
              "distance (with rotated or concave shapes), a binary search in [0, upper-bound] "
              "finds the largest safe distance with no polygon-level penetration. "
              "If rays miss Mesh B entirely, Mesh A is dropped to the world origin plane (Y=0 for Y axis, etc.).</p>",
        "jp": u"<h2>\u30b9\u30ca\u30c3\u30d7\u30bf\u30d6</h2>"
              u"<h3>\u30d0\u30fc\u30c6\u30c3\u30af\u30b9\u30ca\u30c3\u30d7</h3>"
              u"<p>\u8ddd\u96e2\u30d9\u30fc\u30b9\u3067\u8fd1\u3044\u9802\u70b9\u30da\u30a2\u3092\u691c\u51fa\u3057\u3001\u5bfe\u8a71\u7684\u306b\u30b9\u30ca\u30c3\u30d7\u3055\u305b\u308b\u6a5f\u80fd\u3002"
              u"\u9aea\u30fb\u5e03\u30fb\u30a2\u30fc\u30de\u30fc\u7b49\u306e\u7570\u306a\u308b\u30e1\u30c3\u30b7\u30e5\u3092\u7e4b\u304e\u5408\u308f\u305b\u308b\u969b\u3001\u9802\u70b9\u30da\u30a2\u3092\u624b\u52d5\u3067\u9078\u3076\u624b\u9593\u3092\u7701\u3051\u307e\u3059\u3002</p>"
              u"<h4>\u4f5c\u696d\u624b\u9806</h4>"
              u"<ol>"
              u"<li>\u30d3\u30e5\u30fc\u30dd\u30fc\u30c8\u3067\u30e1\u30c3\u30b7\u30e5\u3092\u9078\u629e\uff08\u30b0\u30eb\u30fc\u30d7\u9078\u629e\u53ef\u3001\u914d\u4e0b\u306e\u30e1\u30c3\u30b7\u30e5\u3092\u81ea\u52d5\u3067\u53ce\u96c6\uff09\u3002</li>"
              u"<li>[\u8d77\u52d5] \u3092\u30af\u30ea\u30c3\u30af\u3002\u7d50\u679c\u30a6\u30a3\u30f3\u30c9\u30a6\u304c\u958b\u304d\u3001\u8fd1\u63a5\u30da\u30a2\u304c\u4e00\u89a7\u8868\u793a\u3055\u308c\u307e\u3059\u3002</li>"
              u"<li>\u30d2\u30b9\u30c8\u30b0\u30e9\u30e0\u3092\u76f4\u63a5\u30c9\u30e9\u30c3\u30b0\u3057\u3066\u3057\u304d\u3044\u5024\u3092\u8abf\u6574\uff1a</li>"
              u"<ul>"
              u"<li>\u30d0\u30fc\u306f\u9802\u70b9\u30da\u30a2\u306e\u8ddd\u96e2\u5206\u5e03\u3092\u8868\u3057\u307e\u3059\u3002</li>"
              u"<li>\u7dd1 = \u8fd1\u3044\u3001\u6a59 = \u4e2d\u9593\u3001\u8d64 = \u9060\u3044\u3002</li>"
              u"<li>\u9752\u3044\u7e26\u7dda\u304c\u73fe\u5728\u306e\u3057\u304d\u3044\u5024\u3002\u3053\u308c\u4ee5\u5185\u306e\u30da\u30a2\u306e\u307f\u8868\u306b\u8868\u793a\u3055\u308c\u307e\u3059\u3002</li>"
              u"</ul>"
              u"<li>\u884c\u3092\u30af\u30ea\u30c3\u30af\u3059\u308b\u3068Maya\u306e\u30d3\u30e5\u30fc\u30dd\u30fc\u30c8\u3067\u305d\u306e\u9802\u70b9\u30da\u30a2\u3092\u9078\u629e\u8868\u793a\u3002</li>"
              u"<li>\u884c\u3092\u9078\u629e\u3057\u3066Snap\u65b9\u5411\u30dc\u30bf\u30f3\u3092\u30af\u30ea\u30c3\u30af\uff1a</li>"
              u"<ul>"
              u"<li><b>Snap A\u2192B</b>\uff1aMesh A \u5074\u306e\u9802\u70b9\u3092 Mesh B \u5074\u306b\u5bc4\u305b\u308b\u3002</li>"
              u"<li><b>Snap B\u2192A</b>\uff1aMesh B \u5074\u306e\u9802\u70b9\u3092 Mesh A \u5074\u306b\u5bc4\u305b\u308b\u3002</li>"
              u"<li><b>Snap Mid</b>\uff1a\u4e21\u65b9\u3092\u4e2d\u9593\u4f4d\u7f6e\u306b\u5bc4\u305b\u308b\u3002</li>"
              u"</ul>"
              u"<li>Snap\u6e08\u307f\u306e\u884c\u306f \u2714 \u30de\u30fc\u30af\u304c\u4ed8\u3044\u3066\u8868\u306b\u6b8b\u308a\u307e\u3059\uff08\u78ba\u8a8d\u53ef\u80fd\uff09\u3002</li>"
              u"<li>\u6700\u5f8c\u306b [\u2714 \u78ba\u5b9a] \u3067\u78ba\u5b9a\u3001\u307e\u305f\u306f [\u21A9 \u5143\u306b\u623b\u3059] \u3067\u3059\u3079\u3066\u306e Snap \u3092\u4e00\u62ec\u53d6\u308a\u6d88\u3057\u3002</li>"
              u"</ol>"
              u"<h4>\u30aa\u30d7\u30b7\u30e7\u30f3</h4>"
              u"<ul>"
              u"<li><b>\u540c\u30e1\u30c3\u30b7\u30e5\u3082\u691c\u67fb</b>\uff08\u30c7\u30d5\u30a9\u30eb\u30c8ON\uff09\uff1a\u540c\u4e00\u30e1\u30c3\u30b7\u30e5\u5185\u306e\u8fd1\u63a5\u9802\u70b9\u3082\u691c\u51fa\u3002"
              u"OFF \u306b\u3059\u308b\u3068\u4ed6\u30e1\u30c3\u30b7\u30e5\u9593\u306e\u30da\u30a2\u306e\u307f\u691c\u51fa\u3002</li>"
              u"<li><b>\u91cd\u8907\u9802\u70b9\u3092\u975e\u8868\u793a</b>\uff08\u30c7\u30d5\u30a9\u30eb\u30c8ON\uff09\uff1a\u65e2\u306b\u8ddd\u96e2\u304c\u307b\u307c0\u306e\u30da\u30a2\u3092\u96a0\u3057\u3001\u4f5c\u696d\u5bfe\u8c61\u306e\u30da\u30a2\u3060\u3051\u3092\u8868\u793a\u3002</li>"
              u"</ul>"
              u"<h4>Merge (Maya)</h4>"
              u"<p>Maya \u6a19\u6e96\u306e\u300c\u9802\u70b9\u306e\u30de\u30fc\u30b8\u300d\u30aa\u30d7\u30b7\u30e7\u30f3\u30dc\u30c3\u30af\u30b9\u3092\u958b\u304d\u307e\u3059\u3002"
              u"Snap \u5f8c\u306e\u901a\u5e38\u306e\u9802\u70b9\u30de\u30fc\u30b8\u306b\u4f7f\u7528\u3057\u307e\u3059\u3002</p>"
              u"<hr>"
              u"<h3>\u30d5\u30a7\u30fc\u30b9\u30b9\u30ca\u30c3\u30d7</h3>"
              u"<p><b>\u30e1\u30c3\u30b7\u30e5 A</b> \u3092 <b>\u30e1\u30c3\u30b7\u30e5 B</b> \u306b\u6307\u5b9a\u8ef8\u306b\u6cbf\u3063\u3066\u63a5\u5730\u3055\u305b\u307e\u3059\u3002"
              u"A \u306e\u5168\u9802\u70b9\u304b\u3089 B \u306b\u5411\u3051\u3066\u30ec\u30a4\u30ad\u30e3\u30b9\u30c8\u3092\u884c\u3044\u3001\u30dd\u30ea\u30b4\u30f3\u30ec\u30d9\u30eb\u306e\u885d\u7a81\u5224\u5b9a\u3067\u691c\u8a3c\u3057\u3001"
              u"\u8cab\u901a\u305b\u305a\u306b\u63a5\u89e6\u3059\u308b\u4f4d\u7f6e\u307e\u3067 A \u3092\u79fb\u52d5\u3057\u307e\u3059\u3002</p>"
              u"<h4>\u4f5c\u696d\u624b\u9806</h4>"
              u"<ol>"
              u"<li>\u30d5\u30a7\u30fc\u30b9\u30b9\u30ca\u30c3\u30d7\u306e <b>[\u8d77\u52d5]</b> \u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u30c0\u30a4\u30a2\u30ed\u30b0\u3092\u958b\u304d\u307e\u3059\u3002</li>"
              u"<li>\u79fb\u52d5\u3055\u305b\u305f\u3044\u30e1\u30c3\u30b7\u30e5\u3092\u30d3\u30e5\u30fc\u30dd\u30fc\u30c8\u3067\u9078\u629e\u3057\u3001<b>\u30e1\u30c3\u30b7\u30e5 A</b> \u884c\u306e <b>[\u30bb\u30c3\u30c8]</b> \u3092\u30af\u30ea\u30c3\u30af\u3002</li>"
              u"<li>\u5730\u9762\u5074\u306e\u30e1\u30c3\u30b7\u30e5\u3092\u9078\u629e\u3057\u3001<b>\u30e1\u30c3\u30b7\u30e5 B</b> \u884c\u306e <b>[\u30bb\u30c3\u30c8]</b> \u3092\u30af\u30ea\u30c3\u30af\u3002</li>"
              u"<li>\u9006\u306b\u30bb\u30c3\u30c8\u3057\u305f\u5834\u5408\u306f <b>[\u21C4 A \u2194 B \u5165\u308c\u66ff\u3048]</b> \u3092\u4f7f\u7528\u3002</li>"
              u"<li><b>\u8ef8</b>\u30fb<b>\u65b9\u5411</b>\u30fb<b>\u79fb\u52d5\u30e2\u30fc\u30c9</b>\u30fb<b>\u30aa\u30d5\u30bb\u30c3\u30c8</b> \u3092\u8a2d\u5b9a\u3002</li>"
              u"<li><b>[\u25B6 \u30d7\u30ec\u30d3\u30e5\u30fc]</b> \u3092\u30af\u30ea\u30c3\u30af\u3002A \u304c\u79fb\u52d5\u3057\u3001\u7d50\u679c\u3092\u78ba\u8a8d\u3067\u304d\u307e\u3059\u3002</li>"
              u"<li>\u8a2d\u5b9a\u3092\u5909\u66f4\u3057\u3066\u518d\u5ea6 <b>[\u30d7\u30ec\u30d3\u30e5\u30fc]</b> \u3092\u62bc\u3059\u3068\u3001\u524d\u56de\u306e\u30d7\u30ec\u30d3\u30e5\u30fc\u304c\u81ea\u52d5\u30ad\u30e3\u30f3\u30bb\u30eb\u3055\u308c\u307e\u3059\u3002</li>"
              u"<li>\u826f\u3051\u308c\u3070 <b>[\u2714 \u78ba\u5b9a]</b> \u3067\u78ba\u5b9a\u3001\u3084\u308a\u76f4\u3059\u306a\u3089 <b>[\u21A9 \u5143\u306b\u623b\u3059]</b> \u3067\u30ad\u30e3\u30f3\u30bb\u30eb\u3002</li>"
              u"</ol>"
              u"<p><i>\u672a\u78ba\u5b9a\u306e\u30d7\u30ec\u30d3\u30e5\u30fc\u304c\u3042\u308b\u72b6\u614b\u3067\u30c0\u30a4\u30a2\u30ed\u30b0\u3092\u9589\u3058\u308b\u3068\u3001\u81ea\u52d5\u3067\u30ad\u30e3\u30f3\u30bb\u30eb\u3055\u308c\u307e\u3059\u3002</i></p>"
              u"<h4>\u30d1\u30e9\u30e1\u30fc\u30bf</h4>"
              u"<ul>"
              u"<li><b>\u8ef8</b> \u2014 X / Y / Z\u3002\u3053\u306e\u8ef8\u306b\u6cbf\u3063\u305f\u79fb\u52d5\u306e\u307f\u884c\u3044\u307e\u3059\u3002</li>"
              u"<li><b>\u65b9\u5411</b>"
              u"<ul>"
              u"<li><b>\u81ea\u52d5</b> \u2014 A \u3068 B \u306e\u4e2d\u5fc3\u4f4d\u7f6e\u304b\u3089\u81ea\u52d5\u5224\u5b9a\u3002</li>"
              u"<li><b>+</b> / <b>\u2212</b> \u2014 \u8ef8\u65b9\u5411\u3092\u660e\u793a\u7684\u306b\u6307\u5b9a\u3002</li>"
              u"</ul></li>"
              u"<li><b>\u79fb\u52d5\u30e2\u30fc\u30c9</b>"
              u"<ul>"
              u"<li><b>\u30aa\u30d6\u30b8\u30a7\u30af\u30c8</b> \u2014 A \u306e Transform \u3054\u3068\u79fb\u52d5\u3002</li>"
              u"<li><b>\u30b3\u30f3\u30dd\u30fc\u30cd\u30f3\u30c8</b> \u2014 A \u3067\u73fe\u5728\u9078\u629e\u3057\u3066\u3044\u308b\u9802\u70b9\u30fb\u30a8\u30c3\u30b8\u30fb\u30d5\u30a7\u30fc\u30b9\u306e\u307f\u79fb\u52d5\u3002"
              u"\u9078\u629e\u306f\u30d5\u30a7\u30fc\u30b9\u3092\u5b8c\u5168\u306b\u56f2\u3080\u5fc5\u8981\u304c\u3042\u308a\u307e\u3059\uff08\u4f8b\uff1a\u30af\u30a2\u30c3\u30c9\u306e 4 \u9802\u70b9\u3059\u3079\u3066\uff09\u3002"
              u"\u5b8c\u5168\u306b\u56f2\u3081\u3066\u3044\u306a\u3044\u5834\u5408\u306f\u3001\u9694\u63a5\u30d5\u30a7\u30fc\u30b9\u306b\u62e1\u5f35\u3059\u308b\u304b\u78ba\u8a8d\u30c0\u30a4\u30a2\u30ed\u30b0\u304c\u8868\u793a\u3055\u308c\u307e\u3059\u3002</li>"
              u"</ul></li>"
              u"<li><b>\u30aa\u30d5\u30bb\u30c3\u30c8</b> \u2014 A \u3068 B \u306e\u9593\u306b\u6b8b\u3059\u9694\u305f\u308a\u8ddd\u96e2\u3002"
              u"0 \u306a\u3089\u63a5\u89e6\u3001\u8ca0\u306e\u5024\u306a\u3089 A \u3092 B \u306b\u57cb\u3081\u8fbc\u307f\u307e\u3059\u3002</li>"
              u"</ul>"
              u"<h4>\u30a2\u30eb\u30b4\u30ea\u30ba\u30e0</h4>"
              u"<p>\u307e\u305a\u30ec\u30a4\u30ad\u30e3\u30b9\u30c8\u3067\u6982\u7b97\u8ddd\u96e2\uff08\u4e0a\u9650\u5024\uff09\u3092\u7b97\u51fa\u3057\u307e\u3059\u3002"
              u"\u305d\u306e\u8ddd\u96e2\u3067\u3082\u885d\u7a81\u304c\u6b8b\u308b\u5834\u5408\uff08\u56de\u8ee2\u3057\u305f\u5f62\u72b6\u3084\u51f9\u5f62\u30e1\u30c3\u30b7\u30e5\u3067\u8d77\u3053\u308a\u307e\u3059\uff09\u306f\u3001"
              u"[0, \u4e0a\u9650\u5024] \u306e\u7bc4\u56f2\u3092\u4e8c\u5206\u63a2\u7d22\u3057\u3001\u30dd\u30ea\u30b4\u30f3\u30ec\u30d9\u30eb\u3067\u8cab\u901a\u3057\u306a\u3044\u6700\u5927\u8ddd\u96e2\u3092\u6c42\u3081\u307e\u3059\u3002"
              u"\u30ec\u30a4\u304c B \u306b\u4e00\u3064\u3082\u5f53\u305f\u3089\u306a\u3044\u5834\u5408\u306f\u3001\u30ef\u30fc\u30eb\u30c9\u539f\u70b9\u5e73\u9762\uff08Y \u8ef8\u306a\u3089 Y=0\uff09\u307e\u3067\u843d\u3068\u3057\u307e\u3059\u3002</p>",
    },
    # ---- Vertex Snap (Snap tab) --------------------------------------
    "tab_snap":             {"en": "Alignment",                     "jp": u"\u6574\u5217"},
    "vs_grp_title":         {"en": "Vertex Snap",                   "jp": u"\u30d0\u30fc\u30c6\u30c3\u30af\u30b9\u30ca\u30c3\u30d7"},
    "vs_grp_desc":          {"en": "Distance-based vertex snap. Select mesh(es) and launch.",
                             "jp": u"\u8ddd\u96e2\u30d9\u30fc\u30b9\u306e\u9802\u70b9\u30b9\u30ca\u30c3\u30d7\u3002\u30e1\u30c3\u30b7\u30e5\u3092\u9078\u629e\u3057\u3066\u8d77\u52d5\u3002"},
    "vs_btn_launch":        {"en": u"\u25B6 Launch",                "jp": u"\u25B6 \u8d77\u52d5"},
    "vs_result_title":      {"en": "Vertex Snap \u2014 Pair Results", "jp": u"\u30d0\u30fc\u30c6\u30c3\u30af\u30b9\u30ca\u30c3\u30d7 \u7d50\u679c"},
    "vs_lbl_threshold":     {"en": "Threshold:",                    "jp": u"\u3057\u304d\u3044\u5024:"},
    "vs_chk_hide_coinc":    {"en": u"Hide coincident (dist\u22480)", "jp": u"\u91cd\u8907\u9802\u70b9\u3092\u975e\u8868\u793a"},
    "vs_chk_include_same":  {"en": "Include same-mesh pairs",       "jp": u"\u540c\u30e1\u30c3\u30b7\u30e5\u3082\u691c\u67fb"},
    "vs_col_mesh_a":        {"en": "Mesh A",                        "jp": u"Mesh A"},
    "vs_col_vtx_a":         {"en": "Vtx#",                          "jp": u"Vtx#"},
    "vs_col_mesh_b":        {"en": "Mesh B",                        "jp": u"Mesh B"},
    "vs_col_vtx_b":         {"en": "Vtx#",                          "jp": u"Vtx#"},
    "vs_col_dist":          {"en": "Distance",                      "jp": u"\u8ddd\u96e2"},
    "vs_btn_snap_ab":       {"en": u"Snap A\u2192B",                "jp": u"Snap A\u2192B"},
    "vs_btn_snap_ba":       {"en": u"Snap B\u2192A",                "jp": u"Snap B\u2192A"},
    "vs_btn_snap_mid":      {"en": "Snap Mid",                      "jp": u"Snap Mid"},
    "vs_btn_confirm":       {"en": u"\u2714 Confirm",               "jp": u"\u2714 \u78ba\u5b9a"},
    "vs_btn_revert":        {"en": u"\u21A9 Revert",                "jp": u"\u21A9 \u5143\u306b\u623b\u3059"},
    "vs_btn_merge_maya":    {"en": "Merge (Maya)",                  "jp": u"Merge (Maya)"},
    "vs_snap_ab":           {"en": u"A\u2192B",                     "jp": u"A\u2192B"},
    "vs_snap_ba":           {"en": u"B\u2192A",                     "jp": u"B\u2192A"},
    "vs_snap_mid":          {"en": "Mid",                           "jp": u"Mid"},
    "vs_scope_meshes":      {"en": "Meshes: {names}",               "jp": u"\u30e1\u30c3\u30b7\u30e5: {names}"},
    "vs_scope_pairs":       {"en": "{count} pair(s) within threshold {th}",
                             "jp": u"\u3057\u304d\u3044\u5024 {th} \u5185\u306b {count} \u30da\u30a2"},
    "vs_status_no_mesh":    {"en": "Vertex Snap: no mesh selected.",
                             "jp": u"\u30d0\u30fc\u30c6\u30c3\u30af\u30b9\u30ca\u30c3\u30d7: \u30e1\u30c3\u30b7\u30e5\u304c\u9078\u629e\u3055\u308c\u3066\u3044\u307e\u305b\u3093\u3002"},
    "vs_status_no_sel":     {"en": "Select row(s) in the table.",
                             "jp": u"\u30c6\u30fc\u30d6\u30eb\u306e\u884c\u3092\u9078\u629e\u3002"},
    "vs_status_snapped":    {"en": "Snapped {count} pair(s). Confirm or Revert.",
                             "jp": u"{count}\u30da\u30a2Snap\u6e08\u307f\u3002\u78ba\u5b9a\u307e\u305f\u306f\u5143\u306b\u623b\u3059\u3002"},
    "vs_status_confirmed":  {"en": "Confirmed. {count} pair(s) snapped.",
                             "jp": u"\u78ba\u5b9a\u3002{count}\u30da\u30a2Snap\u6e08\u307f\u3002"},
    "vs_status_reverted":   {"en": "Reverted all snaps.",
                             "jp": u"\u5168\u3066\u306eSnap\u3092\u5143\u306b\u623b\u3057\u307e\u3057\u305f\u3002"},

    # ---- Edge Width Alignment (Snap tab) -----------------------------
    "es_grp_title":         {"en": "Edge Width Alignment",           "jp": u"\u30a8\u30c3\u30b8\u5e45\u306e\u6574\u5217"},
    "es_grp_desc":          {"en": "Equalise the widths of a ring of edges. Pick one edge (auto-expands along Ring or Loop) or several edges and launch.",
                             "jp": u"\u30a8\u30c3\u30b8\u306e\u5e45\u3092\u63c3\u3048\u307e\u3059\u30021\u672c\u9078\u629e\u3067\u30ea\u30f3\u30b0 or \u30eb\u30fc\u30d7\u81ea\u52d5\u62e1\u5f35\u3001\u8907\u6570\u9078\u629e\u306b\u3082\u5bfe\u5fdc\u3002"},
    "es_btn_launch":        {"en": u"\u25B6 Launch",                  "jp": u"\u25B6 \u8d77\u52d5"},
    "es_result_title":      {"en": "Edge Width Alignment",            "jp": u"\u30a8\u30c3\u30b8\u5e45\u306e\u6574\u5217"},
    "es_scope":             {"en": "{count} edge(s) selected.",
                             "jp": u"{count} \u672c\u306e\u30a8\u30c3\u30b8\u3092\u9078\u629e\u4e2d\u3002"},
    "es_scope_with_warn":   {"en": "{count} edge(s) selected. {warn} edge(s) could not be A/B-coloured cleanly.",
                             "jp": u"{count} \u672c\u306e\u30a8\u30c3\u30b8\u3092\u9078\u629e\u4e2d\u3002{warn} \u672c\u306f A/B \u5206\u985e\u304c\u4e0d\u78ba\u5b9a\u3067\u3059\u3002"},
    "es_lbl_uniform":       {"en": "Target width:",                   "jp": u"\u76ee\u6a19\u5e45:"},
    "es_lbl_uniform_hint":  {"en": "(used by the buttons below)",     "jp": u"\uff08\u4e0b\u306e\u30dc\u30bf\u30f3\u3067\u4f7f\u7528\uff09"},
    "es_chk_per_region":    {"en": "Per-region average",              "jp": u"\u533a\u9593\u3054\u3068\u306e\u5e73\u5747"},
    "es_chk_per_region_tip": {"en": "When on, each row is aligned to the average width of its own region (ignores the target-width spin). Turn off to use the spin value as a single global target for every row.",
                              "jp": u"\u30aa\u30f3\u306e\u9593\u3001\u5404\u884c\u306f\u305d\u306e\u533a\u9593\u306e\u5e73\u5747\u5e45\u306b\u63c3\u3048\u3089\u308c\u307e\u3059\uff08\u76ee\u6a19\u5e45\u30b9\u30d4\u30f3\u306f\u4f7f\u308f\u308c\u307e\u305b\u3093\uff09\u3002\u30aa\u30d5\u306b\u3059\u308b\u3068\u3001\u30b9\u30d4\u30f3\u306e\u5024\u304c\u5168\u884c\u5171\u901a\u306e\u76ee\u6a19\u5024\u306b\u306a\u308a\u307e\u3059\u3002"},
    "es_lbl_corner_angle":  {"en": "Corner split:",                   "jp": u"\u30b3\u30fc\u30ca\u30fc\u5206\u5272:"},
    "es_lbl_corner_hint":   {"en": "Split edges into regions at bends wider than this angle.",
                             "jp": u"\u3053\u306e\u89d2\u5ea6\u3088\u308a\u5927\u304d\u304f\u66f2\u304c\u308b\u7b87\u6240\u3067\u30a8\u30c3\u30b8\u3092\u533a\u9593\u306b\u5206\u5272\u3057\u307e\u3059\u3002"},
    "es_scope_region_count": {"en": "{regions} region(s)",
                               "jp": u"{regions} \u533a\u9593"},
    "es_lbl_expand_mode":   {"en": "Auto-select direction:",         "jp": u"\u81ea\u52d5\u9078\u629e\u306e\u65b9\u5411:"},
    "es_mode_ring":         {"en": "Ring \u2014 horizontal (belt direction)",
                             "jp": u"\u30ea\u30f3\u30b0 \u2014 \u6a2a\u65b9\u5411\uff08\u30d9\u30eb\u30c8\u5dfb\u304d\uff09"},
    "es_mode_loop":         {"en": "Loop \u2014 vertical (perpendicular)",
                             "jp": u"\u30eb\u30fc\u30d7 \u2014 \u7e26\u65b9\u5411\uff08\u5782\u76f4\uff09"},
    "es_col_edge":          {"en": "Edge",                            "jp": u"\u30a8\u30c3\u30b8"},
    "es_col_length":        {"en": "Length",                          "jp": u"\u9577\u3055"},
    "es_col_region":        {"en": "Region",                          "jp": u"\u533a\u9593"},
    "es_col_status":        {"en": "A/B",                             "jp": u"A/B"},
    "es_col_log":           {"en": "Applied",                         "jp": u"\u9069\u7528\u6e08"},
    "es_status_ok":         {"en": "OK",                              "jp": u"OK"},
    "es_status_fallback":   {"en": "!",                               "jp": u"!"},
    "es_btn_align_a":       {"en": "Keep A side",                     "jp": u"A \u5074\u3092\u56fa\u5b9a"},
    "es_btn_align_b":       {"en": "Keep B side",                     "jp": u"B \u5074\u3092\u56fa\u5b9a"},
    "es_btn_align_mid":     {"en": "Keep centre",                     "jp": u"\u4e2d\u592e\u3092\u56fa\u5b9a"},
    "es_btn_confirm":       {"en": u"\u2714 Confirm",                  "jp": u"\u2714 \u78ba\u5b9a"},
    "es_btn_revert":        {"en": u"\u21A9 Revert",                   "jp": u"\u21A9 \u5143\u306b\u623b\u3059"},
    "es_log_align_a":       {"en": u"keep A",                          "jp": u"A \u56fa\u5b9a"},
    "es_log_align_b":       {"en": u"keep B",                          "jp": u"B \u56fa\u5b9a"},
    "es_log_align_mid":     {"en": u"keep centre",                     "jp": u"\u4e2d\u592e\u56fa\u5b9a"},
    "es_log_uniform_with_anchor": {"en": "{anchor}, len={value}",
                                    "jp": u"{anchor}, \u5e45={value}"},
    "es_status_no_edges":   {"en": "Edge Width Alignment: select at least one edge.",
                             "jp": u"\u30a8\u30c3\u30b8\u5e45\u306e\u6574\u5217: \u30a8\u30c3\u30b8\u3092 1 \u672c\u4ee5\u4e0a\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "es_status_no_sel":     {"en": "Select row(s) in the table.",
                             "jp": u"\u30c6\u30fc\u30d6\u30eb\u3067\u884c\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "es_status_snapped":    {"en": "Applied to {count} edge(s). Confirm or Revert.",
                             "jp": u"{count} \u672c\u306e\u30a8\u30c3\u30b8\u306b\u9069\u7528\u3002\u78ba\u5b9a\u307e\u305f\u306f\u5143\u306b\u623b\u3059\u3002"},
    "es_status_confirmed":  {"en": "Confirmed. {count} edge(s) aligned.",
                             "jp": u"\u78ba\u5b9a\u3002{count} \u672c\u306e\u30a8\u30c3\u30b8\u3092\u63c3\u3048\u307e\u3057\u305f\u3002"},
    "es_status_reverted":   {"en": "Reverted all edge alignments.",
                             "jp": u"\u5168\u3066\u306e\u30a8\u30c3\u30b8\u63c3\u3048\u3092\u5143\u306b\u623b\u3057\u307e\u3057\u305f\u3002"},
    "es_status_bad_length": {"en": "Target width must be greater than 0.",
                             "jp": u"\u76ee\u6a19\u5e45\u306f 0 \u3088\u308a\u5927\u304d\u3044\u5fc5\u8981\u304c\u3042\u308a\u307e\u3059\u3002"},

    # Belt-width vs edge-length mode.
    "es_lbl_mode":          {"en": "Mode:",                           "jp": u"\u30e2\u30fc\u30c9\uff1a"},
    "es_mode_length":       {"en": "Edge length",                     "jp": u"\u30a8\u30c3\u30b8\u9577\u3055"},
    "es_mode_belt":         {"en": "Belt width (along brims)",        "jp": u"\u30d9\u30eb\u30c8\u5e45\uff08\u30d5\u30c1\u6cbf\u3044\uff09"},
    "es_lbl_mode_hint":     {"en": "Belt width slides endpoints along their detected edge loops.",
                             "jp": u"\u30d9\u30eb\u30c8\u5e45\u30e2\u30fc\u30c9\u306f\u81ea\u52d5\u691c\u51fa\u3057\u305f\u30a8\u30c3\u30b8\u30eb\u30fc\u30d7\u306b\u6cbf\u3063\u3066\u7aef\u70b9\u3092\u30b9\u30e9\u30a4\u30c9\u3055\u305b\u307e\u3059\u3002"},
    "es_status_mode_length": {"en": "Mode: edge length (fastest, may distort at corners).",
                               "jp": u"\u30e2\u30fc\u30c9\uff1a\u30a8\u30c3\u30b8\u9577\u3055\uff08\u9ad8\u901f\u3001\u30b3\u30fc\u30ca\u30fc\u3067\u6b6a\u3080\u5834\u5408\u3042\u308a\uff09"},
    "es_status_mode_belt":  {"en": "Mode: belt width (endpoints slide along detected edge loops).",
                             "jp": u"\u30e2\u30fc\u30c9\uff1a\u30d9\u30eb\u30c8\u5e45\uff08\u7aef\u70b9\u306f\u691c\u51fa\u3055\u308c\u305f\u30a8\u30c3\u30b8\u30eb\u30fc\u30d7\u3092\u30b9\u30e9\u30a4\u30c9\uff09"},
    "es_chip_header":       {"en": "Region:",                          "jp": u"\u533a\u9593\uff1a"},
    "es_chip_label":        {"en": u"#{cid}  ({n} / {avg})",
                             "jp": u"#{cid}\u3000({n} / {avg})"},
    "es_btn_select_all":    {"en": "Select all",                       "jp": u"\u5168\u9078\u629e"},
    "es_status_region_selected": {"en": "Region #{cid} selected: {count} edge(s), avg {avg}.",
                                   "jp": u"\u533a\u9593 #{cid} \u3092\u9078\u629e\uff1a{count} \u672c\u3001\u5e73\u5747 {avg}"},

    # ---- Vertex Align (Alignment tab) --------------------------------
    "va_grp_title":         {"en": "Vertex Align",                    "jp": u"\u9802\u70b9\u6574\u5217"},
    "va_grp_desc":          {"en": "Project selected vertices onto a line or plane.",
                             "jp": u"\u9078\u629e\u3057\u305f\u9802\u70b9\u3092\u76f4\u7dda\u3084\u5e73\u9762\u306b\u6574\u5217\u3055\u305b\u307e\u3059\u3002"},
    "va_btn_launch":        {"en": u"\u25B6 Launch",                   "jp": u"\u25B6 \u8d77\u52d5"},
    "va_dlg_title":         {"en": "Vertex Align",                    "jp": u"\u9802\u70b9\u6574\u5217"},
    "va_tab_linear3d":      {"en": "Linear 3D",                       "jp": u"\u76f4\u7dda\u5316 3D"},
    "va_tab_linear2d":      {"en": "Linear 2D (view)",                "jp": u"\u76f4\u7dda\u5316 2D\uff08\u30d3\u30e5\u30fc\uff09"},
    "va_tab_flatten":       {"en": "Flatten (3 points)",              "jp": u"\u5e73\u9762\u5316\uff083 \u9802\u70b9\uff09"},
    "va_lbl_reference":     {"en": "Reference",                       "jp": u"\u57fa\u6e96"},
    "va_lbl_view":          {"en": "View",                            "jp": u"\u30d3\u30e5\u30fc"},
    "va_lbl_drop_mode":     {"en": "Projection",                      "jp": u"\u6295\u5f71\u65b9\u5411"},
    "va_lbl_pos_empty":     {"en": "Pos{n}: (not set)",               "jp": u"Pos{n}\uff1a\u672a\u8a2d\u5b9a"},
    "va_lbl_pos_value":     {"en": "Pos{n}: ({x}, {y}, {z})",          "jp": u"Pos{n}\uff1a\uff08{x}, {y}, {z}\uff09"},
    "va_btn_set_pos":       {"en": "Set Pos{n}",                      "jp": u"Pos{n} \u53d6\u5f97"},
    "va_btn_auto_view":     {"en": u"\u2190 Auto",                     "jp": u"\u2190 \u81ea\u52d5"},
    "va_btn_preview":       {"en": u"\u25B6 Preview",                  "jp": u"\u25B6 \u30d7\u30ec\u30d3\u30e5\u30fc"},
    "va_btn_confirm":       {"en": u"\u2714 Confirm",                  "jp": u"\u2714 \u78ba\u5b9a"},
    "va_btn_revert":        {"en": u"\u21A9 Revert",                   "jp": u"\u21A9 \u5143\u306b\u623b\u3059"},

    # Tab-specific labels.
    "va_l3d_desc":          {"en": "Project every selected vertex onto the straight line between two reference points.",
                             "jp": u"\u9078\u629e\u9802\u70b9\u3092 2 \u3064\u306e\u57fa\u6e96\u70b9\u3092\u7d50\u3076\u76f4\u7dda\u4e0a\u306b\u6295\u5f71\u3057\u307e\u3059\u3002"},
    "va_l3d_auto":          {"en": "Auto (end-points from selection / edge chain)",
                             "jp": u"\u81ea\u52d5\uff08\u9078\u629e\u306e\u7aef\u70b9 / \u30a8\u30c3\u30b8\u9023\u9396\uff09"},
    "va_l3d_manual":        {"en": "Manual (capture Pos1 / Pos2)",
                             "jp": u"\u624b\u52d5\uff08Pos1 / Pos2 \u3092\u6307\u5b9a\uff09"},
    "va_l3d_chk_equal":     {"en": "Equidistant (edge chain only)",
                             "jp": u"\u7b49\u9593\u9694\uff08\u30a8\u30c3\u30b8\u9023\u9396\u9078\u629e\u6642\u306e\u307f\uff09"},
    "va_l3d_chk_equal_hint": {"en": "Select an ordered edge chain; vertices are redistributed evenly between the two endpoints.",
                              "jp": u"\u6709\u5e8f\u306a\u30a8\u30c3\u30b8\u9023\u9396\u3092\u9078\u629e\u3059\u308b\u3068\u3001\u4e21\u7aef\u70b9\u306e\u9593\u306b\u7b49\u9593\u9694\u3067\u9802\u70b9\u3092\u518d\u914d\u7f6e\u3057\u307e\u3059\u3002"},

    "va_l2d_desc":          {"en": "Flatten vertices onto a line in an orthographic view (the view-depth axis is preserved).",
                             "jp": u"\u6b63\u6295\u5f71\u30d3\u30e5\u30fc\u4e0a\u306e\u76f4\u7dda\u306b\u9802\u70b9\u3092\u6574\u5217\u3057\u307e\u3059\uff08\u30d3\u30e5\u30fc\u5965\u884c\u304d\u306e\u8ef8\u306f\u7dad\u6301\uff09\u3002"},
    "va_l2d_ref_hint":      {"en": "Reference line is taken automatically from the selection's extremes along the view's horizontal axis.",
                             "jp": u"\u57fa\u6e96\u76f4\u7dda\u306f\u30d3\u30e5\u30fc\u306e\u6c34\u5e73\u8ef8\u306b\u6cbf\u3063\u305f\u9078\u629e\u306e\u7aef\u70b9\u304b\u3089\u81ea\u52d5\u3067\u53d6\u5f97\u3055\u308c\u307e\u3059\u3002"},
    "va_view_top":          {"en": "Top",                             "jp": u"Top"},
    "va_view_front":        {"en": "Front",                           "jp": u"Front"},
    "va_view_side":         {"en": "Side",                            "jp": u"Side"},
    "va_drop_shortest":     {"en": "Shortest",                        "jp": u"\u6700\u77ed"},
    "va_drop_horizontal":   {"en": "Horizontal",                      "jp": u"\u6c34\u5e73"},
    "va_drop_vertical":     {"en": "Vertical",                        "jp": u"\u5782\u76f4"},

    "va_flat_desc":         {"en": "Project every selected vertex onto the plane defined by three reference points.",
                             "jp": u"\u9078\u629e\u9802\u70b9\u3092 3 \u3064\u306e\u57fa\u6e96\u70b9\u3067\u5b9a\u307e\u308b\u5e73\u9762\u306b\u6295\u5f71\u3057\u307e\u3059\u3002"},
    "va_flat_auto":         {"en": "Auto (best 3 points from selection)",
                             "jp": u"\u81ea\u52d5\uff08\u9078\u629e\u304b\u3089 3 \u70b9\u3092\u81ea\u52d5\u62bd\u51fa\uff09"},
    "va_flat_manual":       {"en": "Manual (capture Pos1 / Pos2 / Pos3)",
                             "jp": u"\u624b\u52d5\uff08Pos1 / Pos2 / Pos3 \u3092\u6307\u5b9a\uff09"},
    "va_flat_auto_hint":    {"en": "Auto mode needs at least 3 non-colinear vertices in the selection.",
                             "jp": u"\u81ea\u52d5\u30e2\u30fc\u30c9\u306f\u9078\u629e\u5185\u306b 3 \u9802\u70b9\u4ee5\u4e0a\uff08\u540c\u4e00\u76f4\u7dda\u4e0a\u4ee5\u5916\uff09\u304c\u5fc5\u8981\u3067\u3059\u3002"},

    # Statuses.
    "va_status_ready":      {"en": "Ready. Select vertices and Preview.",
                             "jp": u"\u6e96\u5099\u5b8c\u4e86\u3002\u9802\u70b9\u3092\u9078\u629e\u3057\u3066\u30d7\u30ec\u30d3\u30e5\u30fc\u3092\u3002"},
    "va_status_no_selection": {"en": "Vertex Align: select at least one vertex.",
                                "jp": u"\u9802\u70b9\u6574\u5217\uff1a\u9802\u70b9\u3092 1 \u3064\u4ee5\u4e0a\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "va_status_no_sel_for_pos": {"en": "Select the vertex/vertices to capture as Pos.",
                                  "jp": u"Pos \u3068\u3057\u3066\u53d6\u5f97\u3059\u308b\u9802\u70b9\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "va_status_pos_captured": {"en": "Pos{n} captured.",
                                "jp": u"Pos{n} \u3092\u53d6\u5f97\u3057\u307e\u3057\u305f\u3002"},
    "va_status_manual_not_set": {"en": "Capture all reference positions first (Manual mode).",
                                  "jp": u"\u624b\u52d5\u30e2\u30fc\u30c9\u306f\u307e\u305a\u3059\u3079\u3066\u306e\u57fa\u6e96\u70b9\u3092\u53d6\u5f97\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "va_status_need_2_verts": {"en": "Need at least 2 vertices (or an edge) to define the line.",
                                "jp": u"\u76f4\u7dda\u3092\u6c7a\u3081\u308b\u306b\u306f 2 \u9802\u70b9\u4ee5\u4e0a\uff08\u307e\u305f\u306f\u30a8\u30c3\u30b8\uff09\u304c\u5fc5\u8981\u3067\u3059\u3002"},
    "va_status_flat_autofail": {"en": "Auto plane fit failed. Pick manual Pos1/Pos2/Pos3.",
                                 "jp": u"\u81ea\u52d5\u5e73\u9762\u63a8\u5b9a\u304c\u5931\u6557\u3057\u307e\u3057\u305f\u3002\u624b\u52d5\u3067 Pos1/Pos2/Pos3 \u3092\u6307\u5b9a\u3057\u3066\u304f\u3060\u3055\u3044\u3002"},
    "va_status_nothing_to_move": {"en": "No vertices to move.",
                                   "jp": u"\u79fb\u52d5\u5bfe\u8c61\u306e\u9802\u70b9\u304c\u3042\u308a\u307e\u305b\u3093\u3002"},
    "va_status_no_ortho_view": {"en": "Focus on a Top / Front / Side view to auto-detect.",
                                 "jp": u"Top / Front / Side \u306e\u3044\u305a\u308c\u304b\u306b\u30d5\u30a9\u30fc\u30ab\u30b9\u3057\u3066\u304b\u3089\u81ea\u52d5\u691c\u77e5\u3092\u3054\u5229\u7528\u304f\u3060\u3055\u3044\u3002"},
    "va_status_view_detected": {"en": "View detected: {view}.",
                                 "jp": u"\u30d3\u30e5\u30fc\u3092\u691c\u77e5\u3057\u307e\u3057\u305f\uff1a{view}"},
    "va_status_preview_linear_3d": {"en": "Preview: {count} vertex/vertices aligned on 3D line. Confirm or Revert.",
                                      "jp": u"\u30d7\u30ec\u30d3\u30e5\u30fc\uff1a{count} \u9802\u70b9\u3092 3D \u76f4\u7dda\u306b\u6574\u5217\u3002\u78ba\u5b9a\u307e\u305f\u306f\u5143\u306b\u623b\u3059\u3002"},
    "va_status_preview_linear_2d": {"en": "Preview: {count} vertex/vertices aligned ({view} view). Confirm or Revert.",
                                      "jp": u"\u30d7\u30ec\u30d3\u30e5\u30fc\uff1a{count} \u9802\u70b9\u3092\u6574\u5217\uff08{view} \u30d3\u30e5\u30fc\uff09\u3002\u78ba\u5b9a\u307e\u305f\u306f\u5143\u306b\u623b\u3059\u3002"},
    "va_status_preview_flatten": {"en": "Preview: {count} vertex/vertices flattened to plane. Confirm or Revert.",
                                    "jp": u"\u30d7\u30ec\u30d3\u30e5\u30fc\uff1a{count} \u9802\u70b9\u3092\u5e73\u9762\u306b\u6295\u5f71\u3002\u78ba\u5b9a\u307e\u305f\u306f\u5143\u306b\u623b\u3059\u3002"},
    "va_status_confirmed":  {"en": "Vertex Align confirmed.",
                             "jp": u"\u9802\u70b9\u6574\u5217\u3092\u78ba\u5b9a\u3057\u307e\u3057\u305f\u3002"},
    "va_status_reverted":   {"en": "Vertex Align reverted.",
                             "jp": u"\u9802\u70b9\u6574\u5217\u3092\u5143\u306b\u623b\u3057\u307e\u3057\u305f\u3002"},
}

# Python 2/3 unicode type compatibility for tr()
try:
    _TEXT_TYPE = unicode  # Python 2
except NameError:
    _TEXT_TYPE = str       # Python 3


def _to_unicode(s):
    """Force a value into unicode (Python 2) / str (Python 3).

    On Maya 2018 + Japanese Windows (CP932 locale), str.format() with
    a mix of bytes-str and unicode triggers ASCII auto-decoding which
    fails for non-ASCII characters. Returning unicode-only from tr()
    eliminates this entire class of error.
    """
    if isinstance(s, _TEXT_TYPE):
        return s
    if isinstance(s, bytes):
        try:
            return s.decode("utf-8")
        except Exception:
            return s.decode("utf-8", "replace")
    # int / float / other -> stringify safely
    try:
        return _TEXT_TYPE(s)
    except Exception:
        return _TEXT_TYPE(repr(s))


def tr(key, **kw):
    e = _STRINGS.get(key, {})
    if isinstance(e, dict) and ("en" in e or "jp" in e):
        t = e.get(_current_lang, e.get("en", key))
    else:
        t = key
    # Force unicode to avoid Python 2 str/unicode mixing errors
    t = _to_unicode(t)
    if kw:
        # Also unicode-ify kw values so .format(...) stays unicode
        kw = {k: _to_unicode(v) for k, v in kw.items()}
        try:
            t = t.format(**kw)
        except Exception:
            pass
    return t
# ---------------------------------------------------------------------------
# CollisionDetector  (Pure Python — no Maya dependency)
# ---------------------------------------------------------------------------
_EPSILON = 1e-7   # tolerance for floating-point comparisons


def _sub(a, b):   return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def _cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def _dot(a, b):   return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def _len(a):      return math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])
def _norm(a):
    l = _len(a)
    return (a[0]/l, a[1]/l, a[2]/l) if l > 1e-15 else (0.0, 0.0, 0.0)

# ---------------------------------------------------------------------------
# AABB
# ---------------------------------------------------------------------------
class _AABB(object):
    __slots__ = ("mn", "mx")

    def __init__(self, mn, mx):
        self.mn = mn
        self.mx = mx

    def intersects(self, o):
        return (self.mn[0] <= o.mx[0] and self.mx[0] >= o.mn[0] and
                self.mn[1] <= o.mx[1] and self.mx[1] >= o.mn[1] and
                self.mn[2] <= o.mx[2] and self.mx[2] >= o.mn[2])

    @staticmethod
    def from_tri(tri):
        xs = (tri[0][0], tri[1][0], tri[2][0])
        ys = (tri[0][1], tri[1][1], tri[2][1])
        zs = (tri[0][2], tri[1][2], tri[2][2])
        return _AABB((min(xs), min(ys), min(zs)),
                     (max(xs), max(ys), max(zs)))

    def merge(self, o):
        return _AABB(
            (min(self.mn[0], o.mn[0]), min(self.mn[1], o.mn[1]), min(self.mn[2], o.mn[2])),
            (max(self.mx[0], o.mx[0]), max(self.mx[1], o.mx[1]), max(self.mx[2], o.mx[2])))

    def surface_area(self):
        dx = self.mx[0] - self.mn[0]
        dy = self.mx[1] - self.mn[1]
        dz = self.mx[2] - self.mn[2]
        return 2.0 * (dx*dy + dy*dz + dz*dx)


# ---------------------------------------------------------------------------
# BVH
# ---------------------------------------------------------------------------
class _BVHNode(object):
    __slots__ = ("aabb", "left", "right", "tri_idx")
    def __init__(self):
        self.aabb    = None
        self.left    = None
        self.right   = None
        self.tri_idx = -1   # >= 0: leaf node


def _centroid_ax(tri, axis):
    return (tri[0][axis] + tri[1][axis] + tri[2][axis]) / 3.0


def _build_bvh(tris, indices):
    node = _BVHNode()
    box = _AABB.from_tri(tris[indices[0]])
    for i in indices[1:]:
        box = box.merge(_AABB.from_tri(tris[i]))
    node.aabb = box

    if len(indices) == 1:
        node.tri_idx = indices[0]
        return node

    if len(indices) == 2:
        l = _BVHNode(); l.aabb = _AABB.from_tri(tris[indices[0]]); l.tri_idx = indices[0]
        r = _BVHNode(); r.aabb = _AABB.from_tri(tris[indices[1]]); r.tri_idx = indices[1]
        node.left = l; node.right = r
        return node

    c = [(_centroid_ax(tris[i], 0), _centroid_ax(tris[i], 1), _centroid_ax(tris[i], 2))
         for i in indices]
    spans = [max(v[ax] for v in c) - min(v[ax] for v in c) for ax in range(3)]
    axis = spans.index(max(spans))

    sorted_idx = sorted(indices, key=lambda i: _centroid_ax(tris[i], axis))
    mid = len(sorted_idx) // 2
    node.left  = _build_bvh(tris, sorted_idx[:mid])
    node.right = _build_bvh(tris, sorted_idx[mid:])
    return node


def _refit_bvh(node, tris):
    """
    Recursively update AABBs in an existing BVH using new triangle positions.
    The tree structure (left/right/tri_idx) is preserved — only AABBs change.
    This is much faster than rebuilding the BVH from scratch, since the
    topology doesn't change between animation frames.
    """
    if node is None:
        return None
    if node.tri_idx >= 0:
        # Leaf: rebuild AABB from the current triangle position
        node.aabb = _AABB.from_tri(tris[node.tri_idx])
        return node.aabb
    left_aabb = _refit_bvh(node.left, tris)
    right_aabb = _refit_bvh(node.right, tris)
    if left_aabb is None:
        node.aabb = right_aabb
    elif right_aabb is None:
        node.aabb = left_aabb
    else:
        node.aabb = left_aabb.merge(right_aabb)
    return node.aabb


# ---------------------------------------------------------------------------
# Triangle-Triangle intersection  (Moller 1997, corrected)
# ---------------------------------------------------------------------------
def _sgn(x):
    if x > _EPSILON:  return  1
    if x < -_EPSILON: return -1
    return 0


def _coplanar_2d_sat(t1, t2, n):
    """Strict 2D SAT for coplanar triangles. Touching edges return True."""
    nx, ny, nz = abs(n[0]), abs(n[1]), abs(n[2])
    if nx <= ny and nx <= nz: u = _norm((0.0, n[2], -n[1]))
    elif ny <= nz:             u = _norm((n[2], 0.0, -n[0]))
    else:                      u = _norm((n[1], -n[0], 0.0))
    v = _norm(_cross(n, u))

    def p2(pt): return (_dot(pt, u), _dot(pt, v))
    p1 = [p2(p) for p in t1]
    p2_ = [p2(p) for p in t2]

    for pts_a, pts_b in [(p1, p2_), (p2_, p1)]:
        for i in range(3):
            j = (i + 1) % 3
            ex = pts_a[j][0] - pts_a[i][0]
            ey = pts_a[j][1] - pts_a[i][1]
            al = math.sqrt(ex*ex + ey*ey)
            if al < 1e-12: continue
            ax = -ey / al;  ay = ex / al
            a_d = [pt[0]*ax + pt[1]*ay for pt in pts_a]
            b_d = [pt[0]*ax + pt[1]*ay for pt in pts_b]
            if max(b_d) < min(a_d) - _EPSILON or max(a_d) < min(b_d) - _EPSILON:
                return False
    return True


def _moller_interval(coords, dists):
    """
    Compute [t_min, t_max] scalar interval on the intersection line
    for one triangle, given projected coords and plane distances.

    Correctly handles all cases:
      - Normal case: one isolated vertex (opposite sign from the other two)
      - Vertex-on-plane: one dist == 0 (vertex lies exactly on opposite plane)
    """
    d0, d1, d2 = dists[0], dists[1], dists[2]
    p0, p1, p2 = coords[0], coords[1], coords[2]

    s = (_sgn(d0), _sgn(d1), _sgn(d2))
    pos = [i for i in range(3) if s[i] > 0]
    neg = [i for i in range(3) if s[i] < 0]
    zer = [i for i in range(3) if s[i] == 0]

    c = [(p0, d0), (p1, d1), (p2, d2)]

    if len(zer) == 2:
        # Two vertices on plane
        pts = [c[i][0] for i in zer]
        return min(pts), max(pts)

    if len(zer) == 1:
        # One vertex on plane — it is an endpoint
        on = c[zer[0]][0]
        oth = [i for i in range(3) if i != zer[0]]
        ia, ib = oth[0], oth[1]
        if s[ia] != 0 and s[ib] != 0 and s[ia] != s[ib]:
            den = c[ia][1] - c[ib][1]
            if abs(den) > 1e-15:
                t = c[ia][0] + (c[ib][0] - c[ia][0]) * c[ia][1] / den
            else:
                t = on
            return (min(on, t), max(on, t))
        return on, on

    # Normal case: one isolated vertex
    if len(pos) == 1 and len(neg) == 2:
        iso = pos[0]; oth = neg
    elif len(neg) == 1 and len(pos) == 2:
        iso = neg[0]; oth = pos
    else:
        vals = [p0, p1, p2]; return min(vals), max(vals)

    pi_ = c[iso][0]; di_ = c[iso][1]
    j,  k  = oth[0], oth[1]
    pj = c[j][0];  dj = c[j][1]
    pk = c[k][0];  dk = c[k][1]

    den_j = di_ - dj;  den_k = di_ - dk
    tj = (pi_ + (pj - pi_) * di_ / den_j) if abs(den_j) > 1e-15 else pi_
    tk = (pi_ + (pk - pi_) * di_ / den_k) if abs(den_k) > 1e-15 else pi_

    return min(tj, tk), max(tj, tk)


def _tri_tri_intersect(t1, t2):
    """
    Robust Moller (1997) triangle-triangle intersection.
    Returns (hit: bool, depth: float, point: tuple|None,
             n1: tuple|None, n2: tuple|None).
    """
    EPS = 1e-6

    # Compute plane of t2 (normalized)
    e1 = _sub(t2[1], t2[0])
    e2 = _sub(t2[2], t2[0])
    n2_raw = _cross(e1, e2)
    n2_len = _len(n2_raw)
    if n2_len < 1e-12:
        return False, 0.0, None, None, None
    n2 = (n2_raw[0]/n2_len, n2_raw[1]/n2_len, n2_raw[2]/n2_len)
    d2 = -_dot(n2, t2[0])

    # Signed distances of t1 vertices to plane of t2
    dv = [_dot(n2, t1[i]) + d2 for i in range(3)]
    # Clamp tiny values to zero
    dv = [0.0 if abs(d) < EPS else d for d in dv]

    # Early reject: all on same side
    if (dv[0] > 0 and dv[1] > 0 and dv[2] > 0) or \
       (dv[0] < 0 and dv[1] < 0 and dv[2] < 0):
        return False, 0.0, None, None, None

    # Compute plane of t1 (normalized)
    e1 = _sub(t1[1], t1[0])
    e2 = _sub(t1[2], t1[0])
    n1_raw = _cross(e1, e2)
    n1_len = _len(n1_raw)
    if n1_len < 1e-12:
        return False, 0.0, None, None, None
    n1 = (n1_raw[0]/n1_len, n1_raw[1]/n1_len, n1_raw[2]/n1_len)
    d1 = -_dot(n1, t1[0])

    # Signed distances of t2 vertices to plane of t1
    du = [_dot(n1, t2[i]) + d1 for i in range(3)]
    du = [0.0 if abs(d) < EPS else d for d in du]

    if (du[0] > 0 and du[1] > 0 and du[2] > 0) or \
       (du[0] < 0 and du[1] < 0 and du[2] < 0):
        return False, 0.0, None, None, None

    # Intersection line direction = cross of normals
    D = _cross(n1, n2)
    d_len = _len(D)

    # Coplanar / near-parallel case
    # n1 and n2 are both unit vectors, so |n1 × n2| = sin(angle between planes).
    # If d_len < 0.01, the planes are within ~0.57 degrees of parallel —
    # treat as coplanar to avoid numerical instability.
    if d_len < 0.01:
        hit = _coplanar_2d_sat(t1, t2, n1)
        cx = (t1[0][0]+t1[1][0]+t1[2][0]) / 3.0
        cy = (t1[0][1]+t1[1][1]+t1[2][1]) / 3.0
        cz = (t1[0][2]+t1[1][2]+t1[2][2]) / 3.0
        return hit, 0.0, (cx, cy, cz), n1, n2

    # Normalized intersection line direction
    Dn = (D[0]/d_len, D[1]/d_len, D[2]/d_len)

    # Compute scalar intervals using 3D edge-plane intersections
    t1_lo, t1_hi = _compute_interval_3d(t1, dv, Dn)
    if t1_lo is None:
        return False, 0.0, None, None, None
    t2_lo, t2_hi = _compute_interval_3d(t2, du, Dn)
    if t2_lo is None:
        return False, 0.0, None, None, None

    # Check overlap of the two intervals
    ov_lo = max(t1_lo, t2_lo)
    ov_hi = min(t1_hi, t2_hi)

    if ov_lo > ov_hi + EPS:
        return False, 0.0, None, None, None

    # Overlap length in world units along the intersection line
    overlap_len = max(0.0, ov_hi - ov_lo)

    cx = (t1[0][0]+t1[1][0]+t1[2][0]) / 3.0
    cy = (t1[0][1]+t1[1][1]+t1[2][1]) / 3.0
    cz = (t1[0][2]+t1[1][2]+t1[2][2]) / 3.0
    return True, overlap_len, (cx, cy, cz), n1, n2


def _compute_interval_3d(verts, dists, Dn):
    """
    Given triangle vertices, signed distances to the opposite plane,
    and the unit direction of the intersection line Dn,
    compute the scalar interval [t_lo, t_hi] along Dn where the
    triangle crosses the opposite plane (i.e. the 3D points where
    edges pierce the plane, projected onto Dn).
    Returns (t_lo, t_hi) or (None, None) if no crossing.
    """
    signs = []
    for d in dists:
        if d > 0: signs.append(1)
        elif d < 0: signs.append(-1)
        else: signs.append(0)

    pos = [i for i in range(3) if signs[i] > 0]
    neg = [i for i in range(3) if signs[i] < 0]
    zer = [i for i in range(3) if signs[i] == 0]

    # Helper: project 3D point onto Dn
    def proj(pt):
        return _dot(Dn, pt)

    # All zero: shouldn't happen here (coplanar handled separately)
    if len(zer) == 3:
        return None, None

    # Two zero: the edge between them lies on the plane
    if len(zer) == 2:
        t_a = proj(verts[zer[0]])
        t_b = proj(verts[zer[1]])
        return min(t_a, t_b), max(t_a, t_b)

    # One zero: vertex on plane + possibly an edge crossing
    if len(zer) == 1:
        z = zer[0]
        others = [i for i in range(3) if i != z]
        a, b = others[0], others[1]
        t_z = proj(verts[z])
        if signs[a] * signs[b] < 0:
            # Edge a-b pierces the plane in 3D
            t_param = dists[a] / (dists[a] - dists[b])
            pt = (verts[a][0] + (verts[b][0] - verts[a][0]) * t_param,
                  verts[a][1] + (verts[b][1] - verts[a][1]) * t_param,
                  verts[a][2] + (verts[b][2] - verts[a][2]) * t_param)
            t_cross = proj(pt)
            return min(t_z, t_cross), max(t_z, t_cross)
        else:
            return t_z, t_z

    # Normal case: one isolated vertex, two on the other side
    if len(pos) == 1 and len(neg) == 2:
        iso = pos[0]
        others = neg
    elif len(neg) == 1 and len(pos) == 2:
        iso = neg[0]
        others = pos
    else:
        return None, None

    a, b = others[0], others[1]
    # Edge iso-a pierces the plane at:
    t_param_a = dists[iso] / (dists[iso] - dists[a])
    pt_a = (verts[iso][0] + (verts[a][0] - verts[iso][0]) * t_param_a,
            verts[iso][1] + (verts[a][1] - verts[iso][1]) * t_param_a,
            verts[iso][2] + (verts[a][2] - verts[iso][2]) * t_param_a)
    # Edge iso-b pierces at:
    t_param_b = dists[iso] / (dists[iso] - dists[b])
    pt_b = (verts[iso][0] + (verts[b][0] - verts[iso][0]) * t_param_b,
            verts[iso][1] + (verts[b][1] - verts[iso][1]) * t_param_b,
            verts[iso][2] + (verts[b][2] - verts[iso][2]) * t_param_b)

    t_a = proj(pt_a)
    t_b = proj(pt_b)
    return min(t_a, t_b), max(t_a, t_b)


def _compute_interval(proj, dists):
    """Legacy wrapper — kept for backward compat but not used."""
    return None, None

# ---------------------------------------------------------------------------
# Dual-BVH traversal
# ---------------------------------------------------------------------------
def _query_bvh(na, tris_a, nb, tris_b, out, backface_cull=False,
               self_test=False, tri_adj=None, cross_shared=None):
    if not na.aabb.intersects(nb.aabb):
        return

    leaf_a = (na.tri_idx >= 0)
    leaf_b = (nb.tri_idx >= 0)

    if leaf_a and leaf_b:
        # Self-intersection: skip same triangle and adjacent triangles
        if self_test:
            if na.tri_idx == nb.tri_idx:
                return
            if na.tri_idx <= nb.tri_idx:
                return  # avoid duplicate pairs
            if tri_adj and nb.tri_idx in tri_adj.get(na.tri_idx, ()):
                return  # skip adjacent triangles (they share an edge)

        # Cross-mesh: skip if triangles share a snapped vertex position
        if cross_shared and (na.tri_idx, nb.tri_idx) in cross_shared:
            return

        hit, depth, pt, n1, n2 = _tri_tri_intersect(
            tris_a[na.tri_idx], tris_b[nb.tri_idx])
        if hit:
            # Backface culling: skip if normals face opposite directions
            if backface_cull and n1 is not None and n2 is not None:
                if _dot(n1, n2) < -0.5:
                    return
            out.append({"face_a": na.tri_idx, "face_b": nb.tri_idx,
                        "depth": depth, "point": pt})
        return

    if leaf_a:
        _query_bvh(na, tris_a, nb.left,  tris_b, out, backface_cull,
                   self_test, tri_adj, cross_shared)
        _query_bvh(na, tris_a, nb.right, tris_b, out, backface_cull,
                   self_test, tri_adj, cross_shared)
    elif leaf_b:
        _query_bvh(na.left,  tris_a, nb, tris_b, out, backface_cull,
                   self_test, tri_adj, cross_shared)
        _query_bvh(na.right, tris_a, nb, tris_b, out, backface_cull,
                   self_test, tri_adj, cross_shared)
    else:
        if na.aabb.surface_area() >= nb.aabb.surface_area():
            _query_bvh(na.left,  tris_a, nb, tris_b, out, backface_cull,
                       self_test, tri_adj, cross_shared)
            _query_bvh(na.right, tris_a, nb, tris_b, out, backface_cull,
                       self_test, tri_adj, cross_shared)
        else:
            _query_bvh(na, tris_a, nb.left,  tris_b, out, backface_cull,
                       self_test, tri_adj, cross_shared)
            _query_bvh(na, tris_a, nb.right, tris_b, out, backface_cull,
                       self_test, tri_adj, cross_shared)


def _build_tri_adjacency(tri_vert_ids):
    """
    Build triangle adjacency based on shared vertices.
    Two triangles are adjacent if they share ANY vertex.
    This prevents false positives between neighboring faces in self-intersection.
    Returns dict: {tri_idx: set(adjacent_tri_indices)}
    """
    # Build vertex -> triangle mapping
    vert_to_tris = {}
    for ti, (v0, v1, v2) in enumerate(tri_vert_ids):
        for v in (v0, v1, v2):
            if v not in vert_to_tris:
                vert_to_tris[v] = []
            vert_to_tris[v].append(ti)

    # Two triangles sharing any vertex are adjacent
    adj = {}
    for ti in range(len(tri_vert_ids)):
        adj[ti] = set()
    for v, tri_list in vert_to_tris.items():
        for i in range(len(tri_list)):
            for j in range(i + 1, len(tri_list)):
                adj[tri_list[i]].add(tri_list[j])
                adj[tri_list[j]].add(tri_list[i])
    return adj

# ---------------------------------------------------------------------------
# Vertex-share adjacency (distance-based, tolerance-controlled)
# ---------------------------------------------------------------------------
# Two triangles are considered "vertex-shared" (and therefore SKIPPED from
# intersection testing) if they share at least 1 vertex position within
# `tolerance` world units.
#
# The default tolerance covers floating-point round-off introduced by
# vertex snapping, transform composition, etc. (1e-4 in Maya cm units
# = 0.001 mm). The UI exposes this so users can tune for very small or
# very large scenes.
# ---------------------------------------------------------------------------

# Default vertex-share tolerance (world units, Maya cm).
# Stored as 1-element list so the value can be mutated by UI / settings
# without re-importing.
_vert_share_tol = [1.0e-4]


def _set_vert_share_tolerance(value):
    """Setter used by the UI / settings layer."""
    try:
        v = float(value)
    except Exception:
        return
    if v < 0.0:
        v = 0.0
    _vert_share_tol[0] = v


def _get_vert_share_tolerance():
    return _vert_share_tol[0]


def _quantize_position(p, cell):
    """Quantize a world-space point to a grid cell of size `cell`.
    Two points within `cell` units MAY share the same key, but two points
    farther than `cell` units MAY ALSO share a key if they straddle a
    cell boundary. We compensate by also probing the 3x3x3 neighbour
    cells when looking up matches.
    """
    if cell <= 0.0:
        # exact match only
        return (p[0], p[1], p[2])
    inv = 1.0 / cell
    return (int(round(p[0] * inv)),
            int(round(p[1] * inv)),
            int(round(p[2] * inv)))


def _neighbour_cells(key):
    """Yield the 27 (3x3x3) cell keys around `key` for tolerance lookup."""
    x, y, z = key
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                yield (x + dx, y + dy, z + dz)


def _positions_close(a, b, tol):
    """Squared-distance comparison (avoids sqrt)."""
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return (dx * dx + dy * dy + dz * dz) <= (tol * tol)


def _build_cross_mesh_shared_verts(tris_a, tris_b, tolerance=None):
    """
    Build a set of (tri_idx_a, tri_idx_b) pairs whose triangles share AT
    LEAST one vertex position within `tolerance` world units. Such pairs
    are skipped during intersection testing because, by user convention,
    "snapped" or coincident vertices indicate intentional contact, not
    penetration.

    Args:
        tris_a, tris_b: lists of ((x,y,z), (x,y,z), (x,y,z))
        tolerance:      world-unit distance; None -> use module default
                        (`_vert_share_tol[0]`).

    Returns:
        set of (ti_a, ti_b)
    """
    if tolerance is None:
        tolerance = _vert_share_tol[0]
    if tolerance < 0.0:
        tolerance = 0.0

    # Cell size: spatial-hash bucket. Slightly larger than tolerance so
    # that a true match within `tolerance` is at most 1 cell away in any
    # axis (covered by the 3x3x3 neighbour scan).
    cell = tolerance if tolerance > 0.0 else 0.0

    # Build spatial hash for B vertices: cell_key -> list of (ti_b, vert_pos)
    pos_to_b = {}
    for ti_b, tri in enumerate(tris_b):
        for v in tri:
            key = _quantize_position(v, cell)
            bucket = pos_to_b.get(key)
            if bucket is None:
                bucket = []
                pos_to_b[key] = bucket
            bucket.append((ti_b, v))

    shared = set()
    tol_sq_ok = (tolerance > 0.0)

    for ti_a, tri_a in enumerate(tris_a):
        # gather candidate B-triangles by scanning neighbour cells
        candidates = set()
        for v_a in tri_a:
            key_a = _quantize_position(v_a, cell)
            if cell > 0.0:
                for nk in _neighbour_cells(key_a):
                    bucket = pos_to_b.get(nk)
                    if not bucket:
                        continue
                    for ti_b, v_b in bucket:
                        if (ti_a, ti_b) in shared:
                            continue
                        if tol_sq_ok:
                            if _positions_close(v_a, v_b, tolerance):
                                candidates.add(ti_b)
                        else:
                            if v_a == v_b:
                                candidates.add(ti_b)
            else:
                bucket = pos_to_b.get(key_a)
                if not bucket:
                    continue
                for ti_b, v_b in bucket:
                    if v_a == v_b:
                        candidates.add(ti_b)

        for ti_b in candidates:
            shared.add((ti_a, ti_b))

    return shared


def _build_self_mesh_shared_verts_pos(tris, tolerance=None):
    """
    Same idea as `_build_cross_mesh_shared_verts`, but for SELF-test:
    detects pairs (ti_a, ti_b) within the same triangle list that share
    at least one vertex POSITION within tolerance.

    This complements the existing topological adjacency (built from
    Maya vertex IDs in `_build_tri_adjacency`) by also catching the
    case where two triangles have geometrically coincident vertices
    that are NOT merged into the same Maya vertex ID (snapped but not
    welded).

    Returns:
        set of frozenset({ti_a, ti_b})  (unordered pairs, ti_a != ti_b)
    """
    if tolerance is None:
        tolerance = _vert_share_tol[0]
    if tolerance < 0.0:
        tolerance = 0.0

    cell = tolerance if tolerance > 0.0 else 0.0

    # Build spatial hash: cell_key -> list of (ti, vert_pos)
    pos_to_t = {}
    for ti, tri in enumerate(tris):
        for v in tri:
            key = _quantize_position(v, cell)
            bucket = pos_to_t.get(key)
            if bucket is None:
                bucket = []
                pos_to_t[key] = bucket
            bucket.append((ti, v))

    shared = set()
    tol_sq_ok = (tolerance > 0.0)

    for ti_a, tri_a in enumerate(tris):
        for v_a in tri_a:
            key_a = _quantize_position(v_a, cell)
            if cell > 0.0:
                cells_to_check = _neighbour_cells(key_a)
            else:
                cells_to_check = (key_a,)
            for nk in cells_to_check:
                bucket = pos_to_t.get(nk)
                if not bucket:
                    continue
                for ti_b, v_b in bucket:
                    if ti_b == ti_a:
                        continue
                    pair = frozenset((ti_a, ti_b))
                    if pair in shared:
                        continue
                    if tol_sq_ok:
                        if _positions_close(v_a, v_b, tolerance):
                            shared.add(pair)
                    else:
                        if v_a == v_b:
                            shared.add(pair)

    return shared
class CollisionDetector(object):
    """
    BVH-accelerated polygon collision detector.
    Maya-independent. Input: world-space triangle lists.
    triangles format: list of ( (x,y,z), (x,y,z), (x,y,z) )

    Vertex-share skipping
    ---------------------
    Triangles that share at least one vertex are SKIPPED from intersection
    testing. "Sharing" is determined by:

      * Self-test:
          - topological adjacency (same Maya vertex IDs), AND
          - positional adjacency (vertices within `vert_share_tol` world
            units, even if not welded into the same Maya vertex ID).

      * Cross-mesh test:
          - positional adjacency only (different meshes have independent
            vertex IDs by definition).

    The default `vert_share_tol` is read from the module-level setting
    set by the UI (`_vert_share_tol[0]`), so callers usually don't need
    to pass it.
    """

    def __init__(self, triangles_a, triangles_b, tri_vert_ids_a=None,
                 bvh_a=None, bvh_b=None, tri_adj_a=None, cross_shared=None,
                 vert_share_tol=None):
        """
        Optional bvh_a/bvh_b: pre-built BVH trees (e.g. refitted).
            If provided, skips building from scratch. Must match triangles_a/b.
        Optional tri_adj_a: pre-built vertex-share adjacency for self-test
            (topological, from Maya vertex IDs).
        Optional cross_shared: pre-built cross-mesh shared-vertex pair set.
        Optional vert_share_tol: tolerance for positional vertex sharing.
            None -> use module default.
        """
        self._tris_a = triangles_a
        self._tris_b = triangles_b
        self._self_test = (triangles_a is triangles_b)
        self._tri_vert_ids_a = tri_vert_ids_a
        self._tri_adj_a = tri_adj_a
        self._cross_shared = cross_shared
        self._vert_share_tol = vert_share_tol  # may be None
        if bvh_a is not None:
            self._bvh_a = bvh_a
        else:
            self._bvh_a = (_build_bvh(triangles_a, list(range(len(triangles_a))))
                           if triangles_a else None)
        if self._self_test:
            self._bvh_b = self._bvh_a
        elif bvh_b is not None:
            self._bvh_b = bvh_b
        else:
            self._bvh_b = (_build_bvh(triangles_b, list(range(len(triangles_b))))
                           if triangles_b else None)

    def check(self, threshold=0.0, backface_cull=False):
        """Returns list of {face_a, face_b, depth, point} for intersecting pairs.
        backface_cull: if True, skip pairs where normals face opposite directions.
        """
        if self._bvh_a is None or self._bvh_b is None:
            return []

        # ---- Self-test adjacency ------------------------------------------
        # Combine TWO sources of adjacency:
        #   (1) topological  - same Maya vertex IDs   (existing behaviour)
        #   (2) positional   - vertices within tolerance world distance
        #                      (NEW: catches snapped-but-not-welded verts)
        tri_adj = None
        if self._self_test:
            base_adj = self._tri_adj_a
            if base_adj is None and self._tri_vert_ids_a is not None:
                base_adj = _build_tri_adjacency(self._tri_vert_ids_a)

            # Positional self-share (new)
            pos_adj_pairs = _build_self_mesh_shared_verts_pos(
                self._tris_a, tolerance=self._vert_share_tol)

            # Merge into a single adjacency dict {ti: set(neighbours)}
            tri_adj = {}
            if base_adj:
                for k, v in base_adj.items():
                    tri_adj[k] = set(v)
            for pair in pos_adj_pairs:
                a, b = tuple(pair)
                tri_adj.setdefault(a, set()).add(b)
                tri_adj.setdefault(b, set()).add(a)

        # ---- Cross-mesh shared-vertex pairs -------------------------------
        cross_shared = None
        if not self._self_test:
            if self._cross_shared is not None:
                cross_shared = self._cross_shared
            else:
                cross_shared = _build_cross_mesh_shared_verts(
                    self._tris_a, self._tris_b,
                    tolerance=self._vert_share_tol)

        raw = []
        _query_bvh(self._bvh_a, self._tris_a,
                   self._bvh_b, self._tris_b, raw, backface_cull,
                   self._self_test, tri_adj, cross_shared)
        seen, unique = set(), []
        for r in raw:
            key = (r["face_a"], r["face_b"])
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique



# ---------------------------------------------------------------------------
# MayaBridge  (Maya cmds / OpenMaya wrapper)
# ---------------------------------------------------------------------------
class MayaBridge(object):
    """
    Extracts triangle data from Maya meshes and provides scene utilities.
    All methods are static and call Maya API only when MAYA_AVAILABLE.
    """

    @staticmethod
    def get_mesh_shapes():
        """Returns all visible mesh shapes in the scene."""
        if not MAYA_AVAILABLE:
            return []
        shapes = cmds.ls(type="mesh", long=True) or []
        visible = []
        for s in shapes:
            try:
                if not cmds.getAttr(s + ".visibility"):
                    continue
                if cmds.getAttr(s + ".intermediateObject"):
                    continue
                visible.append(s)
            except Exception:
                pass
        return visible

    @staticmethod
    def get_selected_meshes():
        """Returns mesh shapes from current selection, including all descendants."""
        if not MAYA_AVAILABLE:
            return []
        sel = cmds.ls(selection=True, long=True) or []
        shapes = []
        seen = set()
        for node in sel:
            node_type = cmds.nodeType(node)
            if node_type == "mesh":
                if node not in seen:
                    if not cmds.getAttr(node + ".intermediateObject"):
                        shapes.append(node)
                        seen.add(node)
            elif node_type == "transform":
                # Get all descendant mesh shapes recursively
                all_descendants = cmds.listRelatives(
                    node, allDescendents=True,
                    type="mesh", fullPath=True) or []
                for ch in all_descendants:
                    if ch not in seen:
                        try:
                            if not cmds.getAttr(ch + ".intermediateObject"):
                                shapes.append(ch)
                                seen.add(ch)
                        except Exception:
                            pass
        return shapes

    @staticmethod
    def get_triangles(mesh_shape):
        """
        Converts a Maya mesh shape to a list of world-space triangles.
        Returns: (triangles, tri_to_poly, tri_vert_ids)
            triangles    : list of ( (x,y,z), (x,y,z), (x,y,z) )
            tri_to_poly  : list of int — tri_to_poly[tri_idx] = polygon face index
            tri_vert_ids : list of (v0, v1, v2) — vertex indices per triangle
        Raises:  RuntimeError on failure.
        """
        if not MAYA_AVAILABLE:
            raise RuntimeError("Maya not available")

        try:
            sel = om.MSelectionList()
            sel.add(mesh_shape)
            dag_path = om.MDagPath()
            sel.getDagPath(0, dag_path)

            # If transform was passed, extend to shape
            try:
                dag_path.extendToShape()
            except Exception:
                pass

            fn_mesh = om.MFnMesh(dag_path)

            # Get world-space points (deformed positions)
            pts = om.MPointArray()
            fn_mesh.getPoints(pts, om.MSpace.kWorld)

            # Get triangle counts and vertex indices per polygon
            tri_counts  = om.MIntArray()
            tri_verts   = om.MIntArray()
            fn_mesh.getTriangles(tri_counts, tri_verts)

            triangles = []
            tri_to_poly = []
            tri_vert_ids = []
            idx = 0
            for poly_idx in range(fn_mesh.numPolygons()):
                n_tris = tri_counts[poly_idx]
                for _ in range(n_tris):
                    i0 = tri_verts[idx];     idx += 1
                    i1 = tri_verts[idx];     idx += 1
                    i2 = tri_verts[idx];     idx += 1
                    p0 = pts[i0]; p1 = pts[i1]; p2 = pts[i2]
                    triangles.append((
                        (p0.x, p0.y, p0.z),
                        (p1.x, p1.y, p1.z),
                        (p2.x, p2.y, p2.z),
                    ))
                    tri_to_poly.append(poly_idx)
                    tri_vert_ids.append((i0, i1, i2))
            return triangles, tri_to_poly, tri_vert_ids

        except Exception as e:
            raise RuntimeError(
                tr("err_triangulate", mesh=mesh_shape) + " : " + str(e))

    @staticmethod
    def select_faces(mesh_shape, face_ids):
        """Select specific face IDs on a mesh in the Maya viewport."""
        if not MAYA_AVAILABLE or not face_ids:
            return
        cmds.select(clear=True)
        components = ["{0}.f[{1}]".format(mesh_shape, f) for f in face_ids]
        cmds.select(components, add=True)

    @staticmethod
    def get_short_name(long_name):
        """Returns the shortest unique name for display."""
        parts = long_name.split("|")
        return parts[-1] if parts else long_name

    @staticmethod
    def mesh_exists(name):
        if not MAYA_AVAILABLE:
            return False
        return cmds.objExists(name) and cmds.nodeType(name) in ("mesh", "transform")

    @staticmethod
    def get_transform(shape_name):
        """Returns the parent transform of a shape."""
        if not MAYA_AVAILABLE:
            return shape_name
        parents = cmds.listRelatives(shape_name, parent=True, fullPath=True) or []
        return parents[0] if parents else shape_name

    @staticmethod
    def has_animation(mesh_shape):
        """
        Returns True if the mesh is actually animated — its geometry or
        world transform can change between frames.

        A skinCluster / blendShape / etc. alone is NOT animation. The
        deformer's drivers (joints, target weights, controllers) must
        themselves be animated for the mesh to move.

        We check:
          1. animCurve connections on the mesh's transform chain (walking up)
          2. constraint / expression / motionPath inputs on the transform chain
          3. If a skinCluster is present: whether ANY driver joint in its
             influence list is animated (transitively via transform chain
             animCurves)
          4. If a blendShape is present: whether its weight attrs are
             driven by animCurves or expressions
        Returns False if no actual time-varying driver is found.
        """
        if not MAYA_AVAILABLE:
            return False

        visited_nodes = set()

        def _transform_has_anim(tr_node):
            """Walk the transform chain upward; True if any node is animated."""
            node = tr_node
            safety = 0
            while node and safety < 64:
                safety += 1
                if node in visited_nodes:
                    return False
                visited_nodes.add(node)
                try:
                    conns = cmds.listConnections(
                        node, source=True, destination=False,
                        type="animCurve") or []
                    if conns:
                        return True
                    # Check constraints on this transform
                    constraints = cmds.listConnections(
                        node, source=True, destination=False,
                        type="constraint") or []
                    if constraints:
                        return True
                    exprs = cmds.listConnections(
                        node, source=True, destination=False,
                        type="expression") or []
                    if exprs:
                        return True
                    motion = cmds.listConnections(
                        node, source=True, destination=False,
                        type="motionPath") or []
                    if motion:
                        return True
                    parents = cmds.listRelatives(
                        node, parent=True, fullPath=True) or []
                except Exception:
                    return False
                if not parents:
                    break
                node = parents[0]
            return False

        try:
            # 1. Check the mesh's own transform chain
            tr = MayaBridge.get_transform(mesh_shape)
            if _transform_has_anim(tr):
                return True

            # 2. Check deformers. For each deformer, verify that its
            #    drivers are actually animated.
            hist = cmds.listHistory(mesh_shape, pruneDagObjects=True) or []
            for node in hist:
                try:
                    nt = cmds.nodeType(node)
                except Exception:
                    continue

                if nt == "skinCluster":
                    # Get influence joints / drivers
                    try:
                        inflist = cmds.skinCluster(
                            node, query=True, influence=True) or []
                    except Exception:
                        inflist = []
                    for inf in inflist:
                        if _transform_has_anim(inf):
                            return True

                elif nt == "blendShape":
                    # Check weight-attr animation
                    try:
                        weight_conns = cmds.listConnections(
                            node + ".weight", source=True, destination=False,
                            type="animCurve") or []
                        if weight_conns:
                            return True
                        weight_exprs = cmds.listConnections(
                            node + ".weight", source=True, destination=False,
                            type="expression") or []
                        if weight_exprs:
                            return True
                    except Exception:
                        pass

                elif nt in ("cluster", "lattice", "nonLinear", "softMod",
                            "wire", "ffd", "sculpt"):
                    # These are driven by their handle transform —
                    # check the handle's transform chain.
                    try:
                        handles = cmds.listConnections(
                            node, source=True, destination=False,
                            type="transform") or []
                        for h in handles:
                            if _transform_has_anim(h):
                                return True
                    except Exception:
                        pass

                elif nt.startswith("animCurve"):
                    # Direct animation curve in the shape history
                    return True
        except Exception:
            return False

        return False

    @staticmethod
    def any_has_animation(mesh_shapes):
        """Returns True if ANY of the given meshes has animation."""
        for m in mesh_shapes:
            if MayaBridge.has_animation(m):
                return True
        return False

    # Cache: {mesh_shape: {face_id: set(neighbor_face_ids)}}
    _face_adjacency_cache = {}
    # Cache: {mesh_shape: bvh_root_node}
    _bvh_cache = {}
    # Cache: {mesh_shape: tri_adjacency_dict}
    _tri_adj_cache = {}
    # Cache: {(mesh_a, mesh_b): set_of_shared_tri_pairs}
    _cross_shared_cache = {}

    @staticmethod
    def clear_caches():
        """Clear all MayaBridge caches. Call when scene topology may have changed."""
        MayaBridge._face_adjacency_cache = {}
        MayaBridge._bvh_cache = {}
        MayaBridge._tri_adj_cache = {}
        MayaBridge._cross_shared_cache = {}

    @staticmethod
    def get_or_build_cross_shared(mesh_a, mesh_b, tris_a, tris_b):
        """
        Return cached cross-mesh shared-vertex triangle-pair set, or build.
        Since welded seams stay welded through skinning (shared rig driver),
        this set is stable across animation frames.
        """
        key = (mesh_a, mesh_b)
        cached = MayaBridge._cross_shared_cache.get(key)
        if cached is not None:
            return cached
        shared = _build_cross_mesh_shared_verts(tris_a, tris_b)
        MayaBridge._cross_shared_cache[key] = shared
        return shared

    @staticmethod
    def get_or_build_bvh(mesh_shape, tris):
        """
        Return a BVH for the given mesh. If cached, refits the existing
        tree (much faster). Otherwise builds a new tree and caches it.
        """
        cached = MayaBridge._bvh_cache.get(mesh_shape)
        if cached is not None:
            # Refit: update AABBs in place, keep the tree structure
            _refit_bvh(cached, tris)
            return cached
        # Build fresh
        if not tris:
            return None
        root = _build_bvh(tris, list(range(len(tris))))
        MayaBridge._bvh_cache[mesh_shape] = root
        return root

    @staticmethod
    def get_or_build_tri_adj(mesh_shape, tri_vert_ids):
        """Return cached vertex-share triangle adjacency, or build and cache."""
        cached = MayaBridge._tri_adj_cache.get(mesh_shape)
        if cached is not None:
            return cached
        adj = _build_tri_adjacency(tri_vert_ids) if tri_vert_ids else {}
        MayaBridge._tri_adj_cache[mesh_shape] = adj
        return adj

    @staticmethod
    def _build_full_adjacency(mesh_shape):
        """
        Build adjacency for ALL faces of the mesh in one shot and cache it.
        Returns dict {face_id: set(neighbor_face_ids)}.
        """
        if mesh_shape in MayaBridge._face_adjacency_cache:
            return MayaBridge._face_adjacency_cache[mesh_shape]

        adj = {}
        if not MAYA_AVAILABLE:
            return adj
        try:
            # One polyInfo call for the entire mesh: edge -> faces
            # This returns a list of lines like:
            # "EDGE    0:    0    1"
            edge_faces = cmds.polyInfo(mesh_shape, edgeToFace=True) or []
            for line in edge_faces:
                # Parse "EDGE    N:    fa fb ..."
                try:
                    parts = line.split(":")[1].strip().split()
                    face_list = [int(p) for p in parts if p.lstrip("-").isdigit()]
                except (IndexError, ValueError):
                    continue
                # All faces sharing this edge are mutual neighbors
                n = len(face_list)
                for i in range(n):
                    fa = face_list[i]
                    if fa < 0:
                        continue
                    if fa not in adj:
                        adj[fa] = set()
                    for j in range(n):
                        if i == j:
                            continue
                        fb = face_list[j]
                        if fb >= 0:
                            adj[fa].add(fb)
        except Exception:
            pass

        MayaBridge._face_adjacency_cache[mesh_shape] = adj
        return adj

    @staticmethod
    def get_face_neighbors(mesh_shape, face_ids):
        """
        Returns a dict {face_id: set(neighbor_face_ids)} for the given faces.
        Two faces are neighbors if they share at least one edge.
        Uses cached full adjacency for speed.
        """
        if not MAYA_AVAILABLE or not face_ids:
            return {}

        full_adj = MayaBridge._build_full_adjacency(mesh_shape)
        face_set = set(face_ids)
        result = {}
        for fid in face_ids:
            # Only keep neighbors that are in the requested face set
            result[fid] = full_adj.get(fid, set()) & face_set
        return result

def _group_connected_faces(face_ids, neighbors):
    """
    Given a set of face IDs and their adjacency, returns a list of
    connected groups (each group is a set of face IDs).
    Uses BFS flood-fill.
    """
    remaining = set(face_ids)
    groups = []
    while remaining:
        seed = next(iter(remaining))
        group = set()
        queue = [seed]
        while queue:
            f = queue.pop(0)
            if f in group:
                continue
            group.add(f)
            remaining.discard(f)
            for n in neighbors.get(f, ()):
                if n in remaining:
                    queue.append(n)
        groups.append(group)
    return groups



# ---------------------------------------------------------------------------
# CheckItem  (base + concrete implementations)
# ---------------------------------------------------------------------------
SCOPE_SCENE = "scene"
SCOPE_MESH  = "mesh"

_ICON        = {"unchecked": u"\u25CB", "pass": u"\u2714", "fail": u"\u2718"}
_ICON_COLOR  = {"unchecked": "#888", "pass": "#4CAF50", "fail": "#F44336"}

class CheckItem(object):
    """Abstract base for all collision checks. Python 2.7 compatible."""
    label_key       = ""
    desc_key        = ""
    can_auto_fix    = False
    scope           = SCOPE_MESH
    default_enabled = True

    def __init__(self):
        self.issues  = []
        self.status  = "unchecked"
        self.enabled = self.__class__.default_enabled
        self.elapsed_sec = 0.0
        # Settings shared across instances of same class
        self._settings = {}

    @property
    def label(self):
        return tr(self.label_key)

    @property
    def description(self):
        return tr(self.desc_key)

    def check(self):
        """Detection only. Must NOT modify the Maya scene. Returns list[dict]."""
        raise NotImplementedError

    def fix(self, issues=None):
        raise NotImplementedError

    def run_check(self):
        t_start = time.time()
        try:
            self.issues = self.check()
            self.status = "fail" if self.issues else "pass"
        except Exception as e:
            self.issues = [{"mesh_a": "ERROR", "mesh_b": "", "face_a": -1,
                            "face_b": -1, "depth": 0.0, "point": None,
                            "detail": str(e)}]
            self.status = "fail"
        self.elapsed_sec = time.time() - t_start
        return self.issues

    # --- shared settings helpers ---
    def get_setting(self, key, default=None):
        return self._settings.get(key, default)

    def set_setting(self, key, value):
        self._settings[key] = value


# ---- Shared state for mesh pairs (used by both checks) --------------------
_mesh_pairs = []        # list of (mesh_a_long, mesh_b_long)
_use_selected_only = [True]   # wrapped in list for Py2 closure mutability
_self_intersect = [True]      # check self-intersection within a single mesh
_depth_threshold = [0.011]     # minimum depth to report (filters boundary noise)
_proximity_threshold = [2.0]   # mm


def _compute_tris_aabb(tris):
    """Compute AABB (min, max) from a list of triangles. Returns None if empty."""
    if not tris:
        return None
    mn = [float("inf"), float("inf"), float("inf")]
    mx = [float("-inf"), float("-inf"), float("-inf")]
    for tri in tris:
        for v in tri:
            if v[0] < mn[0]: mn[0] = v[0]
            if v[1] < mn[1]: mn[1] = v[1]
            if v[2] < mn[2]: mn[2] = v[2]
            if v[0] > mx[0]: mx[0] = v[0]
            if v[1] > mx[1]: mx[1] = v[1]
            if v[2] > mx[2]: mx[2] = v[2]
    return (tuple(mn), tuple(mx))


def _aabbs_overlap(a, b, margin=0.0):
    """Return True if two AABB tuples (min, max) overlap."""
    if a is None or b is None:
        return False
    amin, amax = a
    bmin, bmax = b
    if amax[0] + margin < bmin[0] or bmax[0] + margin < amin[0]:
        return False
    if amax[1] + margin < bmin[1] or bmax[1] + margin < amin[1]:
        return False
    if amax[2] + margin < bmin[2] or bmax[2] + margin < amin[2]:
        return False
    return True


def _get_pairs_to_check():
    """
    Returns list of (mesh_a, mesh_b) tuples to check.
    When mesh_a == mesh_b, it means self-intersection check.
    If pairs are defined: use them.
    If selected-only: use all combinations from selection.
    Else: all pairs from scene.
    """
    if _mesh_pairs:
        valid = []
        for a, b in _mesh_pairs:
            if MayaBridge.mesh_exists(a) and MayaBridge.mesh_exists(b):
                valid.append((a, b))
        return valid

    if _use_selected_only[0]:
        meshes = MayaBridge.get_selected_meshes()
    else:
        meshes = MayaBridge.get_mesh_shapes()

    pairs = []
    # Self-intersection pairs
    if _self_intersect[0]:
        for m in meshes:
            pairs.append((m, m))

    # Cross-mesh pairs
    for i in range(len(meshes)):
        for j in range(i + 1, len(meshes)):
            pairs.append((meshes[i], meshes[j]))
    return pairs

# ---------------------------------------------------------------------------
class IntersectionCheck(CheckItem):
    """Detects triangles that physically intersect at the current frame.
    Results are grouped by connected adjacent faces."""
    label_key = "chk_intersection"
    desc_key  = "desc_intersection"

    def check(self):
        pairs = _get_pairs_to_check()
        if not pairs:
            return []

        issues = []
        # Triangle + AABB cache for this check run
        _tri_cache = {}
        def _get_cached(m):
            if m in _tri_cache:
                return _tri_cache[m]
            try:
                t, mp, v = MayaBridge.get_triangles(m)
            except RuntimeError as e:
                _tri_cache[m] = ("error", str(e))
                return _tri_cache[m]
            if not t:
                _tri_cache[m] = None
                return None
            entry = (t, mp, v, _compute_tris_aabb(t))
            _tri_cache[m] = entry
            return entry

        for mesh_a, mesh_b in pairs:
            is_self = (mesh_a == mesh_b)
            ea = _get_cached(mesh_a)
            if ea is None:
                continue
            if isinstance(ea, tuple) and len(ea) == 2 and ea[0] == "error":
                issues.append({
                    "mesh_a": mesh_a, "mesh_b": mesh_b,
                    "faces_a": [], "faces_b": [],
                    "face_a": -1, "face_b": -1,
                    "depth": 0.0, "point": None,
                    "detail": ea[1],
                })
                continue
            tris_a, map_a, vids_a, aabb_a = ea
            if is_self:
                tris_b, map_b, vids_b, aabb_b = tris_a, map_a, vids_a, aabb_a
            else:
                eb = _get_cached(mesh_b)
                if eb is None:
                    continue
                if isinstance(eb, tuple) and len(eb) == 2 and eb[0] == "error":
                    continue
                tris_b, map_b, vids_b, aabb_b = eb
                if not _aabbs_overlap(aabb_a, aabb_b):
                    continue

            # Build BVH fresh each time (no cache) to avoid any staleness issues
            det = CollisionDetector(
                tris_a, tris_b if not is_self else tris_a,
                tri_vert_ids_a=vids_a if is_self else None)
            hits = det.check(threshold=0.0, backface_cull=True)

            # Collect unique polygon face pairs, skip coplanar (depth==0)
            all_faces_a = set()
            all_faces_b = set()
            seen_poly_pairs = set()
            hit_list = []
            for h in hits:
                poly_a = map_a[h["face_a"]]
                poly_b = map_b[h["face_b"]]
                key = (poly_a, poly_b)
                if key in seen_poly_pairs:
                    continue
                seen_poly_pairs.add(key)
                if h["depth"] < _depth_threshold[0]:
                    continue  # skip coplanar — handled by OverlapCheck
                hit_list.append({
                    "poly_a": poly_a, "poly_b": poly_b,
                    "depth": h["depth"], "point": h["point"],
                })
                all_faces_a.add(poly_a)
                all_faces_b.add(poly_b)

            if not hit_list:
                continue

            # Group faces_a by adjacency
            neighbors_a = MayaBridge.get_face_neighbors(
                mesh_a, list(all_faces_a))
            groups_a = _group_connected_faces(all_faces_a, neighbors_a)

            # For each group_a, collect all associated faces_b
            for grp_a in groups_a:
                grp_b = set()
                max_depth = 0.0
                for h in hit_list:
                    if h["poly_a"] in grp_a:
                        grp_b.add(h["poly_b"])
                        if h["depth"] > max_depth:
                            max_depth = h["depth"]

                # Sub-group faces_b by adjacency
                if grp_b:
                    neighbors_b = MayaBridge.get_face_neighbors(
                        mesh_b, list(grp_b))
                    sub_groups_b = _group_connected_faces(grp_b, neighbors_b)
                    # Merge all sub_groups_b into one for this group_a
                    merged_b = set()
                    for sg in sub_groups_b:
                        merged_b.update(sg)
                    grp_b = merged_b

                sorted_a = sorted(grp_a)
                sorted_b = sorted(grp_b)
                issues.append({
                    "mesh_a":  mesh_a,
                    "mesh_b":  mesh_b,
                    "faces_a": sorted_a,
                    "faces_b": sorted_b,
                    "face_a":  sorted_a[0] if sorted_a else -1,
                    "face_b":  sorted_b[0] if sorted_b else -1,
                    "depth":   max_depth,
                    "point":   None,
                    "detail":  "{0} Face / {1} Face  max_depth={2:.4f}".format(
                        len(sorted_a), len(sorted_b), max_depth),
                })
        return issues

    def fix(self, issues=None):
        pass  # No auto-fix for intersections


# ---------------------------------------------------------------------------
class OverlapCheck(CheckItem):
    """Detects coplanar overlapping faces (complete overlap / z-fighting)."""
    label_key       = "chk_overlap"
    desc_key        = "desc_overlap"
    default_enabled = False

    def check(self):
        pairs = _get_pairs_to_check()
        if not pairs:
            return []

        issues = []
        for mesh_a, mesh_b in pairs:
            is_self = (mesh_a == mesh_b)
            try:
                tris_a, map_a, vids_a = MayaBridge.get_triangles(mesh_a)
                if is_self:
                    tris_b, map_b, vids_b = tris_a, map_a, vids_a
                else:
                    tris_b, map_b, vids_b = MayaBridge.get_triangles(mesh_b)
            except RuntimeError as e:
                issues.append({
                    "mesh_a": mesh_a, "mesh_b": mesh_b,
                    "faces_a": [], "faces_b": [],
                    "face_a": -1, "face_b": -1,
                    "depth": 0.0, "point": None,
                    "detail": str(e),
                })
                continue

            if not tris_a or not tris_b:
                continue

            det = CollisionDetector(
                tris_a, tris_b if not is_self else tris_a,
                tri_vert_ids_a=vids_a if is_self else None)
            hits = det.check(threshold=0.0)

            # Collect only coplanar (depth==0) hits
            all_faces_a = set()
            all_faces_b = set()
            seen_poly_pairs = set()
            for h in hits:
                poly_a = map_a[h["face_a"]]
                poly_b = map_b[h["face_b"]]
                key = (poly_a, poly_b)
                if key in seen_poly_pairs:
                    continue
                seen_poly_pairs.add(key)
                if h["depth"] >= _EPSILON:
                    continue  # skip non-coplanar
                all_faces_a.add(poly_a)
                all_faces_b.add(poly_b)

            if not all_faces_a:
                continue

            # Group by adjacency
            neighbors_a = MayaBridge.get_face_neighbors(
                mesh_a, list(all_faces_a))
            groups_a = _group_connected_faces(all_faces_a, neighbors_a)

            for grp_a in groups_a:
                # Collect associated faces_b
                grp_b = set()
                for pa, pb in seen_poly_pairs:
                    if pa in grp_a:
                        grp_b.add(pb)

                sorted_a = sorted(grp_a)
                sorted_b = sorted(grp_b)
                issues.append({
                    "mesh_a":  mesh_a,
                    "mesh_b":  mesh_b,
                    "faces_a": sorted_a,
                    "faces_b": sorted_b,
                    "face_a":  sorted_a[0] if sorted_a else -1,
                    "face_b":  sorted_b[0] if sorted_b else -1,
                    "depth":   0.0,
                    "point":   None,
                    "detail":  "{0} Face / {1} Face  coplanar".format(
                        len(sorted_a), len(sorted_b)),
                })
        return issues

    def fix(self, issues=None):
        pass


# ---------------------------------------------------------------------------
class ProximityCheck(CheckItem):
    """Detects triangles within proximity threshold without intersecting."""
    label_key = "chk_proximity"
    desc_key  = "desc_proximity"

    def check(self):
        threshold = _proximity_threshold[0]
        pairs = _get_pairs_to_check()
        if not pairs:
            return []

        issues = []
        for mesh_a, mesh_b in pairs:
            try:
                tris_a, map_a, _va = MayaBridge.get_triangles(mesh_a)
                tris_b, map_b, _vb = MayaBridge.get_triangles(mesh_b)
            except RuntimeError as e:
                issues.append({
                    "mesh_a": mesh_a, "mesh_b": mesh_b,
                    "face_a": -1, "face_b": -1,
                    "depth": 0.0, "point": None,
                    "detail": str(e),
                })
                continue

            if not tris_a or not tris_b:
                continue

            # threshold > 0: near-miss detection
            det  = CollisionDetector(tris_a, tris_b)
            hits = det.check(threshold=threshold)

            seen_poly_pairs = set()
            for h in hits:
                # Exclude actual intersections (depth > 0) — those belong to
                # IntersectionCheck. Proximity shows near-miss only.
                if h["depth"] > _EPSILON:
                    continue
                poly_a = map_a[h["face_a"]]
                poly_b = map_b[h["face_b"]]
                key = (poly_a, poly_b)
                if key in seen_poly_pairs:
                    continue
                seen_poly_pairs.add(key)
                issues.append({
                    "mesh_a": mesh_a,
                    "mesh_b": mesh_b,
                    "face_a": poly_a,
                    "face_b": poly_b,
                    "depth":  h["depth"],
                    "point":  h["point"],
                    "detail": "near-miss (thresh={0:.1f}mm)".format(threshold),
                })
        return issues

    def fix(self, issues=None):
        pass


# Registry for Static group
STATIC_CHECKS = [IntersectionCheck, OverlapCheck]

# ---------------------------------------------------------------------------
# Shared UI helpers & stylesheets
# ---------------------------------------------------------------------------
def _mkbtn(text, h, bg, hv, fs=11, parent=None):
    b = QtWidgets.QPushButton(text, parent)
    b.setFixedHeight(h)
    b.setStyleSheet(
        "QPushButton{{background-color:{bg};color:white;border:none;"
        "border-radius:4px;font-size:{fs}px;font-weight:bold;padding:0 10px}}"
        "QPushButton:hover{{background-color:{hv}}}"
        "QPushButton:disabled{{background-color:#444;color:#666}}"
        .format(bg=bg, hv=hv, fs=fs))
    return b


_DIALOG_SS = (
    "QDialog{background-color:#333;color:#EEE}"
    "QGroupBox{border:1px solid #555;border-radius:6px;"
    "background-color:#2E2E2E;color:#EEE;margin-top:8px;padding-top:8px}"
    "QGroupBox::title{subcontrol-origin:margin;left:8px}"
    "QLabel{color:#EEE}"
    "QCheckBox{color:#EEE}"
    "QDoubleSpinBox,QSpinBox,QLineEdit{"
    "background-color:#2B2B2B;color:#EEE;border:1px solid #555;"
    "border-radius:3px;padding:2px}"
    "QListWidget{background-color:#2B2B2B;color:#EEE;"
    "border:1px solid #555;border-radius:3px}"
    "QListWidget::item:selected{background-color:#1565C0}"
)

_TABLE_SS = (
    "QTableWidget{background-color:#2B2B2B;color:#EEE;"
    "gridline-color:#444;border:none}"
    "QTableWidget::item{padding:2px}"
    "QTableWidget::item:selected{background-color:#1565C0}"
    "QHeaderView::section{background-color:#3C3C3C;color:#EEE;"
    "border:1px solid #555;padding:4px;font-size:10px;font-weight:bold}"
    "QScrollBar:vertical{background:#2B2B2B;width:10px}"
    "QScrollBar::handle:vertical{background:#555;border-radius:4px}"
)


# ---------------------------------------------------------------------------
# Animation Scan  (global settings + scanner)
# ---------------------------------------------------------------------------
_anim_start_frame = [1]
_anim_end_frame   = [100]
_anim_step        = [1]
_anim_use_timeline = [True]
_anim_ignore_static = [True]   # ignore intersections from baseline frame
_anim_baseline_frame = [0]    # specific frame to use as baseline


class AnimationScanner(object):
    """
    Scans frame range for intersection issues.
    Runs on the main thread (Maya API requirement), yields progress
    via callback so the UI can update with processEvents().
    """

    def __init__(self, progress_cb=None, cancelled_cb=None):
        """
        progress_cb(frame, total_frames, issues_this_frame)
        cancelled_cb() -> bool  (returns True if user pressed Stop)
        """
        self._progress_cb  = progress_cb
        self._cancelled_cb = cancelled_cb
        self.results = []    # list of {frame, issues: [...]}
        self.elapsed_sec = 0.0

    def _run_frame_check(self, pairs):
        """
        Run intersection check at the current frame (same logic as static).
        Returns list of grouped issue dicts.
        """
        frame_issues = []
        # Cache for mesh triangles and AABBs this frame
        tri_cache = {}  # mesh -> (tris, map, vids, aabb)

        def _get_cached(m):
            if m in tri_cache:
                return tri_cache[m]
            try:
                t, mp, v = MayaBridge.get_triangles(m)
            except RuntimeError:
                tri_cache[m] = None
                return None
            if not t:
                tri_cache[m] = None
                return None
            ab = _compute_tris_aabb(t)
            entry = (t, mp, v, ab)
            tri_cache[m] = entry
            return entry

        for mesh_a, mesh_b in pairs:
            is_self = (mesh_a == mesh_b)
            ea = _get_cached(mesh_a)
            if ea is None:
                continue
            tris_a, map_a, vids_a, aabb_a = ea
            if is_self:
                tris_b, map_b, aabb_b = tris_a, map_a, aabb_a
            else:
                eb = _get_cached(mesh_b)
                if eb is None:
                    continue
                tris_b, map_b, _vb, aabb_b = eb
                # Mesh-level AABB pre-check
                if not _aabbs_overlap(aabb_a, aabb_b):
                    continue

            # Build fresh detector (no caching) to guarantee correctness.
            # AABB cache (tri_cache) above still avoids redundant mesh fetches.
            det = CollisionDetector(
                tris_a, tris_b if not is_self else tris_a,
                tri_vert_ids_a=vids_a if is_self else None)
            hits = det.check(threshold=0.0, backface_cull=True)

            all_faces_a = set()
            all_faces_b = set()
            seen = set()
            hit_list = []
            for h in hits:
                poly_a = map_a[h["face_a"]]
                poly_b = map_b[h["face_b"]]
                key = (poly_a, poly_b)
                if key in seen:
                    continue
                seen.add(key)
                if h["depth"] < _depth_threshold[0]:
                    continue
                hit_list.append({
                    "poly_a": poly_a, "poly_b": poly_b,
                    "depth": h["depth"],
                })
                all_faces_a.add(poly_a)
                all_faces_b.add(poly_b)

            if not hit_list:
                continue

            # Group faces_a by adjacency
            neighbors_a = MayaBridge.get_face_neighbors(
                mesh_a, list(all_faces_a))
            groups_a = _group_connected_faces(all_faces_a, neighbors_a)

            for grp_a in groups_a:
                grp_b = set()
                max_depth = 0.0
                for h in hit_list:
                    if h["poly_a"] in grp_a:
                        grp_b.add(h["poly_b"])
                        if h["depth"] > max_depth:
                            max_depth = h["depth"]

                if grp_b:
                    neighbors_b = MayaBridge.get_face_neighbors(
                        mesh_b, list(grp_b))
                    sub_groups_b = _group_connected_faces(grp_b, neighbors_b)
                    merged_b = set()
                    for sg in sub_groups_b:
                        merged_b.update(sg)
                    grp_b = merged_b

                sorted_a = sorted(grp_a)
                sorted_b = sorted(grp_b)
                frame_issues.append({
                    "mesh_a":  mesh_a,
                    "mesh_b":  mesh_b,
                    "faces_a": sorted_a,
                    "faces_b": sorted_b,
                    "face_a":  sorted_a[0] if sorted_a else -1,
                    "face_b":  sorted_b[0] if sorted_b else -1,
                    "depth":   max_depth,
                    "point":   None,
                    "detail":  "{0} Face / {1} Face  max_depth={2:.4f}".format(
                        len(sorted_a), len(sorted_b), max_depth),
                })
        return frame_issues

    @staticmethod
    def _match_baseline(issue, baseline_issues):
        """
        Check if an issue's face group overlaps with any baseline issue's
        face group on the same mesh pair. If so, it's a 'known' collision.
        Matching is by mesh pair + any overlap in faces_a OR faces_b.
        """
        i_ma = issue["mesh_a"]
        i_mb = issue["mesh_b"]
        i_fa = set(issue.get("faces_a", []))
        i_fb = set(issue.get("faces_b", []))

        for bl in baseline_issues:
            if bl["mesh_a"] != i_ma or bl["mesh_b"] != i_mb:
                continue
            bl_fa = set(bl.get("faces_a", []))
            bl_fb = set(bl.get("faces_b", []))
            # Any overlap in either face set = same collision region
            if i_fa & bl_fa or i_fb & bl_fb:
                return True
        return False

    def scan(self):
        """Run the scan. Returns list of {frame, issues}."""
        self.elapsed_sec = 0.0
        if not MAYA_AVAILABLE:
            return []

        t_start = time.time()

        # Clear caches to ensure fresh topology data
        MayaBridge.clear_caches()

        # Determine frame range (always from saved spinner values)
        start = _anim_start_frame[0]
        end   = _anim_end_frame[0]
        step  = max(1, _anim_step[0])

        original_time = cmds.currentTime(query=True)

        pairs = _get_pairs_to_check()
        if not pairs:
            self.elapsed_sec = time.time() - t_start
            return []

        frames = list(range(start, end + 1, step))
        total  = len(frames)
        self.results = []

        # Step 1: Collect baseline issues at the specified frame
        baseline_issues = []
        if _anim_ignore_static[0]:
            bl_frame = _anim_baseline_frame[0]
            cmds.currentTime(bl_frame, edit=True, update=True)
            if self._progress_cb:
                self._progress_cb(bl_frame, total, [])
            try:
                baseline_issues = self._run_frame_check(pairs)
            except Exception:
                baseline_issues = []
            if self._cancelled_cb and self._cancelled_cb():
                cmds.currentTime(original_time, edit=True)
                self.elapsed_sec = time.time() - t_start
                return []

        # Step 2: Scan all frames
        for idx, frame in enumerate(frames):
            if self._cancelled_cb and self._cancelled_cb():
                break

            cmds.currentTime(frame, edit=True, update=True)

            all_issues = self._run_frame_check(pairs)

            # Step 3: Filter — separate baseline-known vs new issues
            if baseline_issues:
                new_issues = []
                for iss in all_issues:
                    if not self._match_baseline(iss, baseline_issues):
                        new_issues.append(iss)
                frame_issues = new_issues
            else:
                frame_issues = all_issues

            if frame_issues:
                self.results.append({"frame": frame, "issues": frame_issues})

            if self._progress_cb:
                self._progress_cb(frame, total, frame_issues)

        cmds.currentTime(original_time, edit=True)

        # Frame-to-frame dedup: collapse consecutive occurrences of the same
        # mesh-pair + overlapping face groups into a single result. Carries
        # over between frames so the user only sees each collision "event"
        # once per contiguous span of frames.
        self.results = self._dedup_consecutive(self.results)

        self.elapsed_sec = time.time() - t_start
        return self.results

    @staticmethod
    def _dedup_consecutive(results):
        """
        Remove issues that are EXACTLY identical to an issue from the
        immediately previous frame. An issue is considered a continuation
        only if another issue exists with the same mesh pair AND exactly
        the same faces_a / faces_b sets. Any change in face participation
        counts as a new issue.
        """
        if not results:
            return results

        # Previous frame's issues, stored as:
        #   (mesh_a, mesh_b, frozenset(faces_a), frozenset(faces_b))
        prev_signatures = set()
        out_results = []

        for entry in results:
            frame = entry["frame"]
            frame_issues = entry["issues"]
            current_signatures = set()
            kept_issues = []

            for iss in frame_issues:
                sig = (
                    iss.get("mesh_a", ""),
                    iss.get("mesh_b", ""),
                    frozenset(iss.get("faces_a", [])),
                    frozenset(iss.get("faces_b", [])),
                )
                current_signatures.add(sig)
                # Only skip if this exact signature existed in the
                # immediately previous frame.
                if sig not in prev_signatures:
                    kept_issues.append(iss)

            prev_signatures = current_signatures

            if kept_issues:
                out_results.append({"frame": frame, "issues": kept_issues})

        return out_results


# ---------------------------------------------------------------------------
# AnimScanSettingsDialog
# ---------------------------------------------------------------------------
class AnimScanSettingsDialog(QtWidgets.QDialog):
    """Settings dialog for animation scan: frame range and step."""

    def __init__(self, parent=None):
        super(AnimScanSettingsDialog, self).__init__(parent)
        self.setWindowTitle(tr("anim_settings_title"))
        self.setFixedWidth(320)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setStyleSheet(_DIALOG_SS)
        self._build()
        self._load_state()

    def _build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(10, 10, 10, 10)
        lo.setSpacing(8)

        grp = QtWidgets.QGroupBox(tr("lbl_frame_range"))
        glo = QtWidgets.QVBoxLayout(grp)

        # Use timeline checkbox
        self.cb_timeline = QtWidgets.QCheckBox(tr("chk_use_timeline"))
        self.cb_timeline.toggled.connect(self._on_timeline_toggled)
        glo.addWidget(self.cb_timeline)

        # Frame range row
        range_row = QtWidgets.QHBoxLayout()
        range_row.addWidget(QtWidgets.QLabel(tr("lbl_frame_range")))
        self.spin_start = QtWidgets.QSpinBox()
        self.spin_start.setRange(-100000, 100000)
        self.spin_start.setFixedWidth(70)
        range_row.addWidget(self.spin_start)
        range_row.addWidget(QtWidgets.QLabel(" - "))
        self.spin_end = QtWidgets.QSpinBox()
        self.spin_end.setRange(-100000, 100000)
        self.spin_end.setFixedWidth(70)
        range_row.addWidget(self.spin_end)
        range_row.addStretch()
        glo.addLayout(range_row)

        # Step row
        step_row = QtWidgets.QHBoxLayout()
        step_row.addWidget(QtWidgets.QLabel(tr("lbl_frame_step")))
        self.spin_step = QtWidgets.QSpinBox()
        self.spin_step.setRange(1, 100)
        self.spin_step.setFixedWidth(60)
        step_row.addWidget(self.spin_step)
        step_row.addStretch()
        glo.addLayout(step_row)

        # Ignore static intersections
        self.cb_ignore_static = QtWidgets.QCheckBox(tr("chk_ignore_static"))
        glo.addWidget(self.cb_ignore_static)

        lo.addWidget(grp)

        # OK / Cancel
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch()
        ok = _mkbtn("OK", 26, "#FF9800", "#F57C00")
        ok.clicked.connect(self._save_and_close)
        cancel = _mkbtn("Cancel", 26, "#555", "#444")
        cancel.clicked.connect(self.reject)
        bottom.addWidget(ok)
        bottom.addWidget(cancel)
        lo.addLayout(bottom)

    def _load_state(self):
        self.cb_timeline.setChecked(_anim_use_timeline[0])
        self.cb_ignore_static.setChecked(_anim_ignore_static[0])
        self.spin_start.setValue(_anim_start_frame[0])
        self.spin_end.setValue(_anim_end_frame[0])
        self.spin_step.setValue(_anim_step[0])

        if MAYA_AVAILABLE and _anim_use_timeline[0]:
            self.spin_start.setValue(
                int(cmds.playbackOptions(query=True, minTime=True)))
            self.spin_end.setValue(
                int(cmds.playbackOptions(query=True, maxTime=True)))

        self._on_timeline_toggled(self.cb_timeline.isChecked())

    def _on_timeline_toggled(self, checked):
        self.spin_start.setEnabled(not checked)
        self.spin_end.setEnabled(not checked)
        if checked and MAYA_AVAILABLE:
            self.spin_start.setValue(
                int(cmds.playbackOptions(query=True, minTime=True)))
            self.spin_end.setValue(
                int(cmds.playbackOptions(query=True, maxTime=True)))

    def _save_and_close(self):
        _anim_use_timeline[0] = self.cb_timeline.isChecked()
        _anim_ignore_static[0] = self.cb_ignore_static.isChecked()
        _anim_start_frame[0]  = self.spin_start.value()
        _anim_end_frame[0]    = self.spin_end.value()
        _anim_step[0]         = self.spin_step.value()
        self.accept()


# ---------------------------------------------------------------------------
# AnimResultWindow
# ---------------------------------------------------------------------------
class AnimResultWindow(QtWidgets.QDialog):
    """
    Displays per-frame intersection results.
    Row click -> go to that frame + select the faces.
    """

    def __init__(self, parent=None):
        super(AnimResultWindow, self).__init__(parent)
        self.setWindowTitle(tr("result_title_anim"))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumSize(720, 450)
        self.setStyleSheet(
            "QDialog{background-color:#333;color:#EEE}"
            "QLabel{color:#EEE}")
        self._rows = []
        self._build()

    def _build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(8, 8, 8, 8)
        lo.setSpacing(6)

        # Summary label
        self._summary_label = QtWidgets.QLabel("")
        self._summary_label.setStyleSheet(
            "color:#FF9800;background-color:#2B2B2B;"
            "padding:4px 8px;border-radius:3px;font-size:10px")
        self._summary_label.setWordWrap(True)
        lo.addWidget(self._summary_label)

        # Table: Frame | Status | Mesh A | Mesh B | Detail
        self._table = QtWidgets.QTableWidget(0, 5)
        self._table.setStyleSheet(
            _TABLE_SS + "QTableWidget{alternate-background-color:#323232}")
        self._table.setHorizontalHeaderLabels([
            tr("col_frame"), tr("col_status"),
            tr("col_mesh_a"), tr("col_mesh_b"), tr("col_detail"),
        ])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 50)
        self._table.setColumnWidth(1, 55)
        self._table.setColumnWidth(2, 130)
        self._table.setColumnWidth(3, 130)
        self._table.setWordWrap(True)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.currentCellChanged.connect(self._on_row_changed)
        lo.addWidget(self._table)

        # Bottom bar
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch()
        self._btn_goto = _mkbtn(tr("btn_goto_frame"), 26, "#FF9800", "#F57C00")
        self._btn_goto.clicked.connect(self._goto_current_frame)
        bottom.addWidget(self._btn_goto)
        self._btn_select = _mkbtn(tr("btn_select_faces"), 26, "#2196F3", "#1976D2")
        self._btn_select.clicked.connect(self._select_current_faces)
        bottom.addWidget(self._btn_select)
        btn_close = _mkbtn(tr("btn_close"), 26, "#555", "#444")
        btn_close.clicked.connect(self.hide)
        bottom.addWidget(btn_close)
        lo.addLayout(bottom)

    def populate(self, scan_results):
        """
        scan_results: list of {frame: int, issues: [issue_dict, ...]}
        """
        self._table.setRowCount(0)
        self._rows = []

        total_issues = 0
        frames_with_issues = 0

        for fr_data in scan_results:
            frame = fr_data["frame"]
            issues = fr_data["issues"]
            if not issues:
                continue
            frames_with_issues += 1

            for issue in issues:
                row = self._table.rowCount()
                self._table.insertRow(row)

                # Frame
                f_item = QtWidgets.QTableWidgetItem(str(frame))
                f_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._table.setItem(row, 0, f_item)

                # Status
                st_item = QtWidgets.QTableWidgetItem(tr("fail_label"))
                st_item.setTextAlignment(QtCore.Qt.AlignCenter)
                st_item.setForeground(QtGui.QColor("#F44336"))
                font = st_item.font()
                font.setBold(True)
                st_item.setFont(font)
                self._table.setItem(row, 1, st_item)

                # Mesh A
                short_a = MayaBridge.get_short_name(
                    issue.get("mesh_a", ""))
                self._table.setItem(row, 2,
                    QtWidgets.QTableWidgetItem(short_a))

                # Mesh B
                short_b = MayaBridge.get_short_name(
                    issue.get("mesh_b", ""))
                self._table.setItem(row, 3,
                    QtWidgets.QTableWidgetItem(short_b))

                # Detail
                self._table.setItem(row, 4,
                    QtWidgets.QTableWidgetItem(issue.get("detail", "")))

                self._rows.append({
                    "frame": frame, "issue": issue})
                total_issues += 1

        self._summary_label.setText(
            tr("lbl_anim_summary",
               total=total_issues, frames=frames_with_issues))

    def _on_row_changed(self, row, col, prev_row, prev_col):
        if row < 0 or row >= len(self._rows):
            return
        self._goto_and_select(row)

    def _goto_and_select(self, row):
        """Go to frame and select the grouped faces stored in the issue."""
        if not MAYA_AVAILABLE:
            return
        data  = self._rows[row]
        frame = data["frame"]
        issue = data["issue"]

        cmds.currentTime(frame, edit=True)

        mesh_a = issue.get("mesh_a", "")
        mesh_b = issue.get("mesh_b", "")

        # Use pre-grouped faces if available, fall back to single face
        faces_a = issue.get("faces_a", [])
        faces_b = issue.get("faces_b", [])
        if not faces_a:
            fa = issue.get("face_a", -1)
            if fa >= 0:
                faces_a = [fa]
        if not faces_b:
            fb = issue.get("face_b", -1)
            if fb >= 0:
                faces_b = [fb]

        if faces_a and mesh_a:
            MayaBridge.select_faces(mesh_a, faces_a)
        if faces_b and mesh_b:
            for fb in faces_b:
                try:
                    cmds.select(
                        "{0}.f[{1}]".format(mesh_b, fb), add=True)
                except Exception:
                    pass

    def _goto_current_frame(self):
        row = self._table.currentRow()
        if row >= 0 and row < len(self._rows):
            if MAYA_AVAILABLE:
                cmds.currentTime(
                    self._rows[row]["frame"], edit=True)

    def _select_current_faces(self):
        row = self._table.currentRow()
        if row >= 0:
            self._goto_and_select(row)

    def refresh_labels(self):
        self.setWindowTitle(tr("result_title_anim"))
        headers = [tr("col_frame"), tr("col_status"),
                   tr("col_mesh_a"), tr("col_mesh_b"), tr("col_detail")]
        for i, h in enumerate(headers):
            item = self._table.horizontalHeaderItem(i)
            if item:
                item.setText(h)
        self._btn_goto.setText(tr("btn_goto_frame"))
        self._btn_select.setText(tr("btn_select_faces"))



# ---------------------------------------------------------------------------
# Settings Dialogs
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# StaticCheckSettingsDialog: REMOVED.
# Vertex-share tolerance is now exposed inline in the main window
# (below the depth threshold). Selected-only and self-intersect toggles
# remain on the main window. Mesh-pairs feature is no longer available;
# pair selection is implicit (selected meshes or whole scene).
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# StaticCheckSettingsDialog: REMOVED.
# Vertex-share tolerance is now exposed inline in the main window
# (below the depth threshold). Selected-only and self-intersect toggles
# remain on the main window. Mesh-pairs feature is no longer available;
# pair selection is implicit (selected meshes or whole scene).
# ---------------------------------------------------------------------------
class StaticResultWindow(QtWidgets.QDialog):
    """
    Displays intersection / proximity issues in a table.
    Row selection → auto-selects faces in Maya viewport.
    """
    def __init__(self, all_check_items, parent=None):
        super(StaticResultWindow, self).__init__(parent)
        self.setWindowTitle(tr("result_title_static"))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumSize(680, 400)
        self.setStyleSheet(
            "QDialog{background-color:#333;color:#EEE}"
            "QLabel{color:#EEE}"
        )
        self._check_items = all_check_items
        self._rows = []   # list of {issue, check_item}
        self._build()
        self.populate(all_check_items)

    def _build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(8, 8, 8, 8)
        lo.setSpacing(6)

        # Scope label
        self._scope_label = QtWidgets.QLabel("")
        self._scope_label.setStyleSheet(
            "color:#8BC34A;background-color:#2B2B2B;"
            "padding:4px 8px;border-radius:3px;font-size:10px")
        self._scope_label.setWordWrap(True)
        lo.addWidget(self._scope_label)

        # Table: Status | Check | Mesh A | Mesh B | Detail
        self._table = QtWidgets.QTableWidget(0, 5)
        self._table.setStyleSheet(_TABLE_SS)
        self._table.setHorizontalHeaderLabels([
            tr("col_status"), tr("col_check"),
            tr("col_mesh_a"), tr("col_mesh_b"), tr("col_detail"),
        ])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 60)
        self._table.setColumnWidth(1, 100)
        self._table.setColumnWidth(2, 130)
        self._table.setColumnWidth(3, 130)
        self._table.setWordWrap(True)
        self._table.verticalHeader().setDefaultSectionSize(28)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(
            _TABLE_SS + "QTableWidget{alternate-background-color:#323232}")
        self._table.verticalHeader().setVisible(False)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        lo.addWidget(self._table)

        # Bottom bar
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch()
        self._btn_select = _mkbtn(tr("btn_select_faces"), 26, "#2196F3", "#1976D2")
        self._btn_select.clicked.connect(self._select_current_faces)
        bottom.addWidget(self._btn_select)

        btn_close = _mkbtn(tr("btn_close"), 26, "#555", "#444")
        btn_close.clicked.connect(self.hide)
        bottom.addWidget(btn_close)
        lo.addLayout(bottom)

    def populate(self, check_items):
        """Rebuild the table from the current issues of all check items."""
        self._table.setRowCount(0)
        self._rows = []

        total_issues = 0
        scope_parts  = set()

        for ci in check_items:
            if ci.status == "unchecked":
                continue
            for issue in ci.issues:
                row = self._table.rowCount()
                self._table.insertRow(row)

                # Status
                if issue.get("face_a", -1) == -1:
                    status_text  = "ERROR"
                    status_color = "#FF9800"
                else:
                    status_text  = tr("fail_label")
                    status_color = "#F44336"

                st_item = QtWidgets.QTableWidgetItem(status_text)
                st_item.setTextAlignment(QtCore.Qt.AlignCenter)
                st_item.setForeground(QtGui.QColor(status_color))
                font = st_item.font(); font.setBold(True); st_item.setFont(font)
                self._table.setItem(row, 0, st_item)

                # Check name
                self._table.setItem(row, 1,
                    QtWidgets.QTableWidgetItem(ci.label))

                # Mesh A
                short_a = MayaBridge.get_short_name(
                    issue.get("mesh_a", ""))
                self._table.setItem(row, 2,
                    QtWidgets.QTableWidgetItem(short_a))

                # Mesh B
                short_b = MayaBridge.get_short_name(
                    issue.get("mesh_b", ""))
                self._table.setItem(row, 3,
                    QtWidgets.QTableWidgetItem(short_b))

                # Detail
                self._table.setItem(row, 4,
                    QtWidgets.QTableWidgetItem(issue.get("detail", "")))

                self._rows.append({"issue": issue, "check_item": ci})
                total_issues += 1

                if issue.get("mesh_a"):
                    scope_parts.add(MayaBridge.get_short_name(issue["mesh_a"]))
                if issue.get("mesh_b"):
                    scope_parts.add(MayaBridge.get_short_name(issue["mesh_b"]))

        scope_str = ", ".join(sorted(scope_parts)) if scope_parts else "—"
        # Compute total elapsed time across all checks
        total_elapsed = sum(
            getattr(ci, "elapsed_sec", 0.0) for ci in check_items)
        elapsed_str = "  |  {0:.2f}s".format(total_elapsed) if total_elapsed > 0 else ""
        self._scope_label.setText(
            tr("scope_label", scope=scope_str)
            + "  |  {0} issue(s)".format(total_issues)
            + elapsed_str)

    def _on_selection_changed(self):
        """Highlight faces for ALL currently selected rows in Maya."""
        if not MAYA_AVAILABLE:
            return
        rows = sorted(set(i.row() for i in
                          self._table.selectionModel().selectedRows()))
        if not rows:
            return
        self._highlight_rows(rows)

    def _highlight_rows(self, rows):
        """Collect faces from every row in `rows` and select in ONE call."""
        if not MAYA_AVAILABLE:
            return
        comps = []
        for row in rows:
            if row < 0 or row >= len(self._rows):
                continue
            data = self._rows[row]
            issue = data.get("issue", {})
            mesh_a = issue.get("mesh_a", "")
            mesh_b = issue.get("mesh_b", "")

            faces_a = list(issue.get("faces_a", []) or [])
            if not faces_a:
                fa = issue.get("face_a", -1)
                if fa >= 0:
                    faces_a = [fa]
            faces_b = list(issue.get("faces_b", []) or [])
            if not faces_b:
                fb = issue.get("face_b", -1)
                if fb >= 0:
                    faces_b = [fb]

            for fa in faces_a:
                if mesh_a and fa >= 0:
                    comps.append(u"{0}.f[{1}]".format(mesh_a, fa))
            for fb in faces_b:
                if mesh_b and fb >= 0:
                    comps.append(u"{0}.f[{1}]".format(mesh_b, fb))

        if comps:
            try:
                cmds.select(comps, r=True)
            except Exception:
                pass

    def _select_current_faces(self):
        """[Select Faces] button: honor all selected rows (fallback: current)."""
        rows = sorted(set(i.row() for i in
                          self._table.selectionModel().selectedRows()))
        if not rows:
            r = self._table.currentRow()
            if r >= 0:
                rows = [r]
        if rows:
            self._highlight_rows(rows)

    def refresh_labels(self):
        """Re-apply localized strings (called on language toggle)."""
        self.setWindowTitle(tr("result_title_static"))
        headers = [tr("col_status"), tr("col_check"),
                   tr("col_mesh_a"), tr("col_mesh_b"), tr("col_detail")]
        for i, h in enumerate(headers):
            self._table.horizontalHeaderItem(i).setText(h)
        self._btn_select.setText(tr("btn_select_faces"))

class CheckItemWidget(QtWidgets.QFrame):
    check_requested = QtCore.Signal(object)   # emits the CheckItem instance

    def __init__(self, check_item, has_settings=False, parent=None):
        super(CheckItemWidget, self).__init__(parent)
        self.check_item   = check_item
        self.has_settings = has_settings
        self._build()

    def _build(self):
        self.setStyleSheet(
            "QFrame{background-color:#3C3C3C;border:1px solid #555;"
            "border-radius:4px;margin:1px 0px}")
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(8, 5, 8, 5)
        lo.setSpacing(3)

        # Header row
        hl = QtWidgets.QHBoxLayout()
        hl.setSpacing(4)

        # Enable checkbox (for optional checks)
        self._cb_enabled = QtWidgets.QCheckBox()
        self._cb_enabled.setChecked(self.check_item.enabled)
        self._cb_enabled.setFixedSize(16, 16)
        self._cb_enabled.setStyleSheet(
            "QCheckBox{color:#EEE}"
            "QCheckBox::indicator{width:12px;height:12px}")
        self._cb_enabled.toggled.connect(self._on_enabled_toggled)
        hl.addWidget(self._cb_enabled)

        self._icon = QtWidgets.QLabel(_ICON["unchecked"])
        self._icon.setFixedWidth(18)
        self._icon.setAlignment(QtCore.Qt.AlignCenter)
        self._icon.setStyleSheet("color:#888;font-size:13px;font-weight:bold")
        hl.addWidget(self._icon)

        self._title = QtWidgets.QLabel(
            u"<b>{0}</b>".format(self.check_item.label))
        self._title.setStyleSheet("color:#EEE;font-size:11px")
        hl.addWidget(self._title)
        hl.addStretch()

        self._badge = QtWidgets.QLabel("")
        self._badge.setStyleSheet(
            "color:#F44336;font-size:10px;font-weight:bold;margin-right:4px")
        self._badge.setVisible(False)
        hl.addWidget(self._badge)

        if self.has_settings:
            self._btn_settings = QtWidgets.QPushButton(u"\u2699")
            self._btn_settings.setFixedSize(22, 22)
            self._btn_settings.setStyleSheet(
                "QPushButton{background-color:#555;color:#EEE;"
                "border:1px solid #777;border-radius:3px;font-size:12px}"
                "QPushButton:hover{background-color:#607D8B;border-color:#90A4AE}")
            self._btn_settings.clicked.connect(self._open_settings)
            hl.addWidget(self._btn_settings)

        self._btn_check = QtWidgets.QPushButton(self._action_button_label())
        self._btn_check.setFixedSize(60, 22)
        self._btn_check.setStyleSheet(
            "QPushButton{background-color:#2196F3;color:white;border:none;"
            "border-radius:3px;font-size:10px;font-weight:bold}"
            "QPushButton:hover{background-color:#1976D2}"
            "QPushButton:disabled{background-color:#444;color:#666}")
        self._btn_check.clicked.connect(self._on_check)
        hl.addWidget(self._btn_check)

        lo.addLayout(hl)

        self._desc = QtWidgets.QLabel(self.check_item.description)
        self._desc.setStyleSheet("color:#AAA;font-size:9px;padding-left:20px")
        self._desc.setWordWrap(True)
        lo.addWidget(self._desc)

        # Apply initial enabled state
        self._apply_enabled_state()

    def _on_enabled_toggled(self, checked):
        self.check_item.enabled = checked
        self._apply_enabled_state()

    def _apply_enabled_state(self):
        enabled = self.check_item.enabled
        self._btn_check.setEnabled(enabled)
        opacity = "1.0" if enabled else "0.4"
        self._title.setStyleSheet(
            "color:#EEE;font-size:11px;opacity:{0}".format(opacity))
        self._desc.setStyleSheet(
            "color:{0};font-size:9px;padding-left:20px".format(
                "#AAA" if enabled else "#666"))
        self._icon.setStyleSheet(
            "color:{0};font-size:13px;font-weight:bold".format(
                "#888" if enabled else "#555"))

    def _on_check(self):
        self._btn_check.setEnabled(False)
        self._icon.setText(u"\u29D7")  # hourglass-like placeholder
        self._icon.setStyleSheet("color:#FF9800;font-size:13px;font-weight:bold")
        QtWidgets.QApplication.processEvents()

        self.check_item.run_check()
        self._update_ui()
        self._btn_check.setEnabled(True)
        self.check_requested.emit(self.check_item)

    def _open_settings(self):
        # Settings dialog removed; kept as no-op for backward compatibility.
        pass

    def _update_ui(self):
        s = self.check_item.status
        self._icon.setText(_ICON.get(s, _ICON["unchecked"]))
        self._icon.setStyleSheet(
            "color:{c};font-size:13px;font-weight:bold".format(
                c=_ICON_COLOR.get(s, "#888")))
        n = len(self.check_item.issues)
        if n:
            self._badge.setText("({0})".format(n))
            self._badge.setVisible(True)
        else:
            self._badge.setVisible(False)

    def refresh_labels(self):
        self._title.setText(u"<b>{0}</b>".format(self.check_item.label))
        self._desc.setText(self.check_item.description)
        self._btn_check.setText(self._action_button_label())

    def _action_button_label(self):
        # Move/action items use btn_move; checks use btn_check
        if getattr(self.check_item, "is_action", False):
            return tr("btn_move")
        return tr("btn_check")

    def reset(self):
        self.check_item.status = "unchecked"
        self.check_item.issues = []
        self._icon.setText(_ICON["unchecked"])
        self._icon.setStyleSheet("color:#888;font-size:13px;font-weight:bold")
        self._badge.setVisible(False)



# ---------------------------------------------------------------------------
# CollisionCheckToolWindow  (Main UI — reference architecture compliant)
# ---------------------------------------------------------------------------
_MAIN_SS = (
    "QDialog{background-color:#333}"
    "QScrollArea{border:none;background-color:transparent}"
    "QScrollBar:vertical{background:#2B2B2B;width:10px}"
    "QScrollBar::handle:vertical{background:#555;border-radius:4px}"
    "QGroupBox{border-radius:6px;background-color:#2E2E2E;margin-top:6px}"
    "QGroupBox::title{subcontrol-origin:margin;left:10px;"
    "color:#EEE;font-size:11px;font-weight:bold}"
    "QLabel{color:#EEE}"
)

# -*- coding: utf-8 -*-
# ============================================================================
# 0350_vertex_snap.txt
# Vertex Snap feature for DW_CollisionCheck "Snap" tab.
#
# Depends on (defined earlier in the concatenated build):
#   VERSION, PY2, MAYA_AVAILABLE, cmds, mel,
#   QtCore, QtGui, QtWidgets, wrapInstance, omui,
#   tr(), _STRINGS  (strings added in 0020_strings.txt),
#   _mkbtn()        (defined in 0200_ui_helpers.txt)
# ============================================================================


# ---------------------------------------------------------------------------
# Vertex snap: geometry helpers
# ---------------------------------------------------------------------------

def _vs_get_mesh_verts():
    """Get all verts from selected meshes (traverses hierarchy).
    Returns (vert_data, mesh_short_names).
    vert_data = [(vtx_name, mesh_short, vtx_idx, (x,y,z)), ...]"""
    if not MAYA_AVAILABLE:
        return [], []
    sel = cmds.ls(sl=True, l=True) or []
    if not sel:
        return [], []
    meshes = set()
    for s in sel:
        node = s.split(".")[0]
        for sh in (cmds.listRelatives(node, s=True, f=True, type="mesh") or []):
            try:
                if cmds.getAttr(sh + ".intermediateObject"):
                    continue
            except Exception:
                pass
            xf = cmds.listRelatives(sh, p=True, f=True)
            if xf:
                meshes.add(xf[0])
        for sh in (cmds.listRelatives(node, ad=True, f=True, type="mesh") or []):
            try:
                if cmds.getAttr(sh + ".intermediateObject"):
                    continue
            except Exception:
                pass
            xf = cmds.listRelatives(sh, p=True, f=True)
            if xf:
                meshes.add(xf[0])
    if not meshes:
        return [], []
    vdata = []
    for m in sorted(meshes):
        n = cmds.polyEvaluate(m, v=True)
        for i in range(n):
            vtx = u"{0}.vtx[{1}]".format(m, i)
            p = cmds.pointPosition(vtx, w=True)
            vdata.append((vtx, m.split("|")[-1], i, (p[0], p[1], p[2])))
    short = [m.split("|")[-1] for m in sorted(meshes)]
    return vdata, short


def _vs_find_close_pairs(vdata, threshold, cross_only=False):
    """Return pairs within threshold.
    Each pair = (vtxA, meshA, idxA, posA, vtxB, meshB, idxB, posB, dist)."""
    pairs = []
    n = len(vdata)
    for i in range(n):
        va, ma, ia, pa = vdata[i]
        for j in range(i + 1, n):
            vb, mb, ib, pb = vdata[j]
            if va == vb:
                continue
            if cross_only and ma == mb:
                continue
            dx = pa[0] - pb[0]
            dy = pa[1] - pb[1]
            dz = pa[2] - pb[2]
            d = math.sqrt(dx * dx + dy * dy + dz * dz)
            if d <= threshold:
                pairs.append((va, ma, ia, pa, vb, mb, ib, pb, d))
    pairs.sort(key=lambda x: x[8])
    return pairs


def _vs_snap_one(va, pa, vb, pb, direction):
    """direction: 0=A->B, 1=B->A, 2=midpoint. Returns #verts moved."""
    if direction == 0:
        cmds.xform(va, ws=True, t=[pb[0], pb[1], pb[2]]); return 1
    elif direction == 1:
        cmds.xform(vb, ws=True, t=[pa[0], pa[1], pa[2]]); return 1
    else:
        mx = (pa[0]+pb[0])*0.5; my = (pa[1]+pb[1])*0.5; mz = (pa[2]+pb[2])*0.5
        cmds.xform(va, ws=True, t=[mx, my, mz])
        cmds.xform(vb, ws=True, t=[mx, my, mz]); return 2


# ---------------------------------------------------------------------------
# Vertex snap: UI constants
# ---------------------------------------------------------------------------

_VS_TABLE_SS = (
    "QTableWidget{background-color:#2B2B2B;alternate-background-color:#323232;"
    "color:#DDD;gridline-color:#444;border:1px solid #444;font-size:11px}"
    "QTableWidget::item:selected{background-color:#1565C0}"
    "QHeaderView::section{background-color:#3C3C3C;color:#EEE;"
    "border:1px solid #555;padding:4px;font-size:10px;font-weight:bold}"
    "QScrollBar:vertical{background:#2B2B2B;width:10px}"
    "QScrollBar::handle:vertical{background:#555;border-radius:4px}")

_VS_SPIN_SS = ("QDoubleSpinBox{background-color:#2B2B2B;color:#EEE;"
               "border:1px solid #555;border-radius:3px;padding:1px;font-size:10px}")

_VS_DIR_LABELS = {0: "vs_snap_ab", 1: "vs_snap_ba", 2: "vs_snap_mid"}
_VS_DIR_COLORS = {0: "#2196F3", 1: "#FF9800", 2: "#4CAF50"}


# ---------------------------------------------------------------------------
# Distance histogram (interactive — drag to set threshold)
# ---------------------------------------------------------------------------

_VS_NUM_BINS = 40


def _vs_bar_color(ratio, active):
    if ratio < 0.33:
        r, g, b = 76, 175, 80
    elif ratio < 0.66:
        r, g, b = 255, 152, 0
    else:
        r, g, b = 244, 67, 54
    if not active:
        r = int(r * 0.25); g = int(g * 0.25); b = int(b * 0.25)
    return QtGui.QColor(r, g, b)


class VertexSnapHistogram(QtWidgets.QWidget):
    """Draggable histogram — click/drag to set threshold."""

    threshold_changed = QtCore.Signal(float)

    _MARGIN_L = 4
    _MARGIN_R = 4
    _MARGIN_T = 14
    _MARGIN_B = 14

    def __init__(self, parent=None):
        super(VertexSnapHistogram, self).__init__(parent)
        self.setFixedHeight(100)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._bins = []
        self._max_dist = 1.0
        self._threshold = 0.01
        self._total = 0
        self._within = 0
        self._dragging = False
        self._hover_x = -1

    def set_data(self, distances, max_dist):
        self._max_dist = max(max_dist, 0.0001)
        self._bins = [0] * _VS_NUM_BINS
        for d in distances:
            idx = int(d / self._max_dist * _VS_NUM_BINS)
            if idx >= _VS_NUM_BINS:
                idx = _VS_NUM_BINS - 1
            self._bins[idx] += 1
        self._total = len(distances)
        self._update_within()
        self.update()

    def set_threshold(self, th):
        self._threshold = th
        self._update_within()
        self.update()

    def _update_within(self):
        th_bin = int(self._threshold / self._max_dist * _VS_NUM_BINS)
        self._within = sum(self._bins[:min(th_bin + 1, _VS_NUM_BINS)])

    def _bar_area(self):
        w = self.width(); h = self.height()
        return (self._MARGIN_L, self._MARGIN_T,
                w - self._MARGIN_L - self._MARGIN_R,
                h - self._MARGIN_T - self._MARGIN_B)

    def _x_to_dist(self, x):
        bx, by, bw, bh = self._bar_area()
        ratio = max(0.0, min(1.0, (x - bx) / float(max(bw, 1))))
        return ratio * self._max_dist

    def _dist_to_x(self, d):
        bx, by, bw, bh = self._bar_area()
        return bx + min(d / self._max_dist, 1.0) * bw

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._dragging = True
            self._set_th_from_x(event.x())

    def mouseMoveEvent(self, event):
        self._hover_x = event.x()
        if self._dragging:
            self._set_th_from_x(event.x())
        self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def leaveEvent(self, event):
        self._hover_x = -1
        self.update()

    def _set_th_from_x(self, x):
        d = self._x_to_dist(x)
        d = max(0.0001, round(d, 4))
        if abs(d - self._threshold) > 0.00001:
            self._threshold = d
            self._update_within()
            self.threshold_changed.emit(d)
            self.update()

    def paintEvent(self, event):
        if not self._bins:
            return
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        bx, by, bw, bh = self._bar_area()
        max_count = max(self._bins) if self._bins else 1
        if max_count == 0:
            max_count = 1
        n = len(self._bins)
        bar_w = bw / float(n)
        gap = max(1, int(bar_w * 0.12))
        th_x = self._dist_to_x(self._threshold)

        p.fillRect(int(bx), int(by), int(bw), int(bh),
                   QtGui.QColor(35, 35, 35))

        for i in range(n):
            count = self._bins[i]
            if count == 0:
                continue
            h = int((count / float(max_count)) * bh)
            x = bx + int(i * bar_w) + gap
            w = max(1, int(bar_w) - gap * 2)
            y = by + bh - h
            ratio = i / float(n)
            active = (x + w) <= (th_x + 1)
            p.fillRect(int(x), int(y), int(w), int(h),
                       _vs_bar_color(ratio, active))

        if self._hover_x >= bx and self._hover_x <= bx + bw and not self._dragging:
            pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 40), 1)
            p.setPen(pen)
            p.drawLine(int(self._hover_x), int(by),
                       int(self._hover_x), int(by + bh))

        pen = QtGui.QPen(QtGui.QColor("#42A5F5"), 2)
        p.setPen(pen)
        p.drawLine(int(th_x), int(by - 2), int(th_x), int(by + bh + 2))

        p.setBrush(QtGui.QColor("#42A5F5"))
        p.setPen(QtCore.Qt.NoPen)
        p.drawEllipse(int(th_x) - 5, int(by + bh) - 1, 10, 10)

        p.setPen(QtGui.QColor("#42A5F5"))
        p.setFont(QtGui.QFont("", 8, QtGui.QFont.Bold))
        label = u"{0:.4f}".format(self._threshold)
        lx = int(th_x) + 6
        if lx + 48 > bx + bw:
            lx = int(th_x) - 52
        p.drawText(lx, by - 1, label)

        p.setPen(QtGui.QColor("#AAA"))
        p.setFont(QtGui.QFont("", 8))
        txt = u"{0} / {1}".format(self._within, self._total)
        p.drawText(int(bx + bw - 60), by - 1, 58, 12,
                   QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, txt)

        p.setPen(QtGui.QColor("#555"))
        p.setFont(QtGui.QFont("", 7))
        bottom_y = by + bh + 3
        p.drawText(int(bx), int(bottom_y), u"0")
        max_label = u"{0:.2f}".format(self._max_dist)
        p.drawText(int(bx + bw - 30), int(bottom_y), max_label)

        p.end()


# ---------------------------------------------------------------------------
# VertexSnapResultWindow
# ---------------------------------------------------------------------------

class VertexSnapResultWindow(QtWidgets.QDialog):
    """Pair table with histogram, snap logging, confirm/revert."""

    status_msg = QtCore.Signal(str)

    _HIST_MAX   = 1.0
    _COINCIDENT = 1e-6

    def __init__(self, parent=None):
        super(VertexSnapResultWindow, self).__init__(parent)
        self.setObjectName("DW_VertexSnap_Result")
        self.setWindowTitle(tr("vs_result_title"))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumSize(640, 480)
        self.setStyleSheet(
            "QDialog{background-color:#333;color:#EEE}"
            "QLabel{color:#EEE}")
        self._vdata = []
        self._all_pairs = []
        self._pairs = []
        self._row_to_pair = []
        self._snap_log = {}
        self._undo_open = False
        self._build()

    def _build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(8, 8, 8, 8); lo.setSpacing(6)

        # Scope label (mesh names)
        self._scope_mesh = QtWidgets.QLabel("")
        self._scope_mesh.setStyleSheet(
            "color:#8BC34A;background-color:#2B2B2B;"
            "padding:3px 8px;border-radius:3px;font-size:10px")
        self._scope_mesh.setWordWrap(True)
        lo.addWidget(self._scope_mesh)

        # Interactive histogram
        self._histogram = VertexSnapHistogram()
        self._histogram.threshold_changed.connect(self._on_hist_drag)
        lo.addWidget(self._histogram)

        # Threshold spin
        thr = QtWidgets.QHBoxLayout(); thr.setSpacing(6)
        self._lbl_th = QtWidgets.QLabel(tr("vs_lbl_threshold"))
        self._lbl_th.setStyleSheet("color:#AAA;font-size:10px")
        thr.addWidget(self._lbl_th)
        self._spin = QtWidgets.QDoubleSpinBox()
        self._spin.setRange(0.0001, 10.0); self._spin.setDecimals(4)
        self._spin.setSingleStep(0.001); self._spin.setValue(0.01)
        self._spin.setFixedWidth(85); self._spin.setStyleSheet(_VS_SPIN_SS)
        self._spin.valueChanged.connect(self._on_spin)
        thr.addWidget(self._spin)
        thr.addStretch()
        lo.addLayout(thr)

        # Count + option checkboxes
        cnt_row = QtWidgets.QHBoxLayout(); cnt_row.setSpacing(8)
        self._scope_count = QtWidgets.QLabel("")
        self._scope_count.setStyleSheet("color:#FF9800;font-size:10px;padding:0 4px")
        cnt_row.addWidget(self._scope_count)
        cnt_row.addStretch()
        cb_ss = ("QCheckBox{color:#AAA;font-size:10px}"
                 "QCheckBox::indicator{width:12px;height:12px}")
        self._cb_include_same = QtWidgets.QCheckBox(tr("vs_chk_include_same"))
        self._cb_include_same.setChecked(True)
        self._cb_include_same.setStyleSheet(cb_ss)
        self._cb_include_same.toggled.connect(self._on_include_same_toggled)
        cnt_row.addWidget(self._cb_include_same)
        self._cb_hide_coinc = QtWidgets.QCheckBox(tr("vs_chk_hide_coinc"))
        self._cb_hide_coinc.setChecked(True)
        self._cb_hide_coinc.setStyleSheet(cb_ss)
        self._cb_hide_coinc.toggled.connect(lambda _: self._populate())
        cnt_row.addWidget(self._cb_hide_coinc)
        lo.addLayout(cnt_row)

        # Pair table
        self._table = QtWidgets.QTableWidget(0, 6)
        self._update_headers()
        h = self._table.horizontalHeader()
        self._table.setColumnWidth(0, 42)
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(22)
        self._table.setStyleSheet(_VS_TABLE_SS)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        lo.addWidget(self._table, 1)

        # Snap direction buttons
        sr = QtWidgets.QHBoxLayout(); sr.setSpacing(4)
        self._btn_ab = _mkbtn(tr("vs_btn_snap_ab"), 26, "#2196F3", "#1976D2", fs=10)
        self._btn_ab.clicked.connect(lambda: self._on_snap(0))
        sr.addWidget(self._btn_ab)
        self._btn_ba = _mkbtn(tr("vs_btn_snap_ba"), 26, "#FF9800", "#F57C00", fs=10)
        self._btn_ba.clicked.connect(lambda: self._on_snap(1))
        sr.addWidget(self._btn_ba)
        self._btn_mid = _mkbtn(tr("vs_btn_snap_mid"), 26, "#4CAF50", "#388E3C", fs=10)
        self._btn_mid.clicked.connect(lambda: self._on_snap(2))
        sr.addWidget(self._btn_mid)
        sr.addStretch()
        lo.addLayout(sr)

        # Confirm / Revert / Merge / Close
        cr = QtWidgets.QHBoxLayout(); cr.setSpacing(4)
        self._btn_confirm = _mkbtn(tr("vs_btn_confirm"), 26, "#4CAF50", "#388E3C", fs=10)
        self._btn_confirm.clicked.connect(self._on_confirm)
        self._btn_confirm.setEnabled(False)
        cr.addWidget(self._btn_confirm)
        self._btn_revert = _mkbtn(tr("vs_btn_revert"), 26, "#F44336", "#D32F2F", fs=10)
        self._btn_revert.clicked.connect(self._on_revert)
        self._btn_revert.setEnabled(False)
        cr.addWidget(self._btn_revert)
        cr.addStretch()
        self._btn_merge = _mkbtn(tr("vs_btn_merge_maya"), 26, "#9C27B0", "#7B1FA2", fs=10)
        self._btn_merge.clicked.connect(self._on_merge_maya)
        cr.addWidget(self._btn_merge)
        btn_close = _mkbtn(tr("btn_close"), 26, "#555", "#444", fs=10)
        btn_close.clicked.connect(self.hide)
        cr.addWidget(btn_close)
        lo.addLayout(cr)

    def _update_headers(self):
        self._table.setHorizontalHeaderLabels([
            u"", tr("vs_col_mesh_a"), tr("vs_col_vtx_a"),
            tr("vs_col_mesh_b"), tr("vs_col_vtx_b"), tr("vs_col_dist")])

    # -- Data setup --
    def set_data(self, vdata, mesh_names):
        self._vdata = list(vdata)
        self._snap_log = {}
        self._close_undo()
        self._scope_mesh.setText(tr("vs_scope_meshes", names=u", ".join(mesh_names)))
        self._recompute_all_pairs()
        self._refilter()
        self._update_confirm_state()

    def _recompute_all_pairs(self):
        cross = not self._cb_include_same.isChecked()
        self._all_pairs = _vs_find_close_pairs(
            self._vdata, self._HIST_MAX, cross_only=cross)
        dists = [p[8] for p in self._all_pairs]
        self._histogram.set_data(dists, self._HIST_MAX)

    def _on_include_same_toggled(self, checked):
        self._recompute_all_pairs()
        self._refilter()

    def _refilter(self):
        th = self._spin.value()
        self._pairs = [p for p in self._all_pairs if p[8] <= th]
        self._histogram.set_threshold(th)
        self._populate()

    def _populate(self):
        self._table.setRowCount(0)
        self._row_to_pair = []
        th = max(self._spin.value(), 0.0001)
        hide_coinc = self._cb_hide_coinc.isChecked()
        hidden = 0

        for idx, (va, ma, ia, pa, vb, mb, ib, pb, dist) in enumerate(self._pairs):
            key = self._pair_key(va, vb)
            snap_dir = self._snap_log.get(key)

            # Hide already-coincident pairs (not snapped in this session)
            if hide_coinc and dist < self._COINCIDENT and snap_dir is None:
                hidden += 1
                continue

            r = self._table.rowCount(); self._table.insertRow(r)
            self._row_to_pair.append(idx)

            if snap_dir is not None:
                icon = u"\u2714"
                color = _VS_DIR_COLORS.get(snap_dir, "#888")
                tip = tr(_VS_DIR_LABELS.get(snap_dir, "vs_snap_ab"))
            else:
                icon = u"\u25CB"
                color = "#666"
                tip = u""
            si = QtWidgets.QTableWidgetItem(icon)
            si.setForeground(QtGui.QColor(color))
            si.setTextAlignment(QtCore.Qt.AlignCenter)
            si.setToolTip(tip)
            self._table.setItem(r, 0, si)

            mi_a = QtWidgets.QTableWidgetItem(ma)
            mi_a.setForeground(QtGui.QColor("#8BC34A"))
            f = mi_a.font(); f.setBold(True); mi_a.setFont(f)
            self._table.setItem(r, 1, mi_a)
            self._table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(ia)))

            mi_b = QtWidgets.QTableWidgetItem(mb)
            mi_b.setForeground(QtGui.QColor("#81D4FA"))
            fb = mi_b.font(); fb.setBold(True); mi_b.setFont(fb)
            self._table.setItem(r, 3, mi_b)
            self._table.setItem(r, 4, QtWidgets.QTableWidgetItem(str(ib)))

            di = QtWidgets.QTableWidgetItem(u"{0:.6f}".format(dist))
            di.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            ratio = dist / th
            if ratio < 0.3:
                di.setForeground(QtGui.QColor("#4CAF50"))
            elif ratio < 0.7:
                di.setForeground(QtGui.QColor("#FF9800"))
            else:
                di.setForeground(QtGui.QColor("#F44336"))
            self._table.setItem(r, 5, di)

            if snap_dir is not None:
                for c in range(1, 6):
                    item = self._table.item(r, c)
                    if item:
                        item.setForeground(QtGui.QColor("#666"))

        n = len(self._pairs)
        sn = len(self._snap_log)
        txt = tr("vs_scope_pairs", count=n, th=self._spin.value())
        if sn:
            txt += u"  ({0} snapped)".format(sn)
        if hidden:
            txt += u"  [{0} coincident hidden]".format(hidden)
        self._scope_count.setText(txt)

    def _pair_key(self, va, vb):
        return va + "|" + vb

    # -- Threshold sync --
    def _on_spin(self, val):
        self._refilter()

    def _on_hist_drag(self, val):
        self._spin.blockSignals(True)
        self._spin.setValue(val)
        self._spin.blockSignals(False)
        self._refilter()

    # -- Row selection -> highlight all selected pairs' vertices in Maya --
    def _on_selection_changed(self):
        if not MAYA_AVAILABLE:
            return
        rows = sorted(set(i.row() for i in
                          self._table.selectionModel().selectedRows()))
        if not rows:
            return
        comps = []
        for row in rows:
            if row < 0 or row >= len(self._row_to_pair):
                continue
            pi = self._row_to_pair[row]
            p = self._pairs[pi]
            comps.append(p[0])  # vertex A
            comps.append(p[4])  # vertex B
        if comps:
            try:
                cmds.select(comps, r=True)
            except Exception:
                pass

    # -- Snap (logged, not finalized until Confirm) --
    def _on_snap(self, direction):
        rows = sorted(set(i.row() for i in self._table.selectionModel().selectedRows()))
        if not rows:
            self.status_msg.emit(tr("vs_status_no_sel")); return
        if not self._undo_open:
            cmds.undoInfo(openChunk=True, chunkName="DW_VertexSnap")
            self._undo_open = True
        for r in rows:
            if r >= len(self._row_to_pair):
                continue
            pi = self._row_to_pair[r]
            p = self._pairs[pi]
            va, pa, vb, pb = p[0], p[3], p[4], p[7]
            key = self._pair_key(va, vb)
            if key in self._snap_log:
                continue
            _vs_snap_one(va, pa, vb, pb, direction)
            self._snap_log[key] = direction
        self._populate()
        self._update_confirm_state()
        self.status_msg.emit(tr("vs_status_snapped", count=len(self._snap_log)))

    # -- Confirm / Revert --
    def _on_confirm(self):
        n = len(self._snap_log)
        self._close_undo()
        self._snap_log = {}
        self._update_confirm_state()
        self.status_msg.emit(tr("vs_status_confirmed", count=n))
        self._refresh_vdata()

    def _on_revert(self):
        self._close_undo()
        if MAYA_AVAILABLE:
            try:
                cmds.undo()
            except Exception:
                pass
        self._snap_log = {}
        self._update_confirm_state()
        self.status_msg.emit(tr("vs_status_reverted"))
        self._refresh_vdata()

    def _refresh_vdata(self):
        if not MAYA_AVAILABLE:
            return
        new_vdata = []
        for vtx, mesh, idx, pos in self._vdata:
            try:
                p = cmds.pointPosition(vtx, w=True)
                new_vdata.append((vtx, mesh, idx, (p[0], p[1], p[2])))
            except Exception:
                new_vdata.append((vtx, mesh, idx, pos))
        self._vdata = new_vdata
        self._recompute_all_pairs()
        self._refilter()

    def _close_undo(self):
        if self._undo_open:
            try:
                cmds.undoInfo(closeChunk=True)
            except Exception:
                pass
            self._undo_open = False

    def _update_confirm_state(self):
        has_log = len(self._snap_log) > 0
        self._btn_confirm.setEnabled(has_log)
        self._btn_revert.setEnabled(has_log)

    def _on_merge_maya(self):
        """Open Maya's native Merge Vertices option box."""
        if not MAYA_AVAILABLE:
            return
        try:
            mel.eval("MergeVerticesOptions;")
        except Exception:
            try:
                mel.eval("performPolyMerge 1;")
            except Exception:
                pass

    def refresh_labels(self):
        self.setWindowTitle(tr("vs_result_title"))
        self._update_headers()
        self._lbl_th.setText(tr("vs_lbl_threshold"))
        self._cb_hide_coinc.setText(tr("vs_chk_hide_coinc"))
        self._cb_include_same.setText(tr("vs_chk_include_same"))
        self._btn_ab.setText(tr("vs_btn_snap_ab"))
        self._btn_ba.setText(tr("vs_btn_snap_ba"))
        self._btn_mid.setText(tr("vs_btn_snap_mid"))
        self._btn_confirm.setText(tr("vs_btn_confirm"))
        self._btn_revert.setText(tr("vs_btn_revert"))
        self._btn_merge.setText(tr("vs_btn_merge_maya"))

    def closeEvent(self, event):
        if self._undo_open:
            self._close_undo()
        super(VertexSnapResultWindow, self).closeEvent(event)


# ---------------------------------------------------------------------------
# Snap tab group builder
#
# Called from CollisionCheckToolWindow._build() to build the Snap tab.
# Adds a "Vertex Snap" group (blue border) with a launch button that
# opens the VertexSnapResultWindow.
# ---------------------------------------------------------------------------

def _build_vertex_snap_group(tool_window, parent_layout):
    """Build the Vertex Snap group for the Snap tab.
    `tool_window` is the CollisionCheckToolWindow instance — the group
    stores the result window reference on it (tool_window._vs_result_window).
    Returns the QGroupBox so the caller can track label refs if needed.
    """
    grp = QtWidgets.QGroupBox()
    grp.setStyleSheet(
        "QGroupBox{border:1px solid #2196F3;border-radius:6px;"
        "background-color:#2E2E2E;margin-top:6px}"
        "QGroupBox::title{subcontrol-origin:margin;left:10px;"
        "color:#EEE;font-size:11px;font-weight:bold}")
    lo = QtWidgets.QVBoxLayout(grp)
    lo.setContentsMargins(6, 10, 6, 6)
    lo.setSpacing(4)

    # Header: title + launch button
    hdr = QtWidgets.QHBoxLayout()
    tool_window._vs_grp_lbl = QtWidgets.QLabel(u"\u25A0 " + tr("vs_grp_title"))
    tool_window._vs_grp_lbl.setStyleSheet(
        "color:#2196F3;font-size:11px;font-weight:bold")
    hdr.addWidget(tool_window._vs_grp_lbl)
    hdr.addStretch()
    tool_window._vs_btn_launch = _mkbtn(
        tr("vs_btn_launch"), 24, "#2196F3", "#1976D2", fs=10)
    tool_window._vs_btn_launch.clicked.connect(
        lambda: _vs_launch(tool_window))
    hdr.addWidget(tool_window._vs_btn_launch)
    lo.addLayout(hdr)

    # Description line
    tool_window._vs_desc_lbl = QtWidgets.QLabel(tr("vs_grp_desc"))
    tool_window._vs_desc_lbl.setStyleSheet(
        "color:#AAA;font-size:10px;padding:2px 4px")
    tool_window._vs_desc_lbl.setWordWrap(True)
    lo.addWidget(tool_window._vs_desc_lbl)

    parent_layout.addWidget(grp)
    return grp


def _vs_launch(tool_window):
    """Collect selected meshes, build pairs, open result window."""
    vdata, mesh_names = _vs_get_mesh_verts()
    if not vdata:
        if hasattr(tool_window, "_status_bar"):
            tool_window._status_bar.setText(tr("vs_status_no_mesh"))
        return

    if not hasattr(tool_window, "_vs_result_window"):
        tool_window._vs_result_window = None

    if tool_window._vs_result_window is None:
        tool_window._vs_result_window = VertexSnapResultWindow(parent=tool_window)
        tool_window._vs_result_window.status_msg.connect(
            lambda t: tool_window._status_bar.setText(t)
            if hasattr(tool_window, "_status_bar") else None)

    tool_window._vs_result_window.set_data(vdata, mesh_names)
    tool_window._vs_result_window.show()
    tool_window._vs_result_window.raise_()
    tool_window._vs_result_window.activateWindow()


def _vs_refresh_labels(tool_window):
    """Called from CollisionCheckToolWindow._refresh_labels()."""
    if hasattr(tool_window, "_vs_grp_lbl"):
        tool_window._vs_grp_lbl.setText(u"\u25A0 " + tr("vs_grp_title"))
    if hasattr(tool_window, "_vs_btn_launch"):
        tool_window._vs_btn_launch.setText(tr("vs_btn_launch"))
    if hasattr(tool_window, "_vs_desc_lbl"):
        tool_window._vs_desc_lbl.setText(tr("vs_grp_desc"))
    if getattr(tool_window, "_vs_result_window", None):
        tool_window._vs_result_window.refresh_labels()


def _vs_close_result_window(tool_window):
    """Called from CollisionCheckToolWindow close/reload."""
    if getattr(tool_window, "_vs_result_window", None):
        try:
            tool_window._vs_result_window.close()
        except Exception:
            pass
# -*- coding: utf-8 -*-
# ============================================================================
# 0360_mesh_landing.txt
# Mesh Landing feature for DW_CollisionCheck "Other" tab.
#
# Replaces the previous Move-to-Origin tool. Lands a source mesh onto a
# target mesh along a chosen axis by raycasting every vertex and verifying
# with polygon-level collision (with binary-search fallback for rotated
# meshes).
#
# Depends on (defined earlier in the concatenated build):
#   VERSION, PY2, MAYA_AVAILABLE, cmds, om, omui,
#   QtCore, QtGui, QtWidgets, wrapInstance,
#   tr(),           (strings added in 0020_strings.txt with ml_* keys)
#   _mkbtn()        (defined in 0200_ui_helpers.txt)
# ============================================================================

import math as _ml_math


# ---------------------------------------------------------------------------
# Raycaster — casts against specific target meshes (api1, accelParams cached)
# ---------------------------------------------------------------------------

_ML_RAY_EPS = 1.0e-5


class MeshLandingRaycaster(object):
    def __init__(self, target_shapes):
        self._fn_cache = {}
        self._targets = []
        for s in target_shapes:
            fn = self._make_mfn(s)
            if fn is None:
                continue
            self._fn_cache[s] = fn
            self._targets.append(s)

    @staticmethod
    def _make_mfn(shape):
        try:
            sel = om.MSelectionList()
            sel.add(shape)
            dag = om.MDagPath()
            sel.getDagPath(0, dag)
            try:
                dag.extendToShape()
            except Exception:
                pass
            return om.MFnMesh(dag)
        except Exception:
            return None

    def cast(self, source_point, direction, max_distance=1.0e9,
             debug=False):
        """Cast a ray; return closest hit distance along `direction`, or None.

        Uses MFnMesh.closestIntersection with no accel grid. Any exception
        is logged (with debug=True) so a silent failure cannot hide the
        root cause of bugs.
        """
        ray_src = om.MFloatPoint(float(source_point[0]),
                                 float(source_point[1]),
                                 float(source_point[2]))
        dlen = _ml_math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
        if dlen < _ML_RAY_EPS:
            return None
        ray_dir = om.MFloatVector(float(direction[0] / dlen),
                                  float(direction[1] / dlen),
                                  float(direction[2] / dlen))
        best = None
        for shape in self._targets:
            fn = self._fn_cache[shape]
            # Output buffers — standard Maya API1 idiom.
            hit_pt = om.MFloatPoint()
            hit_rp_util = om.MScriptUtil(0.0)
            hit_rp_ptr = hit_rp_util.asFloatPtr()
            hit_face_util = om.MScriptUtil(0)
            hit_face_ptr = hit_face_util.asIntPtr()
            hit_tri_util = om.MScriptUtil(0)
            hit_tri_ptr = hit_tri_util.asIntPtr()
            hit_b1_util = om.MScriptUtil(0.0)
            hit_b1_ptr = hit_b1_util.asFloatPtr()
            hit_b2_util = om.MScriptUtil(0.0)
            hit_b2_ptr = hit_b2_util.asFloatPtr()

            got = False
            try:
                got = fn.closestIntersection(
                    ray_src,
                    ray_dir,
                    None,                 # faceIds
                    None,                 # triIds
                    False,                # idsSorted
                    om.MSpace.kWorld,
                    float(max_distance),
                    False,                # testBothDirections
                    None,                 # accelParams
                    False,                # sortHits — not used by closestIntersection
                    hit_pt,
                    hit_rp_ptr,
                    hit_face_ptr,
                    hit_tri_ptr,
                    hit_b1_ptr,
                    hit_b2_ptr,
                    _ML_RAY_EPS,
                )
            except Exception as _e:
                if debug:
                    import traceback
                    print(u"[DW MeshLanding] closestIntersection exception "
                          u"on {0}: {1}".format(shape, _e))
                    traceback.print_exc()
                continue
            if not got:
                if debug:
                    print(u"[DW MeshLanding]  ray miss on {0}".format(shape))
                continue
            d = om.MScriptUtil.getFloat(hit_rp_ptr)
            if debug:
                print(u"[DW MeshLanding]  ray hit on {0}: dist={1}".format(
                    shape, d))
            if d is None:
                continue
            if d <= _ML_RAY_EPS:
                continue
            if _ml_math.isnan(d) or _ml_math.isinf(d):
                continue
            if best is None or d < best:
                best = d
        return best


# ---------------------------------------------------------------------------
# Lightweight tri-tri intersection (Moller 1997 variant, no BVH)
# ---------------------------------------------------------------------------

_ML_EPS = 1.0e-7


def _ml_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _ml_cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])


def _ml_dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def _ml_veclen(a):
    return _ml_math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])


def _ml_vecnorm(a):
    L = _ml_veclen(a)
    if L < _ML_EPS:
        return (0.0, 0.0, 0.0)
    return (a[0]/L, a[1]/L, a[2]/L)


def _ml_tri_aabb(tri):
    xs = [tri[0][0], tri[1][0], tri[2][0]]
    ys = [tri[0][1], tri[1][1], tri[2][1]]
    zs = [tri[0][2], tri[1][2], tri[2][2]]
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))


def _ml_aabb_overlap(a, b):
    if a[3] < b[0] or b[3] < a[0]:
        return False
    if a[4] < b[1] or b[4] < a[1]:
        return False
    if a[5] < b[2] or b[5] < a[2]:
        return False
    return True


def _ml_aabb_merge_tris(tris):
    if not tris:
        return (0, 0, 0, 0, 0, 0)
    INF = float("inf")
    mn = [INF, INF, INF]
    mx = [-INF, -INF, -INF]
    for t in tris:
        for v in t:
            if v[0] < mn[0]: mn[0] = v[0]
            if v[1] < mn[1]: mn[1] = v[1]
            if v[2] < mn[2]: mn[2] = v[2]
            if v[0] > mx[0]: mx[0] = v[0]
            if v[1] > mx[1]: mx[1] = v[1]
            if v[2] > mx[2]: mx[2] = v[2]
    return (mn[0], mn[1], mn[2], mx[0], mx[1], mx[2])


def _ml_coplanar_2d_sat(t1, t2, n):
    ax, ay, az = abs(n[0]), abs(n[1]), abs(n[2])
    if ax > ay and ax > az:
        i0, i1 = 1, 2
    elif ay > az:
        i0, i1 = 0, 2
    else:
        i0, i1 = 0, 1

    def proj(tri):
        return [(tri[0][i0], tri[0][i1]),
                (tri[1][i0], tri[1][i1]),
                (tri[2][i0], tri[2][i1])]

    def edges(p):
        return [(p[1][0]-p[0][0], p[1][1]-p[0][1]),
                (p[2][0]-p[1][0], p[2][1]-p[1][1]),
                (p[0][0]-p[2][0], p[0][1]-p[2][1])]

    p1 = proj(t1); p2 = proj(t2)
    for axis_list in (edges(p1), edges(p2)):
        for e in axis_list:
            ax2 = (-e[1], e[0])
            mn1 = mx1 = p1[0][0]*ax2[0] + p1[0][1]*ax2[1]
            for v in p1[1:]:
                d = v[0]*ax2[0] + v[1]*ax2[1]
                if d < mn1: mn1 = d
                if d > mx1: mx1 = d
            mn2 = mx2 = p2[0][0]*ax2[0] + p2[0][1]*ax2[1]
            for v in p2[1:]:
                d = v[0]*ax2[0] + v[1]*ax2[1]
                if d < mn2: mn2 = d
                if d > mx2: mx2 = d
            if mx1 < mn2 - _ML_EPS or mx2 < mn1 - _ML_EPS:
                return False
    return True


def _ml_compute_interval_3d(verts, dists, Dn):
    pts = []
    for i in range(3):
        a = i
        b = (i + 1) % 3
        if dists[a] * dists[b] < 0:
            t = dists[a] / (dists[a] - dists[b])
            pts.append((verts[a][0] + (verts[b][0]-verts[a][0])*t,
                        verts[a][1] + (verts[b][1]-verts[a][1])*t,
                        verts[a][2] + (verts[b][2]-verts[a][2])*t))
        if abs(dists[a]) < _ML_EPS:
            pts.append(verts[a])
    if not pts:
        return None
    ds = [_ml_dot(p, Dn) for p in pts]
    return (min(ds), max(ds))


def _ml_tri_tri_intersect(t1, t2):
    e1 = _ml_sub(t1[1], t1[0])
    e2 = _ml_sub(t1[2], t1[0])
    n1 = _ml_cross(e1, e2)
    d1 = -_ml_dot(n1, t1[0])
    d2_ = [_ml_dot(n1, v) + d1 for v in t2]
    if all(d > _ML_EPS for d in d2_) or all(d < -_ML_EPS for d in d2_):
        return False

    f1 = _ml_sub(t2[1], t2[0])
    f2 = _ml_sub(t2[2], t2[0])
    n2 = _ml_cross(f1, f2)
    d2 = -_ml_dot(n2, t2[0])
    d1_ = [_ml_dot(n2, v) + d2 for v in t1]
    if all(d > _ML_EPS for d in d1_) or all(d < -_ML_EPS for d in d1_):
        return False

    D = _ml_cross(n1, n2)
    if _ml_veclen(D) < _ML_EPS:
        return _ml_coplanar_2d_sat(t1, t2, n1)

    Dn = _ml_vecnorm(D)
    i1 = _ml_compute_interval_3d(t1, d1_, Dn)
    i2 = _ml_compute_interval_3d(t2, d2_, Dn)
    if i1 is None or i2 is None:
        return False
    if i1[1] < i2[0] - _ML_EPS or i2[1] < i1[0] - _ML_EPS:
        return False
    return True


def _ml_meshes_intersect(tris_a, tris_b, aabb_a, aabb_b):
    if not _ml_aabb_overlap(aabb_a, aabb_b):
        return False
    sub_a = []
    sub_b = []
    for t in tris_a:
        ab = _ml_tri_aabb(t)
        if _ml_aabb_overlap(ab, aabb_b):
            sub_a.append((t, ab))
    for t in tris_b:
        ab = _ml_tri_aabb(t)
        if _ml_aabb_overlap(ab, aabb_a):
            sub_b.append((t, ab))
    for ta, aa in sub_a:
        for tb, bb in sub_b:
            if not _ml_aabb_overlap(aa, bb):
                continue
            if _ml_tri_tri_intersect(ta, tb):
                return True
    return False


# ---------------------------------------------------------------------------
# Mesh data helpers
# ---------------------------------------------------------------------------

def _ml_mesh_to_triangles(mesh_shape):
    try:
        sel = om.MSelectionList()
        sel.add(mesh_shape)
        dag = om.MDagPath()
        sel.getDagPath(0, dag)
        try:
            dag.extendToShape()
        except Exception:
            pass
        fn = om.MFnMesh(dag)
        pts = om.MPointArray()
        fn.getPoints(pts, om.MSpace.kWorld)
        tri_counts = om.MIntArray()
        tri_verts = om.MIntArray()
        fn.getTriangles(tri_counts, tri_verts)
        triangles = []
        idx = 0
        for pi in range(fn.numPolygons()):
            n_tris = tri_counts[pi]
            for _ in range(n_tris):
                i0 = tri_verts[idx]; idx += 1
                i1 = tri_verts[idx]; idx += 1
                i2 = tri_verts[idx]; idx += 1
                p0 = pts[i0]; p1 = pts[i1]; p2 = pts[i2]
                triangles.append((
                    (p0.x, p0.y, p0.z),
                    (p1.x, p1.y, p1.z),
                    (p2.x, p2.y, p2.z),
                ))
        return triangles
    except Exception:
        return []


def _ml_mesh_to_triangles_with_ids(mesh_shape):
    """Same as _ml_mesh_to_triangles but also returns per-triangle vert IDs.

    Returns (triangles, vert_ids) where
        triangles[i] = ((x,y,z), (x,y,z), (x,y,z))
        vert_ids[i]  = (v0, v1, v2)  -- indices into the mesh's vertex list
    """
    try:
        sel = om.MSelectionList()
        sel.add(mesh_shape)
        dag = om.MDagPath()
        sel.getDagPath(0, dag)
        try:
            dag.extendToShape()
        except Exception:
            pass
        fn = om.MFnMesh(dag)
        pts = om.MPointArray()
        fn.getPoints(pts, om.MSpace.kWorld)
        tri_counts = om.MIntArray()
        tri_verts = om.MIntArray()
        fn.getTriangles(tri_counts, tri_verts)
        triangles = []
        vert_ids = []
        idx = 0
        for pi in range(fn.numPolygons()):
            n_tris = tri_counts[pi]
            for _ in range(n_tris):
                i0 = tri_verts[idx]; idx += 1
                i1 = tri_verts[idx]; idx += 1
                i2 = tri_verts[idx]; idx += 1
                p0 = pts[i0]; p1 = pts[i1]; p2 = pts[i2]
                triangles.append((
                    (p0.x, p0.y, p0.z),
                    (p1.x, p1.y, p1.z),
                    (p2.x, p2.y, p2.z),
                ))
                vert_ids.append((i0, i1, i2))
        return triangles, vert_ids
    except Exception:
        return [], []


def _ml_translate_triangles(triangles, delta):
    dx, dy, dz = delta
    out = []
    for t in triangles:
        out.append((
            (t[0][0]+dx, t[0][1]+dy, t[0][2]+dz),
            (t[1][0]+dx, t[1][1]+dy, t[1][2]+dz),
            (t[2][0]+dx, t[2][1]+dy, t[2][2]+dz),
        ))
    return out


def _ml_translate_aabb(aabb, delta):
    dx, dy, dz = delta
    return (aabb[0]+dx, aabb[1]+dy, aabb[2]+dz,
            aabb[3]+dx, aabb[4]+dy, aabb[5]+dz)


def _ml_get_mesh_shapes(objects):
    """Collect mesh shapes from a list of nodes (transforms, groups, or meshes).

    Recurses through transform hierarchies so selecting a group returns every
    mesh underneath it. Intermediate objects (deformer orig shapes) are skipped.

    Note: Maya's `cmds.listRelatives(..., allDescendents=True, type="mesh")`
    is unreliable because the `type` filter is applied to intermediate
    transform nodes too, which can prune the traversal. We instead collect
    all descendants and filter by node type in Python.
    """
    shapes = []
    for obj in objects:
        if not cmds.objExists(obj):
            continue
        node_type = cmds.nodeType(obj)
        if node_type == "mesh":
            # Direct mesh-shape selection
            try:
                if cmds.getAttr(obj + ".intermediateObject"):
                    continue
            except Exception:
                pass
            full = cmds.ls(obj, long=True)
            if full:
                shapes.append(full[0])
            continue

        # Transform / group: enumerate the entire subtree and pull out
        # mesh shapes. Separate calls for descendants and direct shapes;
        # `listRelatives(allDescendents=True)` alone doesn't include
        # shapes parented directly to the top node.
        collected = set()

        # 1. All transforms + shapes under this node
        all_descendants = cmds.listRelatives(
            obj,
            allDescendents=True,
            fullPath=True) or []

        # 2. Direct shape children (catches the common case where the
        #    node itself is a transform with a mesh shape).
        direct_shapes = cmds.listRelatives(
            obj,
            shapes=True,
            fullPath=True) or []

        for node in list(all_descendants) + list(direct_shapes):
            if node in collected:
                continue
            collected.add(node)
            try:
                if cmds.nodeType(node) != "mesh":
                    continue
            except Exception:
                continue
            try:
                if cmds.getAttr(node + ".intermediateObject"):
                    continue
            except Exception:
                pass
            shapes.append(node)

    # preserve uniqueness without losing order
    seen = set()
    out = []
    for s in shapes:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _ml_get_world_verts(mesh_shape):
    try:
        sel = om.MSelectionList()
        sel.add(mesh_shape)
        dag = om.MDagPath()
        sel.getDagPath(0, dag)
        try:
            dag.extendToShape()
        except Exception:
            pass
        fn = om.MFnMesh(dag)
        pts = om.MPointArray()
        fn.getPoints(pts, om.MSpace.kWorld)
        out = []
        for i in range(pts.length()):
            p = pts[i]
            out.append((p.x, p.y, p.z))
        return out
    except Exception:
        return []


def _ml_get_selected_vert_positions(mesh_shape, vert_indices):
    out = []
    for vi in vert_indices:
        try:
            p = cmds.xform(u"{0}.vtx[{1}]".format(mesh_shape, vi),
                           q=True, ws=True, t=True)
            out.append((p[0], p[1], p[2]))
        except Exception:
            pass
    return out


# ---------------------------------------------------------------------------
# Landing core (raycast + binary-search fallback)
# ---------------------------------------------------------------------------

_ML_AXIS_NAMES = ["X", "Y", "Z"]


def _ml_bbox_gap_estimate(source_pts, target_shapes, axis, sign):
    """Estimate gap between source points and target BBox along an axis.

    `source_pts` is a pre-collected list of (x,y,z) positions — pass only
    the selected-vertex positions in component mode so the bbox is
    tight.
    """
    if not source_pts:
        return None
    tgt_pts = []
    for s in target_shapes:
        tgt_pts.extend(_ml_get_world_verts(s))
    if not tgt_pts:
        return None
    src_vals = [p[axis] for p in source_pts]
    tgt_vals = [p[axis] for p in tgt_pts]
    if sign > 0:
        gap = min(tgt_vals) - max(src_vals)
    else:
        gap = min(src_vals) - max(tgt_vals)
    if gap < 0:
        return 0.0
    return gap


def ml_compute_landing(source_shapes, target_shapes, axis, sign, offset,
                       vert_indices=None, debug=False):
    """Compute landing delta. Returns (distance, sign) or (None, 0).

    If `vert_indices` is given (component mode), ONLY the selected
    vertices participate. Source shapes that have no entry in
    `vert_indices` are ignored completely — they won't be moved and
    won't contribute to raycast, bounding-box, or triangle data.
    """
    is_component_mode = vert_indices is not None

    # Normalize: in component mode drop shapes that have no entries or
    # only empty lists, so downstream "shape in vert_indices" is reliable.
    if is_component_mode:
        vert_indices = {s: v for s, v in vert_indices.items() if v}

    if debug:
        print(u"[DW MeshLanding] ----- compute_landing -----")
        print(u"  source_shapes:", source_shapes)
        print(u"  target_shapes:", target_shapes)
        print(u"  axis={0} sign_in={1} offset={2}".format(
            axis, sign, offset))
        print(u"  component_mode:", is_component_mode)
        if is_component_mode:
            for s, vs in vert_indices.items():
                print(u"    {0}: {1} verts".format(
                    s.split(u"|")[-1], len(vs)))

    all_pts = []
    for shape in source_shapes:
        if is_component_mode:
            if shape not in vert_indices:
                continue  # this shape has no selected verts → skip
            pts = _ml_get_selected_vert_positions(shape, vert_indices[shape])
        else:
            pts = _ml_get_world_verts(shape)
        all_pts.extend(pts)

    if not all_pts:
        if debug:
            print(u"  [FAIL] no source points collected")
        return None, 0

    if debug:
        print(u"  collected {0} source pts (incl. virtual)"
              .format(len(all_pts)))

    if sign == 0:
        src_cx = sum(p[axis] for p in all_pts) / len(all_pts)
        tgt_pts = []
        for s in target_shapes:
            tgt_pts.extend(_ml_get_world_verts(s))
        if tgt_pts:
            tgt_cx = sum(p[axis] for p in tgt_pts) / len(tgt_pts)
            sign = -1 if src_cx > tgt_cx else 1
            if debug:
                print(u"  auto-sign: src_cx={0:.3f} tgt_cx={1:.3f} "
                      u"-> sign={2}".format(src_cx, tgt_cx, sign))
        else:
            sign = -1

    direction = [0.0, 0.0, 0.0]
    direction[axis] = float(sign)
    direction = tuple(direction)

    raycaster = MeshLandingRaycaster(target_shapes)
    ray_min_dist = None
    ray_hits = 0
    first_pt_info = None
    # For the first 3 points, also cast with debug on to see what's happening.
    for idx, p in enumerate(all_pts):
        cast_debug = bool(debug) and idx < 3
        d = raycaster.cast(p, direction, debug=cast_debug)
        if first_pt_info is None:
            first_pt_info = (p, d)
        if d is not None:
            ray_hits += 1
            if ray_min_dist is None or d < ray_min_dist:
                ray_min_dist = d
    if debug:
        print(u"  raycast: {0}/{1} hits, min_dist={2}".format(
            ray_hits, len(all_pts), ray_min_dist))
        if first_pt_info is not None:
            pt, d = first_pt_info
            print(u"  first source pt={0} direction={1} hit_dist={2}".format(
                pt, direction, d))
        if ray_min_dist is not None:
            sample = all_pts[0]
            expected_hit = (sample[0] + direction[0] * ray_min_dist,
                            sample[1] + direction[1] * ray_min_dist,
                            sample[2] + direction[2] * ray_min_dist)
            print(u"  sample hit predicted at: {0}".format(expected_hit))
    if ray_min_dist is None:
        # Rays missed every triangle of Mesh B. Fall back to the world
        # origin plane (Y=0 for Y-axis, etc.). This matches the user's
        # intuition that "when there's nothing underneath, drop to the
        # floor" where the floor is the world origin plane.
        src_vals = [p[axis] for p in all_pts]
        if sign < 0:
            # Moving in the negative direction: distance from min src
            # to the origin plane (0).
            ray_min_dist = min(src_vals) - 0.0
        else:
            # Moving in the positive direction: distance from origin
            # up to max src.
            ray_min_dist = 0.0 - max(src_vals)
        if debug:
            print(u"  [ray-miss fallback: drop to world origin plane] "
                  u"ray_min_dist={0}".format(ray_min_dist))
        if ray_min_dist is None or ray_min_dist <= 0.0:
            # Already past the origin plane → nothing to do.
            if debug:
                print(u"  [FAIL] already past origin plane")
            return None, 0

    # ----- Build list of triangles that will actually move ---------------
    # Object mode:     all triangles from every source mesh.
    # Component mode:  ONLY triangles where all 3 vertices are in the
    #                  user's selection. Shapes with no entries in
    #                  vert_indices are entirely excluded (they won't
    #                  move, so they must not constrain the motion).
    # Additionally, any caller-provided virtual triangles (built from
    # sparse vertex / edge selections) participate in the collision
    # check as if they were real geometry.
    src_moving_tris = []
    for shape in source_shapes:
        if is_component_mode:
            if shape not in vert_indices:
                continue
            tris, vids = _ml_mesh_to_triangles_with_ids(shape)
            moving = set(vert_indices[shape])
            for t, vid in zip(tris, vids):
                if (vid[0] in moving and vid[1] in moving
                        and vid[2] in moving):
                    src_moving_tris.append(t)
        else:
            tris = _ml_mesh_to_triangles(shape)
            src_moving_tris.extend(tris)

    tgt_tris = []
    for shape in target_shapes:
        tgt_tris.extend(_ml_mesh_to_triangles(shape))

    if debug:
        print(u"  moving_tris={0}  tgt_tris={1}"
              .format(len(src_moving_tris), len(tgt_tris)))

    # If there are no fully-selected triangles (user picked disconnected
    # vertices), fall back to raycast-only — rays already gave us a
    # vertex-level safe distance.
    if not src_moving_tris or not tgt_tris:
        if offset >= 0:
            result = ray_min_dist - offset
            if result < 0.0:
                result = 0.0
        else:
            # Negative offset: embed by |offset| past the raycast hit.
            result = ray_min_dist + abs(offset)
        if debug:
            print(u"  [raycast-only] result={0}".format(result))
        return result, sign

    # Precompute AABBs from the moving-triangle subset ONLY. This is key:
    # the AABB must not include geometry that won't translate, otherwise
    # broad-phase collision rejection (and the narrow-phase intersection
    # test that follows) is polluted by static geometry.
    src_aabb_static = _ml_aabb_merge_tris(src_moving_tris)
    tgt_aabb = _ml_aabb_merge_tris(tgt_tris)
    if debug:
        print(u"  src_aabb: ({0:.3f},{1:.3f},{2:.3f})-({3:.3f},{4:.3f},{5:.3f})"
              .format(*src_aabb_static))
        print(u"  tgt_aabb: ({0:.3f},{1:.3f},{2:.3f})-({3:.3f},{4:.3f},{5:.3f})"
              .format(*tgt_aabb))

    def _collides_at(dist):
        dlist = [0.0, 0.0, 0.0]
        dlist[axis] = dist * sign
        delta = tuple(dlist)
        moved_aabb = _ml_translate_aabb(src_aabb_static, delta)
        if not _ml_aabb_overlap(moved_aabb, tgt_aabb):
            return False
        moved_tris = _ml_translate_triangles(src_moving_tris, delta)
        return _ml_meshes_intersect(moved_tris, tgt_tris,
                                     moved_aabb, tgt_aabb)

    # ----- Resolve final distance -----
    if offset < 0:
        # Negative offset: embed past the raycast hit. No collision
        # check (we WANT Mesh A to go into Mesh B).
        if debug:
            print(u"  [negative offset] result={0}".format(
                ray_min_dist + abs(offset)))
        return ray_min_dist + abs(offset), sign

    # If Mesh A (selected subset) and Mesh B have no overlap along the
    # OTHER two axes (i.e. they aren't over each other from above), the
    # raycast dist is the true answer and we must NOT run binary search
    # — otherwise small AABB touches produce false positives that stop
    # motion early.
    def _axes_transverse_overlap():
        """Return True if src and tgt AABBs overlap on the two axes
        perpendicular to the move axis."""
        other = [i for i in (0, 1, 2) if i != axis]
        for i in other:
            a_min, a_max = src_aabb_static[i], src_aabb_static[i + 3]
            b_min, b_max = tgt_aabb[i], tgt_aabb[i + 3]
            if a_max < b_min or b_max < a_min:
                return False
        return True

    if not _axes_transverse_overlap():
        # No footprint overlap → the triangles can never physically
        # intersect no matter how far along `axis` we move. Trust the
        # raycast result (which already accounts for direction).
        result = ray_min_dist - offset
        if result < 0.0:
            result = 0.0
        if debug:
            print(u"  [no transverse overlap] result={0}".format(result))
        return result, sign

    # Non-negative offset: find the max non-colliding distance, then
    # subtract the offset to leave a gap.
    collides_at_ray = _collides_at(ray_min_dist)
    if debug:
        print(u"  collides_at(ray_min_dist={0}) = {1}".format(
            ray_min_dist, collides_at_ray))
    if not collides_at_ray:
        result = ray_min_dist - offset
        if result < 0.0:
            result = 0.0
        if debug:
            print(u"  [no collision at raycast] result={0}".format(result))
        return result, sign

    lo = 0.0
    hi = ray_min_dist
    best = 0.0
    _MAX_ITER = 20
    _TOL = 1.0e-4
    for _it in range(_MAX_ITER):
        mid = (lo + hi) * 0.5
        if _collides_at(mid):
            hi = mid
        else:
            best = mid
            lo = mid
        if (hi - lo) < _TOL:
            break

    final_d = best - offset
    if final_d < 0.0:
        final_d = 0.0
    if debug:
        print(u"  [binary-search] best={0} final_d={1}".format(best, final_d))
    return final_d, sign


# ---------------------------------------------------------------------------
# Mesh Landing: tab-side launcher group
# ---------------------------------------------------------------------------

def _build_mesh_landing_group(tool_window, parent_layout):
    """Compact launcher. Matches the header+desc+launch layout of the
    Vertex Snap and Edge Width Alignment groups so all three buttons
    sit at the same horizontal position."""
    grp = QtWidgets.QGroupBox()
    grp.setStyleSheet(
        "QGroupBox{border:1px solid #4CAF50;border-radius:6px;"
        "background-color:#2E2E2E;margin-top:6px}"
        "QGroupBox::title{subcontrol-origin:margin;left:10px;"
        "color:#EEE;font-size:11px;font-weight:bold}")
    glo = QtWidgets.QVBoxLayout(grp)
    glo.setContentsMargins(6, 10, 6, 6)
    glo.setSpacing(4)

    # Header row: title + launch button (launch aligned to right,
    # matching the Vertex Snap and Edge Width Alignment groups).
    hdr = QtWidgets.QHBoxLayout()
    tool_window._ml_grp_lbl = QtWidgets.QLabel(u"\u25A0 " + tr("ml_grp_title"))
    tool_window._ml_grp_lbl.setStyleSheet(
        "color:#4CAF50;font-size:11px;font-weight:bold")
    hdr.addWidget(tool_window._ml_grp_lbl)
    hdr.addStretch()
    tool_window._ml_btn_launch = _mkbtn(tr("ml_btn_launch"), 24,
                                         "#4CAF50", "#388E3C", fs=10)
    tool_window._ml_btn_launch.clicked.connect(
        lambda: _ml_launch(tool_window))
    hdr.addWidget(tool_window._ml_btn_launch)
    glo.addLayout(hdr)

    tool_window._ml_desc_lbl = QtWidgets.QLabel(tr("ml_grp_desc"))
    tool_window._ml_desc_lbl.setStyleSheet(
        "color:#AAA;font-size:10px;padding:2px 4px")
    tool_window._ml_desc_lbl.setWordWrap(True)
    glo.addWidget(tool_window._ml_desc_lbl)

    # State — initialised on launch
    tool_window._ml_result_window = None

    parent_layout.addWidget(grp)
    return grp


def _ml_launch(tool_window):
    """Open / refocus the Mesh Landing dialog."""
    if getattr(tool_window, "_ml_result_window", None) is None:
        tool_window._ml_result_window = MeshLandingDialog(parent=tool_window)
        tool_window._ml_result_window.status_msg.connect(
            lambda t: _ml_set_status(tool_window, t))
    tool_window._ml_result_window.show()
    tool_window._ml_result_window.raise_()
    tool_window._ml_result_window.activateWindow()


def _ml_set_status(tool_window, text):
    if hasattr(tool_window, "_status_bar"):
        tool_window._status_bar.setText(text)


def _ml_refresh_labels(tool_window):
    """Called from CollisionCheckToolWindow._refresh_labels()."""
    if hasattr(tool_window, "_ml_grp_lbl"):
        tool_window._ml_grp_lbl.setText(u"\u25A0 " + tr("ml_grp_title"))
    if hasattr(tool_window, "_ml_desc_lbl"):
        tool_window._ml_desc_lbl.setText(tr("ml_grp_desc"))
    if hasattr(tool_window, "_ml_btn_launch"):
        tool_window._ml_btn_launch.setText(tr("ml_btn_launch"))
    w = getattr(tool_window, "_ml_result_window", None)
    if w is not None:
        w.refresh_labels()


# ---------------------------------------------------------------------------
# Mesh Landing Dialog — preview + confirm/revert workflow
# ---------------------------------------------------------------------------

class MeshLandingDialog(QtWidgets.QDialog):
    """Dialog with A/B mesh picker, live preview, and confirm/revert.

    Workflow:
      1. Pick Mesh A (mover) and Mesh B (ground). Swap button flips them.
      2. Adjust axis / direction / mode / offset.
      3. Click [Preview] to run landing within an undo chunk.
      4. Adjust settings and re-preview freely (previous preview is undone
         automatically before the new one is applied).
      5. Click [Confirm] to finalize, or [Revert] to cancel and restore."""

    status_msg = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(MeshLandingDialog, self).__init__(parent)
        self.setObjectName("DW_MeshLanding_Dialog")
        self.setWindowTitle(tr("ml_dlg_title"))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumSize(460, 360)
        self.setStyleSheet(
            "QDialog{background-color:#333;color:#EEE}"
            "QLabel{color:#EEE}")

        self._mesh_a_shapes = []
        self._mesh_b_shapes = []
        self._preview_active = False   # True when a preview is applied
        self._last_dist = 0.0
        self._last_axis = 1
        # Snapshot of Mesh A state BEFORE the current preview was applied.
        # Restoration writes absolute positions back, which is robust
        # against Ctrl+Z, manual edits, or any other state changes the
        # user may have performed while the dialog was open.
        self._snapshot = None    # {"is_component": bool,
                                 #  "object_positions": {node: (x,y,z)},
                                 #  "vert_positions": {shape: {vi: (x,y,z)}}}
        self._build()

    # -- UI construction --
    def _build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(10, 10, 10, 10)
        lo.setSpacing(6)

        _lbl_ss = "color:#AAA;font-size:10px"
        _field_ss = ("QLineEdit{background-color:#2B2B2B;color:#EEE;"
                     "border:1px solid #555;border-radius:3px;"
                     "padding:2px 4px;font-size:10px}")
        _spin_ss = ("QDoubleSpinBox{background-color:#2B2B2B;color:#EEE;"
                    "border:1px solid #555;border-radius:3px;"
                    "padding:1px;font-size:10px}")
        _set_btn_ss = ("QPushButton{background-color:#455A64;color:#EEE;"
                       "border:1px solid #607D8B;border-radius:3px;"
                       "font-size:10px;padding:2px 8px}"
                       "QPushButton:hover{background-color:#546E7A}")

        # ---- Mesh A row ----
        a_row = QtWidgets.QHBoxLayout()
        self._lbl_mesh_a = QtWidgets.QLabel(tr("ml_lbl_mesh_a"))
        self._lbl_mesh_a.setStyleSheet(
            "color:#8BC34A;font-size:10px;font-weight:bold")
        self._lbl_mesh_a.setFixedWidth(110)
        a_row.addWidget(self._lbl_mesh_a)
        self._txt_mesh_a = QtWidgets.QLineEdit()
        self._txt_mesh_a.setReadOnly(True)
        self._txt_mesh_a.setStyleSheet(_field_ss)
        a_row.addWidget(self._txt_mesh_a)
        self._btn_set_a = QtWidgets.QPushButton(tr("ml_btn_set"))
        self._btn_set_a.setStyleSheet(_set_btn_ss)
        self._btn_set_a.setFixedWidth(50)
        self._btn_set_a.clicked.connect(self._on_set_a)
        a_row.addWidget(self._btn_set_a)
        lo.addLayout(a_row)

        # ---- Mesh B row ----
        b_row = QtWidgets.QHBoxLayout()
        self._lbl_mesh_b = QtWidgets.QLabel(tr("ml_lbl_mesh_b"))
        self._lbl_mesh_b.setStyleSheet(
            "color:#81D4FA;font-size:10px;font-weight:bold")
        self._lbl_mesh_b.setFixedWidth(110)
        b_row.addWidget(self._lbl_mesh_b)
        self._txt_mesh_b = QtWidgets.QLineEdit()
        self._txt_mesh_b.setReadOnly(True)
        self._txt_mesh_b.setStyleSheet(_field_ss)
        b_row.addWidget(self._txt_mesh_b)
        self._btn_set_b = QtWidgets.QPushButton(tr("ml_btn_set"))
        self._btn_set_b.setStyleSheet(_set_btn_ss)
        self._btn_set_b.setFixedWidth(50)
        self._btn_set_b.clicked.connect(self._on_set_b)
        b_row.addWidget(self._btn_set_b)
        lo.addLayout(b_row)

        # ---- Swap A <-> B ----
        swap_row = QtWidgets.QHBoxLayout()
        swap_row.addStretch()
        self._btn_swap = QtWidgets.QPushButton(tr("ml_btn_swap"))
        self._btn_swap.setStyleSheet(
            "QPushButton{background-color:#607D8B;color:#EEE;border:none;"
            "border-radius:3px;font-size:10px;font-weight:bold;padding:4px 12px}"
            "QPushButton:hover{background-color:#78909C}")
        self._btn_swap.setFixedWidth(140)
        self._btn_swap.clicked.connect(self._on_swap)
        swap_row.addWidget(self._btn_swap)
        swap_row.addStretch()
        lo.addLayout(swap_row)

        # ---- Separator ----
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color:#555")
        lo.addWidget(sep)

        # ---- Axis row ----
        ax_row = QtWidgets.QHBoxLayout()
        self._lbl_axis = QtWidgets.QLabel(tr("ml_lbl_axis"))
        self._lbl_axis.setStyleSheet(_lbl_ss)
        self._lbl_axis.setFixedWidth(110)
        ax_row.addWidget(self._lbl_axis)
        self._rb_x = QtWidgets.QRadioButton("X")
        self._rb_y = QtWidgets.QRadioButton("Y")
        self._rb_z = QtWidgets.QRadioButton("Z")
        self._rb_y.setChecked(True)
        ax_grp = QtWidgets.QButtonGroup(self)
        for rb in (self._rb_x, self._rb_y, self._rb_z):
            rb.setStyleSheet("QRadioButton{color:#CCC;font-size:10px}")
            ax_grp.addButton(rb)
            ax_row.addWidget(rb)
        ax_row.addStretch()
        lo.addLayout(ax_row)

        # ---- Direction row ----
        dir_row = QtWidgets.QHBoxLayout()
        self._lbl_dir = QtWidgets.QLabel(tr("ml_lbl_direction"))
        self._lbl_dir.setStyleSheet(_lbl_ss)
        self._lbl_dir.setFixedWidth(110)
        dir_row.addWidget(self._lbl_dir)
        self._rb_auto = QtWidgets.QRadioButton(tr("ml_dir_auto"))
        self._rb_pos = QtWidgets.QRadioButton(tr("ml_dir_positive"))
        self._rb_neg = QtWidgets.QRadioButton(tr("ml_dir_negative"))
        self._rb_auto.setChecked(True)
        dir_grp = QtWidgets.QButtonGroup(self)
        for rb in (self._rb_auto, self._rb_pos, self._rb_neg):
            rb.setStyleSheet("QRadioButton{color:#CCC;font-size:10px}")
            dir_grp.addButton(rb)
            dir_row.addWidget(rb)
        dir_row.addStretch()
        lo.addLayout(dir_row)

        # ---- Mode row ----
        mode_row = QtWidgets.QHBoxLayout()
        self._lbl_mode = QtWidgets.QLabel(tr("ml_lbl_mode"))
        self._lbl_mode.setStyleSheet(_lbl_ss)
        self._lbl_mode.setFixedWidth(110)
        mode_row.addWidget(self._lbl_mode)
        self._rb_obj = QtWidgets.QRadioButton(tr("ml_mode_object"))
        self._rb_comp = QtWidgets.QRadioButton(tr("ml_mode_component"))
        self._rb_obj.setChecked(True)
        mode_grp = QtWidgets.QButtonGroup(self)
        for rb in (self._rb_obj, self._rb_comp):
            rb.setStyleSheet("QRadioButton{color:#CCC;font-size:10px}")
            mode_grp.addButton(rb)
            mode_row.addWidget(rb)
        mode_row.addStretch()
        lo.addLayout(mode_row)

        # ---- Offset row (spinbox + slider, negative allowed) ----
        off_row = QtWidgets.QHBoxLayout()
        self._lbl_offset = QtWidgets.QLabel(tr("ml_lbl_offset"))
        self._lbl_offset.setStyleSheet(_lbl_ss)
        self._lbl_offset.setFixedWidth(110)
        off_row.addWidget(self._lbl_offset)
        self._spin_offset = QtWidgets.QDoubleSpinBox()
        self._spin_offset.setRange(-1.0e6, 1.0e6)
        self._spin_offset.setDecimals(4)
        self._spin_offset.setSingleStep(0.001)
        self._spin_offset.setValue(0.0)
        self._spin_offset.setFixedWidth(85)
        self._spin_offset.setStyleSheet(_spin_ss)
        self._spin_offset.setToolTip(tr("ml_tip_offset"))
        off_row.addWidget(self._spin_offset)
        # Slider covers -1.0..+1.0 in 0.0001 steps (integer scale 10000).
        # For larger values the user can type directly into the spinbox.
        self._slider_offset = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._slider_offset.setRange(-10000, 10000)
        self._slider_offset.setValue(0)
        self._slider_offset.setStyleSheet(
            "QSlider::groove:horizontal{background:#2B2B2B;height:4px;"
            "border-radius:2px}"
            "QSlider::handle:horizontal{background:#4CAF50;width:12px;"
            "margin:-4px 0;border-radius:6px}"
            "QSlider::sub-page:horizontal,QSlider::add-page:horizontal{"
            "background:transparent}")
        self._slider_offset.setToolTip(tr("ml_tip_slider"))
        off_row.addWidget(self._slider_offset, 1)
        # Two-way sync (with blockSignals to avoid loops)
        self._spin_offset.valueChanged.connect(self._on_offset_spin_changed)
        self._slider_offset.valueChanged.connect(
            self._on_offset_slider_changed)
        lo.addLayout(off_row)

        # ---- Preview status ----
        self._lbl_preview_status = QtWidgets.QLabel(u"")
        self._lbl_preview_status.setStyleSheet(
            "color:#FFB74D;font-size:10px;font-weight:bold;padding:4px;"
            "background-color:#2B2B2B;border-radius:3px")
        self._lbl_preview_status.setWordWrap(True)
        self._lbl_preview_status.setVisible(False)
        lo.addWidget(self._lbl_preview_status)

        lo.addStretch()

        # ---- Preview button ----
        pv_row = QtWidgets.QHBoxLayout()
        pv_row.addStretch()
        self._btn_preview = _mkbtn(tr("ml_btn_preview"), 28,
                                    "#2196F3", "#1976D2")
        self._btn_preview.setFixedWidth(140)
        self._btn_preview.clicked.connect(self._on_preview)
        pv_row.addWidget(self._btn_preview)
        pv_row.addStretch()
        lo.addLayout(pv_row)

        # ---- Confirm / Revert / Close ----
        cr_row = QtWidgets.QHBoxLayout()
        self._btn_confirm = _mkbtn(tr("ml_btn_confirm"), 26,
                                    "#4CAF50", "#388E3C", fs=10)
        self._btn_confirm.clicked.connect(self._on_confirm)
        self._btn_confirm.setEnabled(False)
        cr_row.addWidget(self._btn_confirm)
        self._btn_revert = _mkbtn(tr("ml_btn_revert"), 26,
                                   "#F44336", "#D32F2F", fs=10)
        self._btn_revert.clicked.connect(self._on_revert)
        self._btn_revert.setEnabled(False)
        cr_row.addWidget(self._btn_revert)
        cr_row.addStretch()
        self._btn_close = _mkbtn(tr("btn_close"), 26, "#555", "#444", fs=10)
        self._btn_close.clicked.connect(self.close)
        cr_row.addWidget(self._btn_close)
        lo.addLayout(cr_row)

    # -- Mesh A/B picking --
    def _on_set_a(self):
        if not MAYA_AVAILABLE:
            return
        sel = cmds.ls(sl=True, long=True) or []
        shapes = _ml_get_mesh_shapes(sel)
        self._mesh_a_shapes = shapes
        self._txt_mesh_a.setText(self._short_names(shapes))

    def _on_set_b(self):
        if not MAYA_AVAILABLE:
            return
        sel = cmds.ls(sl=True, long=True) or []
        shapes = _ml_get_mesh_shapes(sel)
        self._mesh_b_shapes = shapes
        self._txt_mesh_b.setText(self._short_names(shapes))

    def _on_swap(self):
        self._mesh_a_shapes, self._mesh_b_shapes = \
            self._mesh_b_shapes, self._mesh_a_shapes
        self._txt_mesh_a.setText(self._short_names(self._mesh_a_shapes))
        self._txt_mesh_b.setText(self._short_names(self._mesh_b_shapes))
        self.status_msg.emit(tr("ml_status_swapped"))

    @staticmethod
    def _short_names(shapes):
        if not shapes:
            return u"---"
        # Show transform names (parent of the shape) — more meaningful than
        # "pCubeShape1" when the user selected "pCube1" or a group.
        names = []
        seen = set()
        for s in shapes:
            short = s.split("|")[-1]
            # Strip trailing "Shape" / "Shape1" / "ShapeOrig" if present
            if short.endswith("Shape"):
                short = short[:-5]
            elif "Shape" in short:
                # pCubeShape1 -> pCube1
                idx = short.rfind("Shape")
                short = short[:idx] + short[idx + 5:]
            if short and short not in seen:
                seen.add(short)
                names.append(short)
        if len(names) > 4:
            return u"{0}, {1}, ... ({2} meshes)".format(
                names[0], names[1], len(names))
        return u", ".join(names)

    # -- Settings readers --
    def _get_axis(self):
        if self._rb_x.isChecked():
            return 0
        if self._rb_z.isChecked():
            return 2
        return 1

    def _get_sign(self):
        if self._rb_pos.isChecked():
            return 1
        if self._rb_neg.isChecked():
            return -1
        return 0

    # -- Offset two-way sync (spinbox <-> slider) --
    def _on_offset_spin_changed(self, val):
        # Clamp to slider's integer range when syncing.
        iv = int(round(val * 10000.0))
        if iv > 10000:
            iv = 10000
        elif iv < -10000:
            iv = -10000
        self._slider_offset.blockSignals(True)
        try:
            self._slider_offset.setValue(iv)
        finally:
            self._slider_offset.blockSignals(False)

    def _on_offset_slider_changed(self, iv):
        val = iv / 10000.0
        self._spin_offset.blockSignals(True)
        try:
            self._spin_offset.setValue(val)
        finally:
            self._spin_offset.blockSignals(False)

    # -- Preview / Confirm / Revert --
    def _gather_components(self):
        """Analyze current selection and return candidate face sets.

        Returns a tuple (enclosed_map, adjacent_map, selection_items):
          * enclosed_map: dict {shape: [vi,...]} — faces fully enclosed
            by the selection (vertices, edges, or faces). This is the
            "strict" / precise answer the user drew.
          * adjacent_map: dict {shape: [vi,...]} — every face that
            touches any selected component. This is the wider fallback
            used when `enclosed_map` is empty.
          * face_items_map: dict {shape: [face_item_str, ...]} —
            the exact face components to re-select in Maya when the
            fallback is accepted by the user.

        Either map may be empty if the selection does not touch any
        Mesh A shape.
        """
        sel = cmds.ls(sl=True, fl=True, long=True) or []
        a_set = set(self._mesh_a_shapes)

        # Bucket the raw selection by shape and component type.
        per_shape = {}  # shape -> {"vtx": set, "e": set, "f": set}
        for item in sel:
            if u".vtx[" in item:
                sep, kind = u".vtx[", "vtx"
            elif u".e[" in item:
                sep, kind = u".e[", "e"
            elif u".f[" in item:
                sep, kind = u".f[", "f"
            else:
                continue
            shape_part = item.split(sep)[0]
            shapes = _ml_get_mesh_shapes([shape_part])
            if not shapes:
                continue
            shape = shapes[0]
            if shape not in a_set:
                continue
            try:
                idx = int(item.split(u"[")[-1].rstrip(u"]"))
            except Exception:
                continue
            bucket = per_shape.setdefault(
                shape, {"vtx": set(), "e": set(), "f": set()})
            bucket[kind].add(idx)

        enclosed_faces_per_shape = {}  # shape -> set of face indices
        adjacent_faces_per_shape = {}  # shape -> set of face indices

        for shape, buckets in per_shape.items():
            enclosed = set()
            adjacent = set()

            # Faces directly selected always qualify for both.
            enclosed.update(buckets["f"])
            adjacent.update(buckets["f"])

            # --- Vertex-side analysis ---
            if buckets["vtx"]:
                vtx_items = [u"{0}.vtx[{1}]".format(shape, vi)
                             for vi in buckets["vtx"]]
                try:
                    candidate_faces = cmds.polyListComponentConversion(
                        vtx_items, toFace=True) or []
                    candidate_faces = cmds.ls(candidate_faces, fl=True) or []
                except Exception:
                    candidate_faces = []
                sel_vset = buckets["vtx"]
                for f_item in candidate_faces:
                    try:
                        fi = int(f_item.split(u"[")[-1].rstrip(u"]"))
                    except Exception:
                        continue
                    # Adjacent: any face touched by any selected vertex.
                    adjacent.add(fi)
                    # Enclosed: face whose full vert set is inside sel.
                    try:
                        verts_of_f = cmds.polyListComponentConversion(
                            f_item, fromFace=True, toVertex=True) or []
                        verts_of_f = cmds.ls(verts_of_f, fl=True) or []
                    except Exception:
                        continue
                    f_vidxs = set()
                    for v in verts_of_f:
                        try:
                            f_vidxs.add(int(v.split(u"[")[-1].rstrip(u"]")))
                        except Exception:
                            pass
                    if f_vidxs and f_vidxs.issubset(sel_vset):
                        enclosed.add(fi)

            # --- Edge-side analysis ---
            if buckets["e"]:
                e_items = [u"{0}.e[{1}]".format(shape, ei)
                           for ei in buckets["e"]]
                try:
                    candidate_faces = cmds.polyListComponentConversion(
                        e_items, toFace=True) or []
                    candidate_faces = cmds.ls(candidate_faces, fl=True) or []
                except Exception:
                    candidate_faces = []
                sel_eset = buckets["e"]
                for f_item in candidate_faces:
                    try:
                        fi = int(f_item.split(u"[")[-1].rstrip(u"]"))
                    except Exception:
                        continue
                    adjacent.add(fi)
                    try:
                        edges_of_f = cmds.polyListComponentConversion(
                            f_item, fromFace=True, toEdge=True) or []
                        edges_of_f = cmds.ls(edges_of_f, fl=True) or []
                    except Exception:
                        continue
                    f_eidxs = set()
                    for e in edges_of_f:
                        try:
                            f_eidxs.add(int(e.split(u"[")[-1].rstrip(u"]")))
                        except Exception:
                            pass
                    if f_eidxs and f_eidxs.issubset(sel_eset):
                        enclosed.add(fi)

            if enclosed:
                enclosed_faces_per_shape[shape] = enclosed
            if adjacent:
                adjacent_faces_per_shape[shape] = adjacent

        def _faces_to_vert_map(faces_per_shape):
            out = {}
            for shape, faces in faces_per_shape.items():
                if not faces:
                    continue
                face_items = [u"{0}.f[{1}]".format(shape, fi)
                              for fi in faces]
                try:
                    verts = cmds.polyListComponentConversion(
                        face_items, fromFace=True, toVertex=True) or []
                    verts = cmds.ls(verts, fl=True) or []
                except Exception:
                    verts = []
                idxs = []
                for v in verts:
                    try:
                        idxs.append(int(v.split(u"[")[-1].rstrip(u"]")))
                    except Exception:
                        pass
                if idxs:
                    out[shape] = list(set(idxs))
            return out

        def _faces_to_items(faces_per_shape):
            out = {}
            for shape, faces in faces_per_shape.items():
                out[shape] = [u"{0}.f[{1}]".format(shape, fi)
                              for fi in sorted(faces)]
            return out

        enclosed_map = _faces_to_vert_map(enclosed_faces_per_shape)
        adjacent_map = _faces_to_vert_map(adjacent_faces_per_shape)
        face_items_map = _faces_to_items(adjacent_faces_per_shape)
        return enclosed_map, adjacent_map, face_items_map

    @staticmethod
    def _split_into_islands(vert_map):
        """Split a {shape: [vert_idx,...]} map into disconnected islands.

        Two vertices belong to the same island if a chain of shared-edge
        connections links them. Each island is returned as its own
        {shape: [vert_idx,...]} dict, so it can be fed directly into
        ml_compute_landing as a separate landing problem.

        Vertices from different shapes are always in different islands
        (we never bridge across objects).
        """
        islands = []
        for shape, vidxs in vert_map.items():
            if not vidxs:
                continue
            vset = set(vidxs)

            # Build adjacency: v -> set of neighboring selected verts,
            # via edges that connect two selected verts.
            adj = {v: set() for v in vset}
            try:
                vtx_items = [u"{0}.vtx[{1}]".format(shape, vi)
                             for vi in vset]
                edges = cmds.polyListComponentConversion(
                    vtx_items, toEdge=True) or []
                edges = cmds.ls(edges, fl=True) or []
            except Exception:
                edges = []
            for e in edges:
                try:
                    verts = cmds.polyListComponentConversion(
                        e, fromEdge=True, toVertex=True) or []
                    verts = cmds.ls(verts, fl=True) or []
                    pair = []
                    for v in verts:
                        try:
                            pair.append(int(v.split(u"[")[-1].rstrip(u"]")))
                        except Exception:
                            pass
                    if len(pair) == 2 and pair[0] in vset and pair[1] in vset:
                        adj[pair[0]].add(pair[1])
                        adj[pair[1]].add(pair[0])
                except Exception:
                    continue

            # BFS/DFS to find connected components.
            visited = set()
            for start in vset:
                if start in visited:
                    continue
                stack = [start]
                comp = []
                while stack:
                    v = stack.pop()
                    if v in visited:
                        continue
                    visited.add(v)
                    comp.append(v)
                    for n in adj.get(v, ()):
                        if n not in visited:
                            stack.append(n)
                islands.append({shape: comp})

        # Edge-case: no islands were produced (vert_map was empty).
        if not islands and vert_map:
            islands.append(dict(vert_map))
        return islands

    def _on_preview(self):
        if not MAYA_AVAILABLE:
            return
        if not self._mesh_a_shapes:
            self.status_msg.emit(tr("ml_status_no_a"))
            return
        if not self._mesh_b_shapes:
            self.status_msg.emit(tr("ml_status_no_b"))
            return

        # If a previous preview exists, restore its snapshot first so
        # we start the new calculation from a clean, known state. This
        # works correctly even if the user pressed Ctrl+Z, moved things
        # manually, or otherwise altered the scene between previews.
        if self._preview_active:
            self._restore_snapshot()

        axis = self._get_axis()
        sign = self._get_sign()
        offset = self._spin_offset.value()
        is_component = self._rb_comp.isChecked()

        vert_map = None
        if is_component:
            enclosed_map, adjacent_map, face_items_map = \
                self._gather_components()
            if enclosed_map:
                # Selection fully encloses at least one face → use as-is.
                vert_map = enclosed_map
            elif adjacent_map:
                # Nothing enclosed, but the selection touches some faces.
                # Ask the user whether to proceed with the expanded set.
                total_faces = sum(len(v) for v in face_items_map.values())
                total_verts = sum(len(v) for v in adjacent_map.values())
                msg_body = tr("ml_confirm_expand_body",
                              n_faces=total_faces, n_verts=total_verts)
                reply = QtWidgets.QMessageBox.question(
                    self,
                    tr("ml_confirm_expand_title"),
                    msg_body,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No)
                if reply != QtWidgets.QMessageBox.Yes:
                    self.status_msg.emit(tr("ml_status_cancelled"))
                    return
                # Switch Maya's selection to the expanded face set so
                # the user can visually confirm what moved after the
                # preview.
                expanded_items = []
                for shape, items in face_items_map.items():
                    expanded_items.extend(items)
                if expanded_items:
                    try:
                        cmds.select(expanded_items, r=True)
                    except Exception:
                        pass
                vert_map = adjacent_map
            else:
                # Nothing usable at all.
                self.status_msg.emit(tr("ml_status_no_enclosed"))
                self._set_preview_label(tr("ml_status_no_enclosed"),
                                        warn=True)
                return

        # Wrap the preview in a single undo chunk so Ctrl+Z collapses it.
        cmds.undoInfo(openChunk=True, chunkName="DW_MeshLanding_Preview")
        try:
            # Take the snapshot of Mesh A's state BEFORE we move anything.
            self._snapshot = self._capture_snapshot(is_component, vert_map)

            if is_component:
                # Split selected verts into connected islands so each
                # disjoint group lands independently.
                islands = self._split_into_islands(vert_map)
                any_hit = False
                max_dist = 0.0
                actual_sign_report = 0
                fail_count = 0
                for island_vert_map in islands:
                    result = ml_compute_landing(
                        self._mesh_a_shapes, self._mesh_b_shapes,
                        axis, sign, offset,
                        vert_indices=island_vert_map)
                    if result is None or result[0] is None \
                            or result[0] < 1.0e-8:
                        fail_count += 1
                        continue
                    d, actual_sign = result
                    delta = [0.0, 0.0, 0.0]
                    delta[axis] = d * actual_sign
                    for shape, vidxs in island_vert_map.items():
                        comps = [u"{0}.vtx[{1}]".format(shape, vi)
                                 for vi in vidxs]
                        if comps:
                            cmds.xform(comps, ws=True, r=True,
                                       t=(delta[0], delta[1], delta[2]))
                    any_hit = True
                    if d > max_dist:
                        max_dist = d
                        actual_sign_report = actual_sign
                if not any_hit:
                    self.status_msg.emit(tr("ml_status_no_hit"))
                    self._set_preview_label(tr("ml_status_no_hit"),
                                            warn=True)
                    self._snapshot = None
                    return
                dist = max_dist
                actual_sign = actual_sign_report
            else:
                # Object mode: each source shape lands independently so
                # disconnected meshes (e.g. pCube1 far away from pCube2)
                # each find their own collision distance with Mesh B.
                any_hit = False
                max_dist = 0.0
                fail_shapes = []
                for shape in self._mesh_a_shapes:
                    result = ml_compute_landing(
                        [shape], self._mesh_b_shapes,
                        axis, sign, offset)
                    if result is None or result[0] is None \
                            or result[0] < 1.0e-8:
                        fail_shapes.append(shape)
                        continue
                    d, actual_sign = result
                    delta = [0.0, 0.0, 0.0]
                    delta[axis] = d * actual_sign
                    tr_node = cmds.listRelatives(shape, parent=True,
                                                  fullPath=True)
                    if tr_node:
                        cmds.xform(tr_node[0], ws=True, r=True,
                                   t=(delta[0], delta[1], delta[2]))
                    any_hit = True
                    if d > max_dist:
                        max_dist = d
                        # Keep the sign from the last successful landing
                        # for status reporting.
                        actual_sign_report = actual_sign
                if not any_hit:
                    self.status_msg.emit(tr("ml_status_no_hit"))
                    self._set_preview_label(tr("ml_status_no_hit"),
                                            warn=True)
                    self._snapshot = None
                    return
                dist = max_dist   # representative distance for the status
                actual_sign = actual_sign_report

            self._preview_active = True
            self._last_dist = dist
            self._last_axis = axis
            msg = tr("ml_status_preview",
                     dist=u"{0:.4f}".format(dist),
                     axis=_ML_AXIS_NAMES[axis])
            self.status_msg.emit(msg)
            self._set_preview_label(msg, warn=False)
            self._btn_confirm.setEnabled(True)
            self._btn_revert.setEnabled(True)
        except Exception as _e:
            import traceback
            traceback.print_exc()
            self.status_msg.emit(u"Error: {0}".format(_e))
            self._set_preview_label(u"Error: {0}".format(_e), warn=True)
        finally:
            cmds.undoInfo(closeChunk=True)

    # -- Snapshot helpers --
    def _capture_snapshot(self, is_component, vert_map):
        """Capture Mesh A's current state so we can restore it later."""
        snap = {
            "is_component": is_component,
            "object_positions": {},   # transform_node -> (tx, ty, tz)
            "vert_positions": {},     # shape -> {vi: (x, y, z)}
        }
        if is_component and vert_map:
            for shape, vidxs in vert_map.items():
                if not cmds.objExists(shape):
                    continue
                pos_map = {}
                for vi in vidxs:
                    try:
                        p = cmds.xform(
                            u"{0}.vtx[{1}]".format(shape, vi),
                            q=True, ws=True, t=True)
                        pos_map[vi] = (p[0], p[1], p[2])
                    except Exception:
                        pass
                if pos_map:
                    snap["vert_positions"][shape] = pos_map
        else:
            for shape in self._mesh_a_shapes:
                tr_node = cmds.listRelatives(shape, parent=True,
                                              fullPath=True)
                if not tr_node or not cmds.objExists(tr_node[0]):
                    continue
                try:
                    t = cmds.xform(tr_node[0], q=True, ws=True, t=True)
                    snap["object_positions"][tr_node[0]] = (t[0], t[1], t[2])
                except Exception:
                    pass
        return snap

    def _restore_snapshot(self):
        """Write saved positions back absolutely. Idempotent; safe after Ctrl+Z."""
        snap = self._snapshot
        if not snap:
            self._preview_active = False
            return
        if snap.get("is_component"):
            for shape, pos_map in snap.get("vert_positions", {}).items():
                if not cmds.objExists(shape):
                    continue
                for vi, pos in pos_map.items():
                    try:
                        cmds.xform(u"{0}.vtx[{1}]".format(shape, vi),
                                   ws=True, t=pos)
                    except Exception:
                        pass
        else:
            for node, pos in snap.get("object_positions", {}).items():
                if not cmds.objExists(node):
                    continue
                try:
                    cmds.xform(node, ws=True, t=pos)
                except Exception:
                    pass
        self._preview_active = False
        self._snapshot = None

    def _set_preview_label(self, text, warn=False):
        self._lbl_preview_status.setText(text)
        if warn:
            self._lbl_preview_status.setStyleSheet(
                "color:#FF5252;font-size:10px;font-weight:bold;padding:4px;"
                "background-color:#2B2B2B;border-radius:3px")
        else:
            self._lbl_preview_status.setStyleSheet(
                "color:#8BC34A;font-size:10px;font-weight:bold;padding:4px;"
                "background-color:#2B2B2B;border-radius:3px")
        self._lbl_preview_status.setVisible(True)

    def _on_confirm(self):
        if not self._preview_active:
            return
        # Drop the snapshot — we're committing to the current state.
        # The preview chunk is already closed; user can still Ctrl+Z
        # to undo the whole operation if they change their mind.
        self._preview_active = False
        self._snapshot = None
        self._btn_confirm.setEnabled(False)
        self._btn_revert.setEnabled(False)
        msg = tr("ml_status_confirmed",
                 dist=u"{0:.4f}".format(self._last_dist),
                 axis=_ML_AXIS_NAMES[self._last_axis])
        self.status_msg.emit(msg)
        self._set_preview_label(msg, warn=False)

    def _on_revert(self):
        if not self._preview_active:
            return
        # Restore the snapshot inside its own undo chunk so the revert
        # itself is also undoable in one step.
        cmds.undoInfo(openChunk=True, chunkName="DW_MeshLanding_Revert")
        try:
            self._restore_snapshot()
        finally:
            cmds.undoInfo(closeChunk=True)
        self._btn_confirm.setEnabled(False)
        self._btn_revert.setEnabled(False)
        self.status_msg.emit(tr("ml_status_reverted"))
        self._lbl_preview_status.setVisible(False)

    def closeEvent(self, event):
        # Auto-revert any uncommitted preview when dialog closes.
        if self._preview_active:
            cmds.undoInfo(openChunk=True,
                          chunkName="DW_MeshLanding_AutoRevert")
            try:
                self._restore_snapshot()
            finally:
                cmds.undoInfo(closeChunk=True)
        super(MeshLandingDialog, self).closeEvent(event)

    # -- Language refresh --
    def refresh_labels(self):
        self.setWindowTitle(tr("ml_dlg_title"))
        self._lbl_mesh_a.setText(tr("ml_lbl_mesh_a"))
        self._lbl_mesh_b.setText(tr("ml_lbl_mesh_b"))
        self._btn_set_a.setText(tr("ml_btn_set"))
        self._btn_set_b.setText(tr("ml_btn_set"))
        self._btn_swap.setText(tr("ml_btn_swap"))
        self._lbl_axis.setText(tr("ml_lbl_axis"))
        self._lbl_dir.setText(tr("ml_lbl_direction"))
        self._rb_auto.setText(tr("ml_dir_auto"))
        self._rb_pos.setText(tr("ml_dir_positive"))
        self._rb_neg.setText(tr("ml_dir_negative"))
        self._lbl_mode.setText(tr("ml_lbl_mode"))
        self._rb_obj.setText(tr("ml_mode_object"))
        self._rb_comp.setText(tr("ml_mode_component"))
        self._lbl_offset.setText(tr("ml_lbl_offset"))
        self._btn_preview.setText(tr("ml_btn_preview"))
        self._btn_confirm.setText(tr("ml_btn_confirm"))
        self._btn_revert.setText(tr("ml_btn_revert"))
        self._btn_close.setText(tr("btn_close"))
# -*- coding: utf-8 -*-
# ============================================================================
# 0370_edge_snap.txt
# Edge Snap feature for DW_CollisionCheck "Snap" tab.
#
# Equalises the "width" (length) of selected edges. Typical use case:
# a belt, a step, or any row of edges that should all have the same
# width. The user selects edges (a ring-loop-like selection), the
# tool assigns each endpoint to side A or side B via bipartite BFS,
# and then the user can snap each pair toward A, toward B, toward the
# midpoint, or to a uniform target length.
#
# Depends on (defined earlier in the concatenated build):
#   VERSION, PY2, MAYA_AVAILABLE, cmds,
#   QtCore, QtGui, QtWidgets,
#   tr(), _STRINGS  (strings added in 0020_strings.txt),
#   _mkbtn()        (defined in 0200_ui_helpers.txt)
# ============================================================================


# ---------------------------------------------------------------------------
# Edge Snap: geometry helpers
# ---------------------------------------------------------------------------

def _es_expand_edge_loop_if_single(sel, mode="ring"):
    """If the selection is exactly one mesh edge, replace `sel` with
    the full ring OR loop containing that edge. Otherwise return
    `sel` unchanged.

    mode:
        "ring" (default) — walks via opposite sides of the edge's
                           adjacent quad faces (horizontal, "belt"
                           direction). Usual choice for width-
                           alignment on belts / steps.
        "loop"           — walks via the endpoint vertices, stepping
                           through the opposite edge of each quad
                           (the direction perpendicular to ring).
    """
    edge_items = [s for s in sel if u".e[" in s]
    if len(edge_items) != 1:
        return sel
    one = edge_items[0]
    try:
        shape_part, _, tail = one.partition(u".e[")
        ei = int(tail.rstrip(u"]"))
    except Exception:
        return sel
    try:
        cmds.select(one, r=True)
        if mode == "loop":
            cmds.polySelect(shape_part, edgeLoop=ei, add=True)
        else:
            cmds.polySelect(shape_part, edgeRing=ei, add=True)
    except Exception:
        return sel
    new_sel = cmds.ls(sl=True, fl=True, long=True) or []
    if len(new_sel) >= 1:
        return new_sel
    return sel


def _es_get_selected_edges(expand_mode="ring"):
    """Collect selected edges with per-edge metadata.

    If the user selected exactly one edge at launch time, the full
    edge ring (or loop, depending on expand_mode) containing that
    edge is auto-selected before we gather the data.

    expand_mode:
        "ring" — `polySelect -edgeRing`, belt direction (default).
        "loop" — `polySelect -edgeLoop`, perpendicular direction.

    Returns list of dicts:
        {
            "edge":    "|pCube1|pCubeShape1.e[12]",
            "shape":   "|pCube1|pCubeShape1",
            "v0_idx":  7,
            "v1_idx":  8,
            "p0":      (x,y,z),
            "p1":      (x,y,z),
        }

    Empty list if Maya unavailable or nothing valid selected.
    """
    if not MAYA_AVAILABLE:
        return []
    sel = cmds.ls(sl=True, fl=True, long=True) or []
    sel = _es_expand_edge_loop_if_single(sel, mode=expand_mode)
    edges = []
    seen = set()
    for item in sel:
        if u".e[" not in item:
            continue
        if item in seen:
            continue
        seen.add(item)
        try:
            shape_part, _, tail = item.partition(u".e[")
            ei = int(tail.rstrip(u"]"))
        except Exception:
            continue
        # Convert to the mesh shape long name.
        try:
            node_type = cmds.nodeType(shape_part)
            if node_type == "mesh":
                shape = cmds.ls(shape_part, long=True)[0]
            else:
                # shape_part was a transform — get its mesh shape child.
                shs = cmds.listRelatives(shape_part, shapes=True,
                                          noIntermediate=True,
                                          fullPath=True, type="mesh") or []
                if not shs:
                    continue
                shape = shs[0]
        except Exception:
            continue
        # Get the 2 endpoint vert indices.
        try:
            verts = cmds.polyListComponentConversion(
                item, fromEdge=True, toVertex=True) or []
            verts = cmds.ls(verts, fl=True) or []
        except Exception:
            continue
        if len(verts) < 2:
            continue
        v_idxs = []
        for v in verts[:2]:
            try:
                v_idxs.append(int(v.split(u"[")[-1].rstrip(u"]")))
            except Exception:
                v_idxs = []
                break
        if len(v_idxs) != 2:
            continue
        try:
            p0 = cmds.pointPosition(
                u"{0}.vtx[{1}]".format(shape, v_idxs[0]), w=True)
            p1 = cmds.pointPosition(
                u"{0}.vtx[{1}]".format(shape, v_idxs[1]), w=True)
        except Exception:
            continue
        edges.append({
            "edge":   item,
            "shape":  shape,
            "v0_idx": v_idxs[0],
            "v1_idx": v_idxs[1],
            "p0":     (p0[0], p0[1], p0[2]),
            "p1":     (p1[0], p1[1], p1[2]),
        })
    return edges


def _es_bipartite_assign(edges):
    """Assign each edge's endpoints to side A or side B via BFS.

    For every connected component of the selection graph (vertices
    linked by selected edges), we try a 2-colouring. If the component
    is bipartite, the colouring is used directly. If not (odd cycle),
    we still produce a best-effort colouring — the edges whose
    colouring failed are flagged so the UI can warn / still assign
    something deterministic.

    Returns a list parallel to `edges`, each entry being one of
        "ok"        — colouring succeeded for this edge
        "fallback"  — colouring uncertain; we kept the first endpoint
                      as side A as a best effort.
    After the call, each edge dict gets two new fields:
        "a_idx", "a_pos", "b_idx", "b_pos"
    so downstream code can treat A vs B uniformly regardless of which
    endpoint the edge originally pointed to.
    """
    # Build graph: vertex -> list of (neighbour_vert, edge_index)
    # Vertex key is (shape, vert_idx).
    adj = {}
    for ei, e in enumerate(edges):
        k0 = (e["shape"], e["v0_idx"])
        k1 = (e["shape"], e["v1_idx"])
        adj.setdefault(k0, []).append((k1, ei))
        adj.setdefault(k1, []).append((k0, ei))

    color = {}    # vertex_key -> 0 (side A) or 1 (side B)
    status = ["ok"] * len(edges)

    # BFS over every component.
    for start in list(adj.keys()):
        if start in color:
            continue
        color[start] = 0
        queue = [start]
        while queue:
            v = queue.pop(0)
            c = color[v]
            for nb, ei in adj.get(v, []):
                if nb not in color:
                    color[nb] = 1 - c
                    queue.append(nb)
                else:
                    if color[nb] == c:
                        # Non-bipartite — both endpoints of this edge
                        # got the same colour. Mark the offending edge
                        # and keep the colouring as-is.
                        status[ei] = "fallback"

    # Fill in a_idx / b_idx / a_pos / b_pos.
    for ei, e in enumerate(edges):
        k0 = (e["shape"], e["v0_idx"])
        k1 = (e["shape"], e["v1_idx"])
        c0 = color.get(k0, 0)
        c1 = color.get(k1, 1)
        # Convention: side A = colour 0, side B = colour 1.
        # If the colouring is degenerate (both same), just keep v0 as A.
        if c0 == 0 and c1 == 1:
            a_idx, a_pos = e["v0_idx"], e["p0"]
            b_idx, b_pos = e["v1_idx"], e["p1"]
        elif c0 == 1 and c1 == 0:
            a_idx, a_pos = e["v1_idx"], e["p1"]
            b_idx, b_pos = e["v0_idx"], e["p0"]
        else:
            a_idx, a_pos = e["v0_idx"], e["p0"]
            b_idx, b_pos = e["v1_idx"], e["p1"]
            status[ei] = "fallback"
        e["a_idx"] = a_idx
        e["a_pos"] = a_pos
        e["b_idx"] = b_idx
        e["b_pos"] = b_pos
    return status


def _es_compute_adjacency_pairs(edges):
    """Build the list of candidate adjacent edge pairs, each with the
    bend angle (in degrees, 0 = perfectly smooth, 90 = perpendicular).

    Returns a list of (ei, ej, bend_angle_deg, kind):
        kind = "face-opposite" for quad-opposite-edge adjacency
               (ring-rung-style: two rungs bordering the same quad)
        kind = "vertex-fan"    for adjacency via a shared vertex
               (loop-along-belt-style: two edges meeting at a vertex)

    The angle semantic depends on the kind:
        face-opposite → line angle between the two edges' direction
                         vectors (using |dot|). For a smoothly curving
                         belt this is near 0; at a corner it's larger.
        vertex-fan    → bend angle at the shared vertex. Computed as
                         (180° - angle between v→n1 and v→n2).
                         For a straight run of edges, v→n1 and v→n2
                         point in opposite directions → angle ≈ 180° →
                         bend ≈ 0°. At a right-angle corner, bend = 90°.

    We build a list rather than immediately deciding "cut or link" so
    the same data can feed both the BFS and the histogram widget.
    """
    import math as _m
    n = len(edges)
    if n == 0:
        return []

    # --- Shared-face (opposite-edge) adjacency ---------------------
    # Map each edge to the set of faces it belongs to.
    edge_faces = []
    for e in edges:
        faces = set()
        if MAYA_AVAILABLE:
            try:
                fs = cmds.polyListComponentConversion(
                    e["edge"], fromEdge=True, toFace=True) or []
                fs = cmds.ls(fs, fl=True, long=True) or []
                for f in fs:
                    faces.add(f)
            except Exception:
                pass
        edge_faces.append(faces)

    face_to_edges = {}
    for ei, faces in enumerate(edge_faces):
        for f in faces:
            face_to_edges.setdefault(f, []).append(ei)

    # Direction vectors A→B normalised.
    dirs = []
    for e in edges:
        ax, ay, az = e["a_pos"]
        bx, by, bz = e["b_pos"]
        dx = bx - ax; dy = by - ay; dz = bz - az
        l = (dx * dx + dy * dy + dz * dz) ** 0.5
        if l < 1.0e-9:
            dirs.append((1.0, 0.0, 0.0))
        else:
            dirs.append((dx / l, dy / l, dz / l))

    # Vertex keys per edge for quick "do they share a vertex?" test.
    vkeys = []
    for e in edges:
        vkeys.append({(e["shape"], e["v0_idx"]),
                      (e["shape"], e["v1_idx"])})

    pairs = []
    seen = set()

    # 1) Shared-face adjacency — but ONLY for edge pairs that DON'T
    # also share a vertex. A quad face has 4 edges; edges that share
    # a vertex on that face are "adjacent edges of the quad" and the
    # angle between their direction vectors is roughly 90° regardless
    # of whether the belt is straight — that's geometric noise. We
    # only want the "opposite" pairs (no shared vertex).
    for f, eis in face_to_edges.items():
        if len(eis) < 2:
            continue
        for i in range(len(eis)):
            for j in range(i + 1, len(eis)):
                a, b = eis[i], eis[j]
                if vkeys[a] & vkeys[b]:
                    # They share a vertex — that's handled by the
                    # vertex-fan pass below, not as face-opposite.
                    continue
                key = (a, b) if a < b else (b, a)
                if key in seen:
                    continue
                seen.add(key)
                d1 = dirs[a]
                d2 = dirs[b]
                dot = d1[0] * d2[0] + d1[1] * d2[1] + d1[2] * d2[2]
                dot_abs = max(-1.0, min(1.0, abs(dot)))
                line_angle = _m.degrees(_m.acos(dot_abs))
                pairs.append((a, b, line_angle, "face-opposite"))

    # 2) Vertex-fan adjacency — two edges meeting at a shared vertex.
    # Compute the TRUE bend angle at that vertex (rather than the
    # line angle between direction vectors A→B). The vectors go from
    # the shared vertex outward to each edge's far end.
    vert_to_edges = {}
    for ei, e in enumerate(edges):
        for vi in (e["v0_idx"], e["v1_idx"]):
            key = (e["shape"], vi)
            vert_to_edges.setdefault(key, []).append(ei)

    for vk, eis in vert_to_edges.items():
        if len(eis) < 2:
            continue
        shape, vi = vk
        # Position of the shared vertex is either a_pos or b_pos.
        def _far_end(ei):
            e = edges[ei]
            if e["v0_idx"] == vi:
                return e["p1"], e["p0"]    # far, near
            return e["p0"], e["p1"]
        for i in range(len(eis)):
            for j in range(i + 1, len(eis)):
                a, b = eis[i], eis[j]
                key = (a, b) if a < b else (b, a)
                if key in seen:
                    continue
                seen.add(key)
                fa, va = _far_end(a)
                fb, _  = _far_end(b)
                v1 = (fa[0] - va[0], fa[1] - va[1], fa[2] - va[2])
                v2 = (fb[0] - va[0], fb[1] - va[1], fb[2] - va[2])
                l1 = (v1[0]**2 + v1[1]**2 + v1[2]**2) ** 0.5
                l2 = (v2[0]**2 + v2[1]**2 + v2[2]**2) ** 0.5
                if l1 < 1.0e-9 or l2 < 1.0e-9:
                    continue
                v1 = (v1[0]/l1, v1[1]/l1, v1[2]/l1)
                v2 = (v2[0]/l2, v2[1]/l2, v2[2]/l2)
                dot = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
                dot = max(-1.0, min(1.0, dot))
                # Angle between the two outgoing vectors: 0° = same
                # direction (impossible for distinct edges meeting
                # at a vertex on a sane mesh, really). 180° = they
                # point exactly opposite — i.e. a straight line.
                open_angle = _m.degrees(_m.acos(dot))
                # Bend angle = how much the line bends at this
                # vertex relative to straight.
                #   straight (open_angle 180°) → bend 0°
                #   right angle (open 90°)      → bend 90°
                #   needle point (open 0°)      → bend 180°
                # We cap bend at 90° (sharper than that is still
                # "sharp" — all above 90 behave the same to us).
                bend = 180.0 - open_angle
                if bend > 90.0:
                    bend = 90.0
                pairs.append((a, b, bend, "vertex-fan"))

    return pairs


def _es_compute_ring_components(edges, corner_angle_deg):
    """Group the selected edges into "smooth regions" of the ring,
    splitting at corners sharper than `corner_angle_deg`.

    Delegates adjacency/angle computation to
    `_es_compute_adjacency_pairs`. Each pair whose bend angle exceeds
    the threshold is skipped (treated as a cut); the rest are merged
    into the same component via union-find.
    """
    n = len(edges)
    if n == 0:
        return []
    pairs = _es_compute_adjacency_pairs(edges)
    adj = [set() for _ in range(n)]
    for a, b, angle, _kind in pairs:
        if angle <= corner_angle_deg:
            adj[a].add(b)
            adj[b].add(a)

    comp = [-1] * n
    cid = 0
    for i in range(n):
        if comp[i] != -1:
            continue
        comp[i] = cid
        stack = [i]
        while stack:
            v = stack.pop()
            for nb in adj[v]:
                if comp[nb] == -1:
                    comp[nb] = cid
                    stack.append(nb)
        cid += 1
    return comp


def _es_edge_length(e):
    ax, ay, az = e["a_pos"]
    bx, by, bz = e["b_pos"]
    dx = bx - ax; dy = by - ay; dz = bz - az
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def _es_darken(hex_colour, factor=0.8):
    """Return a darker variant of a #RRGGBB hex colour (for hover)."""
    h = hex_colour.lstrip("#")
    if len(h) != 6:
        return hex_colour
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
    except ValueError:
        return hex_colour
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return "#{0:02X}{1:02X}{2:02X}".format(r, g, b)


def _es_set_vtx_pos(shape, vi, pos):
    """Set a vertex's world-space position via cmds.xform."""
    try:
        cmds.xform(u"{0}.vtx[{1}]".format(shape, vi),
                   ws=True, t=(pos[0], pos[1], pos[2]))
    except Exception:
        pass


def _es_snap_edge_to_length(e, target_length, anchor):
    """Scale one edge so its new length = target_length, anchored on
    one of the two endpoints or on the current midpoint.

    anchor:
        0 = keep A, move B along the current edge direction so the
            edge length becomes target_length ("A-anchored")
        1 = keep B, move A along the current edge direction so the
            edge length becomes target_length ("B-anchored")
        2 = keep midpoint, scale both endpoints symmetrically
            ("centre-anchored", legacy behaviour)

    The A→B direction vector is preserved (we only rescale along it).
    If the edge is degenerate (near-zero length) we skip it because we
    have no direction to preserve.
    """
    ax, ay, az = e["a_pos"]
    bx, by, bz = e["b_pos"]
    dx = bx - ax; dy = by - ay; dz = bz - az
    curlen = (dx * dx + dy * dy + dz * dz) ** 0.5
    if curlen < 1.0e-10:
        return
    ux = dx / curlen
    uy = dy / curlen
    uz = dz / curlen
    shape = e["shape"]
    if anchor == 0:
        # Keep A; put B exactly at distance `target_length` from A
        # along the current direction.
        new_b = (ax + ux * target_length,
                 ay + uy * target_length,
                 az + uz * target_length)
        _es_set_vtx_pos(shape, e["b_idx"], new_b)
    elif anchor == 1:
        # Keep B; put A exactly at distance `target_length` from B,
        # i.e. B minus the unit vector times target.
        new_a = (bx - ux * target_length,
                 by - uy * target_length,
                 bz - uz * target_length)
        _es_set_vtx_pos(shape, e["a_idx"], new_a)
    else:
        # Keep midpoint; symmetric scale.
        half = target_length * 0.5
        mx = (ax + bx) * 0.5
        my = (ay + by) * 0.5
        mz = (az + bz) * 0.5
        new_a = (mx - ux * half, my - uy * half, mz - uz * half)
        new_b = (mx + ux * half, my + uy * half, mz + uz * half)
        _es_set_vtx_pos(shape, e["a_idx"], new_a)
        _es_set_vtx_pos(shape, e["b_idx"], new_b)


# ---------------------------------------------------------------------------
# Belt width mode: detect the two parallel edge loops (the two "brims")
# that the selected rungs connect, and snap endpoints *along* them.
# ---------------------------------------------------------------------------

def _es_expand_brim_from_vertex(shape, vert_idx, forbidden_edge_set,
                                  rung_verts_set):
    """Given a shape and a seed vertex index, find the edge loop that
    runs along the belt's brim on this side — i.e. the chain of
    edges that:
      * starts at `vert_idx`,
      * uses edges that are NOT in `forbidden_edge_set` (rung edges),
      * stays on the "brim" by preferring edges whose far endpoint is
        another rung endpoint on the same side (i.e. in rung_verts_set).

    Returns a list of world-space positions along the brim in order,
    or [] if no suitable brim could be traced.

    This avoids messing with Maya's selection (the previous
    `polySelect -edgeLoop`-based approach disturbed the current
    selection and sometimes returned the rungs themselves).
    """
    if not MAYA_AVAILABLE:
        return []

    # Build a small helper that walks vertex-by-vertex, picking at each
    # step a neighbour that (a) is reached by a non-rung edge, (b) is
    # preferably a rung endpoint on this side, (c) hasn't been visited.
    def _neighbours(v_idx):
        """Return list of (neighbour_v_idx, edge_str, edge_idx) tuples
        for the given vertex, excluding forbidden (rung) edges."""
        vtx = u"{0}.vtx[{1}]".format(shape, v_idx)
        try:
            inc = cmds.polyListComponentConversion(
                vtx, fromVertex=True, toEdge=True) or []
            inc = cmds.ls(inc, fl=True, long=True) or []
        except Exception:
            return []
        out = []
        for e in inc:
            if e in forbidden_edge_set:
                continue
            try:
                ei = int(e.split(u"[")[-1].rstrip(u"]"))
                verts = cmds.polyListComponentConversion(
                    e, fromEdge=True, toVertex=True) or []
                verts = cmds.ls(verts, fl=True, long=True) or []
                vids = []
                for x in verts:
                    try:
                        vids.append(int(x.split(u"[")[-1].rstrip(u"]")))
                    except Exception:
                        pass
                if len(vids) != 2:
                    continue
                other = vids[0] if vids[1] == v_idx else vids[1]
                out.append((other, e, ei))
            except Exception:
                continue
        return out

    def _get_pos(vi):
        try:
            p = cmds.pointPosition(
                u"{0}.vtx[{1}]".format(shape, vi), w=True)
            return (p[0], p[1], p[2])
        except Exception:
            return None

    # Walk in two directions from the seed vertex, preferring rung-
    # endpoint neighbours (brim connects rung-endpoints to each other).
    def _walk(start):
        visited = {start}
        seq = [start]
        cur = start
        # Iterate forward as far as possible.
        while True:
            nbrs = _neighbours(cur)
            # Prefer neighbours that are themselves rung endpoints (on
            # this side), not yet visited.
            best = None
            for other, _estr, _ei in nbrs:
                if other in visited:
                    continue
                if other in rung_verts_set:
                    best = other
                    break
            if best is None:
                # No rung-endpoint neighbour — fall back to any unvisited
                # neighbour so we still trace *some* polyline.
                for other, _estr, _ei in nbrs:
                    if other not in visited:
                        best = other
                        break
            if best is None:
                break
            seq.append(best)
            visited.add(best)
            cur = best
            if len(seq) > 10000:
                break
        return seq

    forward = _walk(vert_idx)
    # Now walk backward from the seed vertex.
    visited_fwd = set(forward)
    back = [vert_idx]
    cur = vert_idx
    while True:
        nbrs = _neighbours(cur)
        best = None
        for other, _estr, _ei in nbrs:
            if other in visited_fwd or other in back:
                continue
            if other in rung_verts_set:
                best = other
                break
        if best is None:
            for other, _estr, _ei in nbrs:
                if other in visited_fwd or other in back:
                    continue
                best = other
                break
        if best is None:
            break
        back.append(best)
        cur = best
        if len(back) > 10000:
            break

    # Combine back (reversed, minus duplicated seed) + forward.
    ordered_verts = list(reversed(back[1:])) + forward
    positions = []
    for vi in ordered_verts:
        p = _get_pos(vi)
        if p is not None:
            positions.append(p)
    return positions


def _es_detect_belt_brims(edges):
    """For each rung edge in `edges`, detect the two brim polylines
    (one on side A, one on side B) that the rung connects.

    Returns a dict:
        {
            "brim_a_verts":   {rung_ei -> [(x,y,z), (x,y,z), ...]},
            "brim_b_verts":   {rung_ei -> [(x,y,z), (x,y,z), ...]},
        }

    The polylines are expressed as ordered world-space positions so
    downstream code can project points onto them. Empty list means
    brim detection failed for that rung (e.g. isolated rung — we fall
    back to simple length snap in that case).
    """
    if not MAYA_AVAILABLE:
        return {"brim_a_verts": {}, "brim_b_verts": {}}
    rung_edge_set = set(e["edge"] for e in edges)
    # All A-side vertices and all B-side vertices across the rung
    # selection — used to help the brim walker stay on the correct
    # side of the belt.
    side_a_verts = set()
    side_b_verts = set()
    for e in edges:
        side_a_verts.add(e["a_idx"])
        side_b_verts.add(e["b_idx"])

    brim_a_verts = {}
    brim_b_verts = {}
    for ei, e in enumerate(edges):
        shape = e["shape"]
        brim_a_verts[ei] = _es_expand_brim_from_vertex(
            shape, e["a_idx"], rung_edge_set, side_a_verts)
        brim_b_verts[ei] = _es_expand_brim_from_vertex(
            shape, e["b_idx"], rung_edge_set, side_b_verts)
    return {"brim_a_verts": brim_a_verts,
            "brim_b_verts": brim_b_verts}


def _es_project_point_onto_polyline(point, polyline):
    """Given a world-space point and a polyline (list of (x,y,z)),
    return the closest point that lies ON any segment of the polyline.

    Returns (closest_point, seg_idx, t_along_seg) — or None if polyline
    has < 2 vertices.
    """
    if len(polyline) < 2:
        return None
    px, py, pz = point
    best = None
    best_d2 = None
    best_info = None
    for i in range(len(polyline) - 1):
        ax, ay, az = polyline[i]
        bx, by, bz = polyline[i + 1]
        dx = bx - ax; dy = by - ay; dz = bz - az
        seg_len2 = dx * dx + dy * dy + dz * dz
        if seg_len2 < 1.0e-18:
            continue
        t = ((px - ax) * dx + (py - ay) * dy + (pz - az) * dz) / seg_len2
        t_clamped = max(0.0, min(1.0, t))
        cx = ax + dx * t_clamped
        cy = ay + dy * t_clamped
        cz = az + dz * t_clamped
        ex = px - cx; ey = py - cy; ez = pz - cz
        d2 = ex * ex + ey * ey + ez * ez
        if best_d2 is None or d2 < best_d2:
            best_d2 = d2
            best = (cx, cy, cz)
            best_info = (i, t_clamped)
    if best is None:
        return None
    return (best, best_info[0], best_info[1])


def _es_slide_along_polyline(start_point, polyline, target_distance,
                              direction_hint):
    """Starting from `start_point` (which must already lie on or near
    the polyline), walk `target_distance` units ALONG the polyline in
    the direction suggested by `direction_hint` (a unit-ish vector).

    Returns the new world-space point. If the polyline is too short
    to absorb the distance, clamps at the polyline's endpoint.

    Implementation: first find the segment `start_point` lies on
    (closest-point projection), then step through segments until the
    accumulated along-polyline distance matches `target_distance`.
    """
    proj = _es_project_point_onto_polyline(start_point, polyline)
    if proj is None:
        return start_point
    (on_pt, seg_idx, t) = proj
    # Determine which direction to walk along the polyline, using
    # direction_hint dotted against the local tangent.
    # Try forward first.
    def _walk(forward):
        remaining = target_distance
        pos = on_pt
        idx = seg_idx
        local_t = t
        while remaining > 1.0e-12:
            if forward:
                # Walk from `pos` toward polyline[idx+1].
                if idx + 1 >= len(polyline):
                    return pos
                nxt = polyline[idx + 1]
                dx = nxt[0] - pos[0]
                dy = nxt[1] - pos[1]
                dz = nxt[2] - pos[2]
                seg_remaining = (dx * dx + dy * dy + dz * dz) ** 0.5
                if seg_remaining >= remaining:
                    frac = remaining / seg_remaining
                    return (pos[0] + dx * frac,
                            pos[1] + dy * frac,
                            pos[2] + dz * frac)
                remaining -= seg_remaining
                pos = nxt
                idx += 1
            else:
                # Walk from `pos` toward polyline[idx].
                if idx < 0:
                    return pos
                prv = polyline[idx]
                dx = prv[0] - pos[0]
                dy = prv[1] - pos[1]
                dz = prv[2] - pos[2]
                seg_remaining = (dx * dx + dy * dy + dz * dz) ** 0.5
                if seg_remaining >= remaining:
                    frac = remaining / seg_remaining
                    return (pos[0] + dx * frac,
                            pos[1] + dy * frac,
                            pos[2] + dz * frac)
                remaining -= seg_remaining
                pos = prv
                idx -= 1
        return pos

    # Local tangent at on_pt: polyline[seg_idx+1] - polyline[seg_idx].
    if seg_idx + 1 < len(polyline):
        tdx = polyline[seg_idx + 1][0] - polyline[seg_idx][0]
        tdy = polyline[seg_idx + 1][1] - polyline[seg_idx][1]
        tdz = polyline[seg_idx + 1][2] - polyline[seg_idx][2]
    else:
        tdx = polyline[seg_idx][0] - polyline[seg_idx - 1][0]
        tdy = polyline[seg_idx][1] - polyline[seg_idx - 1][1]
        tdz = polyline[seg_idx][2] - polyline[seg_idx - 1][2]
    tl = (tdx * tdx + tdy * tdy + tdz * tdz) ** 0.5
    if tl > 1.0e-12:
        tdx /= tl; tdy /= tl; tdz /= tl
    dot = (direction_hint[0] * tdx
           + direction_hint[1] * tdy
           + direction_hint[2] * tdz)
    forward = (dot >= 0.0)
    return _walk(forward)


def _es_belt_width_from_rung(rung_pos_a, rung_pos_b,
                              brim_a_poly, brim_b_poly):
    """Measure the current "belt width" at a specific rung.

    Returns the straight distance between A's projection onto brim A
    and B's projection onto brim B. This is the straight chord; for
    an ideal, perpendicular rung it equals the rung length.
    """
    pa = _es_project_point_onto_polyline(rung_pos_a, brim_a_poly)
    pb = _es_project_point_onto_polyline(rung_pos_b, brim_b_poly)
    if pa is None or pb is None:
        return None
    (ax, ay, az), _, _ = pa
    (bx, by, bz), _, _ = pb
    dx = bx - ax; dy = by - ay; dz = bz - az
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def _es_snap_belt_rung_to_width(e, target_width, anchor,
                                  brim_a_poly, brim_b_poly):
    """Adjust one rung so its A→B *straight* distance becomes
    target_width by sliding the moving endpoint ALONG its brim.

    anchor:
        0 = keep A; slide B along brim B so |A-B| == target_width.
            The new B is found by walking along brim B from the
            current closest-point projection toward the direction
            closest to (current B minus A).
        1 = keep B; slide A along brim A.
        2 = keep midpoint; slide both endpoints symmetrically outward
            along their brims.

    If brim polylines are empty, falls back to the simple length-
    based snap (so the user still gets *some* effect).
    """
    if (not brim_a_poly or len(brim_a_poly) < 2
            or not brim_b_poly or len(brim_b_poly) < 2):
        _es_snap_edge_to_length(e, target_width, anchor)
        return
    ax, ay, az = e["a_pos"]
    bx, by, bz = e["b_pos"]
    shape = e["shape"]
    if anchor == 0:
        # Slide B along brim B. Direction hint = current B minus A
        # projected into brim-B's tangent direction; we use this to
        # pick "forward" vs "back" along the brim.
        # Step 1: project A to brim A (its anchor point).
        proj_a = _es_project_point_onto_polyline((ax, ay, az), brim_a_poly)
        proj_b = _es_project_point_onto_polyline((bx, by, bz), brim_b_poly)
        if proj_a is None or proj_b is None:
            _es_snap_edge_to_length(e, target_width, anchor)
            return
        (apx, apy, apz), _, _ = proj_a
        (bpx, bpy, bpz), seg_b, t_b = proj_b
        # Target: find point on brim B such that its distance from
        # (apx, apy, apz) equals target_width. We do this iteratively
        # by finding the closest-approach parametric, then adjusting.
        # For simplicity and robustness, we use a 1-D search along
        # the polyline's arc-length from proj_b, using the same
        # _walk helper via _es_slide_along_polyline with the current
        # pb as start and the desired delta as distance. But first we
        # need the current ||A_brim - B_brim|| and how much we need
        # to shift B along the brim to make the chord length equal
        # target_width.
        # Short-cut: project A onto brim B too — the foot of A on
        # brim B is the point on brim B closest to A. Then we need
        # the point on brim B that is target_width away from A. We
        # compute it by sampling arc-length along brim B around the
        # foot until |A - sampled| ≈ target_width.
        foot_of_a = _es_project_point_onto_polyline(
            (apx, apy, apz), brim_b_poly)
        if foot_of_a is None:
            _es_snap_edge_to_length(e, target_width, anchor)
            return
        (foax, foay, foaz), foot_seg, foot_t = foot_of_a
        dfa = (foax - apx, foay - apy, foaz - apz)
        foot_dist = (dfa[0] ** 2 + dfa[1] ** 2 + dfa[2] ** 2) ** 0.5
        if target_width <= foot_dist + 1.0e-9:
            # Can't reach a chord shorter than the perpendicular
            # distance. Clamp to the foot.
            new_b = (foax, foay, foaz)
        else:
            # We need to walk from the foot along brim B in the
            # direction closest to the current B (so we keep the
            # rung on the same side as it was) by a distance that
            # makes the chord (A→new_b) == target_width. That's a
            # right-triangle: chord² = foot² + walk².
            walk_d = (target_width * target_width
                      - foot_dist * foot_dist) ** 0.5
            # Direction hint = from foot toward current B projection.
            hint = (bpx - foax, bpy - foay, bpz - foaz)
            hl = (hint[0] ** 2 + hint[1] ** 2 + hint[2] ** 2) ** 0.5
            if hl < 1.0e-9:
                # Degenerate — current B is already at foot. Use
                # brim-B tangent as a fallback direction.
                if foot_seg + 1 < len(brim_b_poly):
                    hint = (brim_b_poly[foot_seg + 1][0] - foax,
                            brim_b_poly[foot_seg + 1][1] - foay,
                            brim_b_poly[foot_seg + 1][2] - foaz)
                else:
                    hint = (brim_b_poly[foot_seg][0]
                            - brim_b_poly[foot_seg - 1][0],
                            brim_b_poly[foot_seg][1]
                            - brim_b_poly[foot_seg - 1][1],
                            brim_b_poly[foot_seg][2]
                            - brim_b_poly[foot_seg - 1][2])
                hl = (hint[0] ** 2 + hint[1] ** 2 + hint[2] ** 2) ** 0.5
                if hl < 1.0e-9:
                    _es_snap_edge_to_length(e, target_width, anchor)
                    return
            hint = (hint[0] / hl, hint[1] / hl, hint[2] / hl)
            new_b = _es_slide_along_polyline(
                (foax, foay, foaz), brim_b_poly, walk_d, hint)
        _es_set_vtx_pos(shape, e["b_idx"], new_b)
    elif anchor == 1:
        # Mirror: keep B, slide A on brim A.
        proj_a = _es_project_point_onto_polyline((ax, ay, az), brim_a_poly)
        proj_b = _es_project_point_onto_polyline((bx, by, bz), brim_b_poly)
        if proj_a is None or proj_b is None:
            _es_snap_edge_to_length(e, target_width, anchor)
            return
        (apx, apy, apz), _, _ = proj_a
        (bpx, bpy, bpz), _, _ = proj_b
        foot_of_b = _es_project_point_onto_polyline(
            (bpx, bpy, bpz), brim_a_poly)
        if foot_of_b is None:
            _es_snap_edge_to_length(e, target_width, anchor)
            return
        (fbax, fbay, fbaz), foot_seg, _ = foot_of_b
        dfb = (fbax - bpx, fbay - bpy, fbaz - bpz)
        foot_dist = (dfb[0] ** 2 + dfb[1] ** 2 + dfb[2] ** 2) ** 0.5
        if target_width <= foot_dist + 1.0e-9:
            new_a = (fbax, fbay, fbaz)
        else:
            walk_d = (target_width * target_width
                      - foot_dist * foot_dist) ** 0.5
            hint = (apx - fbax, apy - fbay, apz - fbaz)
            hl = (hint[0] ** 2 + hint[1] ** 2 + hint[2] ** 2) ** 0.5
            if hl < 1.0e-9:
                if foot_seg + 1 < len(brim_a_poly):
                    hint = (brim_a_poly[foot_seg + 1][0] - fbax,
                            brim_a_poly[foot_seg + 1][1] - fbay,
                            brim_a_poly[foot_seg + 1][2] - fbaz)
                else:
                    hint = (brim_a_poly[foot_seg][0]
                            - brim_a_poly[foot_seg - 1][0],
                            brim_a_poly[foot_seg][1]
                            - brim_a_poly[foot_seg - 1][1],
                            brim_a_poly[foot_seg][2]
                            - brim_a_poly[foot_seg - 1][2])
                hl = (hint[0] ** 2 + hint[1] ** 2 + hint[2] ** 2) ** 0.5
                if hl < 1.0e-9:
                    _es_snap_edge_to_length(e, target_width, anchor)
                    return
            hint = (hint[0] / hl, hint[1] / hl, hint[2] / hl)
            new_a = _es_slide_along_polyline(
                (fbax, fbay, fbaz), brim_a_poly, walk_d, hint)
        _es_set_vtx_pos(shape, e["a_idx"], new_a)
    else:
        # Centre-anchored belt width: pull both endpoints symmetrically
        # toward the midpoint until the chord equals target_width.
        # Implementation: find foot of midpoint on each brim, then
        # walk half-distance outward on each brim. Simpler for now:
        # fallback to length-based centre snap along the current rung
        # direction.
        _es_snap_edge_to_length(e, target_width, anchor)


# ---------------------------------------------------------------------------
# Edge Snap: stylesheet scraps
# ---------------------------------------------------------------------------

_ES_SPIN_SS = (
    "QDoubleSpinBox{background-color:#2B2B2B;color:#EEE;"
    "border:1px solid #555;border-radius:3px;padding:1px;font-size:10px}")

_ES_TABLE_SS = (
    "QTableWidget{background-color:#2B2B2B;color:#EEE;"
    "alternate-background-color:#323232;gridline-color:#444;"
    "font-size:10px;selection-background-color:#3A5A7C;"
    "selection-color:#FFF}"
    "QHeaderView::section{background-color:#3C3C3C;color:#CCC;"
    "padding:3px;border:1px solid #444;font-size:10px}")

# Colours used to tint the "Region" column so different smooth
# regions of the selection are easy to distinguish visually.
_ES_REGION_COLOURS = [
    "#81D4FA",   # light blue
    "#FFD54F",   # amber
    "#A5D6A7",   # light green
    "#F48FB1",   # pink
    "#CE93D8",   # light purple
    "#FFAB91",   # peach
    "#80CBC4",   # teal
    "#E6EE9C",   # lime
]


# ---------------------------------------------------------------------------
# Bend-angle histogram widget
# ---------------------------------------------------------------------------

class _EsAngleHistogram(QtWidgets.QWidget):
    """Horizontal histogram showing the distribution of bend angles
    between adjacent selected edges (0°..90°), overlaid with an
    interactive threshold marker.

    Bars to the LEFT of the threshold are drawn in the "kept"
    colour (green-ish) because their adjacency is preserved.
    Bars to the RIGHT are drawn in the "cut" colour (red-ish),
    highlighting which pairs the threshold will split on.

    The user drags the vertical orange marker left/right (or clicks
    anywhere on the chart) to change the threshold. A `threshold_changed`
    signal fires with the new value in degrees.
    """

    _N_BINS = 36   # 2.5° per bin across 0..90
    _MIN_DEG = 5.0
    _MAX_DEG = 89.0
    _PAD = 4

    threshold_changed = QtCore.Signal(float)

    def __init__(self, parent=None):
        super(_EsAngleHistogram, self).__init__(parent)
        self._angles = []            # list of bend angles in degrees
        self._threshold = 60.0
        self._dragging = False
        self.setMinimumHeight(48)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                            QtWidgets.QSizePolicy.Fixed)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        # We want mouse-move events even when no button is held, so
        # the cursor can change near the marker.
        self.setMouseTracking(True)

    def set_angles(self, angles):
        """Replace the dataset and repaint."""
        self._angles = list(angles) if angles else []
        self.update()

    def set_threshold(self, threshold_deg):
        v = max(self._MIN_DEG,
                min(self._MAX_DEG, float(threshold_deg)))
        if abs(v - self._threshold) < 1.0e-6:
            return
        self._threshold = v
        self.update()

    def _x_to_deg(self, x):
        pad = self._PAD
        chart_w = max(1, self.width() - pad * 2)
        frac = (x - pad) / float(chart_w)
        return max(self._MIN_DEG,
                    min(self._MAX_DEG, frac * 90.0))

    def _deg_to_x(self, deg):
        pad = self._PAD
        chart_w = max(1, self.width() - pad * 2)
        return pad + int((deg / 90.0) * chart_w)

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self._dragging = True
            new_deg = self._x_to_deg(ev.pos().x())
            self.set_threshold(new_deg)
            self.threshold_changed.emit(self._threshold)
            ev.accept()

    def mouseMoveEvent(self, ev):
        if self._dragging:
            new_deg = self._x_to_deg(ev.pos().x())
            self.set_threshold(new_deg)
            self.threshold_changed.emit(self._threshold)
            ev.accept()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self._dragging:
            self._dragging = False
            ev.accept()

    def paintEvent(self, _ev):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, False)

        w = self.width()
        h = self.height()
        # Background.
        p.fillRect(0, 0, w, h, QtGui.QColor("#1A1A1A"))
        if w <= 4 or h <= 4:
            p.end()
            return

        pad = self._PAD
        chart_w = w - pad * 2
        chart_h = h - pad * 2

        # Bin the angles.
        bins = [0] * self._N_BINS
        # Leave room at the bottom for tick labels.
        label_h = 12
        bar_area_h = max(1, chart_h - label_h)

        for a in self._angles:
            a = max(0.0, min(90.0, a))
            b = int(a / 90.0 * self._N_BINS)
            if b >= self._N_BINS:
                b = self._N_BINS - 1
            bins[b] += 1
        max_count = max(bins) if bins else 0

        # Threshold position in pixels.
        t_frac = max(0.0, min(90.0, self._threshold)) / 90.0
        t_px = pad + int(t_frac * chart_w)
        bar_bottom = pad + bar_area_h

        # Draw bars.
        bin_w = chart_w / float(self._N_BINS)
        for i, c in enumerate(bins):
            if c == 0:
                continue
            bar_h = int((c / float(max_count)) * bar_area_h) if max_count > 0 else 0
            if bar_h < 1:
                bar_h = 1
            x0 = pad + int(i * bin_w)
            x1 = pad + int((i + 1) * bin_w)
            # Colour: left of threshold = kept (green), right = cut (red).
            bin_centre = (i + 0.5) / self._N_BINS * 90.0
            if bin_centre <= self._threshold:
                col = QtGui.QColor("#4CAF50")
            else:
                col = QtGui.QColor("#E53935")
            p.fillRect(x0, bar_bottom - bar_h,
                       max(1, x1 - x0 - 1), bar_h, col)

        # Baseline axis.
        p.setPen(QtGui.QPen(QtGui.QColor("#444"), 1))
        p.drawLine(pad, bar_bottom, pad + chart_w, bar_bottom)

        # Tick labels at 0°, 30°, 60°, 90°.
        p.setPen(QtGui.QPen(QtGui.QColor("#888"), 1))
        f = p.font()
        f.setPointSize(7)
        p.setFont(f)
        for deg in (0, 30, 60, 90):
            x = pad + int((deg / 90.0) * chart_w)
            # Tick.
            p.drawLine(x, bar_bottom, x, bar_bottom + 3)
            p.drawText(x - 9, bar_bottom + label_h,
                       u"{0}\u00B0".format(deg))

        # Threshold line + triangular drag handle at the top.
        pen = QtGui.QPen(QtGui.QColor("#FF9800"), 2)
        p.setPen(pen)
        p.drawLine(t_px, pad, t_px, bar_bottom)
        # Triangle handle pointing down at the top of the line.
        tri = QtGui.QPolygon([
            QtCore.QPoint(t_px - 5, pad),
            QtCore.QPoint(t_px + 5, pad),
            QtCore.QPoint(t_px, pad + 6),
        ])
        p.setBrush(QtGui.QColor("#FF9800"))
        p.setPen(QtGui.QPen(QtGui.QColor("#E65100"), 1))
        p.drawPolygon(tri)

        p.end()


# ---------------------------------------------------------------------------
# Edge Snap: result window
# ---------------------------------------------------------------------------

class EdgeSnapResultWindow(QtWidgets.QDialog):
    """Row-per-edge table with direction buttons, uniform-length mode,
    per-row snap logging, confirm/revert (single undo chunk)."""

    status_msg = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(EdgeSnapResultWindow, self).__init__(parent)
        self.setObjectName("DW_EdgeSnap_Result")
        self.setWindowTitle(tr("es_result_title"))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumSize(620, 460)
        self.setStyleSheet(
            "QDialog{background-color:#333;color:#EEE}"
            "QLabel{color:#EEE}")
        self._edges = []          # list of edge dicts
        self._status = []         # per-edge bipartite status ("ok"/"fallback")
        self._components = []     # per-edge ring-component id
        self._corner_angle = 60.0 # deg — see set_data / slider
        # Belt-width mode data — populated on demand (only when the
        # user switches to belt-width mode, to avoid the cost when
        # they only need simple length alignment).
        self._brim_data = None
        self._belt_mode = False
        self._snap_log = {}       # edge_str -> direction name
        self._undo_open = False
        self._build()

    # -- UI construction --
    def _build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(8, 8, 8, 8)
        lo.setSpacing(6)

        # Mode selector: simple edge length vs. belt-width-along-brims.
        # Belt-width mode detects the two parallel edge loops that the
        # selected rungs connect, measures the perpendicular distance
        # between them, and slides the moving endpoint ALONG its brim
        # rather than along the current rung direction.
        mode_row = QtWidgets.QHBoxLayout()
        mode_row.setSpacing(8)
        mode_row.setContentsMargins(0, 0, 0, 0)
        self._lbl_mode = QtWidgets.QLabel(tr("es_lbl_mode"))
        self._lbl_mode.setStyleSheet("color:#AAA;font-size:10px")
        mode_row.addWidget(self._lbl_mode)
        rb_ss = ("QRadioButton{color:#DDD;font-size:10px}"
                 "QRadioButton::indicator{width:11px;height:11px}")
        self._rb_mode_length = QtWidgets.QRadioButton(tr("es_mode_length"))
        self._rb_mode_length.setStyleSheet(rb_ss)
        self._rb_mode_length.setChecked(True)
        self._rb_mode_length.toggled.connect(self._on_mode_changed)
        mode_row.addWidget(self._rb_mode_length)
        self._rb_mode_belt = QtWidgets.QRadioButton(tr("es_mode_belt"))
        self._rb_mode_belt.setStyleSheet(rb_ss)
        self._rb_mode_belt.toggled.connect(self._on_mode_changed)
        mode_row.addWidget(self._rb_mode_belt)
        self._lbl_mode_hint = QtWidgets.QLabel(tr("es_lbl_mode_hint"))
        self._lbl_mode_hint.setStyleSheet(
            "color:#777;font-size:9px;padding:0 4px")
        self._lbl_mode_hint.setWordWrap(True)
        mode_row.addWidget(self._lbl_mode_hint, 1)
        lo.addLayout(mode_row)

        # Scope / status line at top.
        self._scope_lbl = QtWidgets.QLabel(u"")
        self._scope_lbl.setStyleSheet(
            "color:#8BC34A;background-color:#2B2B2B;"
            "padding:3px 8px;border-radius:3px;font-size:10px")
        self._scope_lbl.setWordWrap(True)
        lo.addWidget(self._scope_lbl)

        # Region chip strip — one clickable button per region, with
        # per-region edge count + average width. Clicking a chip
        # selects just that region's rows in the table (so the
        # direction buttons operate on a single region) and loads its
        # average into the target-width spin.
        self._region_chip_wrapper = QtWidgets.QFrame()
        self._region_chip_wrapper.setStyleSheet(
            "QFrame{background-color:#222;border-radius:3px}")
        chip_lo = QtWidgets.QHBoxLayout(self._region_chip_wrapper)
        chip_lo.setContentsMargins(6, 4, 6, 4)
        chip_lo.setSpacing(6)
        self._region_chip_layout = chip_lo
        # Persistent "Select all" button on the right so the user can
        # revert to working with every row at once.
        self._region_chip_placeholder = QtWidgets.QLabel(u"")
        self._region_chip_placeholder.setStyleSheet(
            "color:#777;font-size:10px")
        chip_lo.addWidget(self._region_chip_placeholder)
        chip_lo.addStretch()
        self._btn_select_all = _mkbtn(tr("es_btn_select_all"), 22,
                                       "#607D8B", "#455A64", fs=10)
        self._btn_select_all.clicked.connect(self._on_select_all_rows)
        chip_lo.addWidget(self._btn_select_all)
        self._region_chip_wrapper.setVisible(False)
        lo.addWidget(self._region_chip_wrapper)
        # List of dynamically-added chip buttons so we can delete them
        # between refreshes.
        self._region_chip_buttons = []

        # Uniform-length row: spinbox + apply button.
        uni = QtWidgets.QHBoxLayout()
        uni.setSpacing(6)
        self._lbl_uniform = QtWidgets.QLabel(tr("es_lbl_uniform"))
        self._lbl_uniform.setStyleSheet("color:#AAA;font-size:10px")
        uni.addWidget(self._lbl_uniform)
        self._spin_uniform = QtWidgets.QDoubleSpinBox()
        self._spin_uniform.setRange(0.0, 1.0e6)
        self._spin_uniform.setDecimals(4)
        self._spin_uniform.setSingleStep(0.01)
        self._spin_uniform.setValue(0.0)
        self._spin_uniform.setFixedWidth(100)
        self._spin_uniform.setStyleSheet(_ES_SPIN_SS)
        uni.addWidget(self._spin_uniform)
        self._cb_per_region = QtWidgets.QCheckBox(tr("es_chk_per_region"))
        self._cb_per_region.setToolTip(tr("es_chk_per_region_tip"))
        self._cb_per_region.setStyleSheet(
            "QCheckBox{color:#FFD54F;font-size:10px}"
            "QCheckBox::indicator{width:12px;height:12px}")
        self._cb_per_region.setChecked(True)
        uni.addWidget(self._cb_per_region)
        # Hint label so it's clear the direction buttons below use this.
        self._lbl_uniform_hint = QtWidgets.QLabel(tr("es_lbl_uniform_hint"))
        self._lbl_uniform_hint.setStyleSheet(
            "color:#777;font-size:9px;padding:0 4px")
        uni.addWidget(self._lbl_uniform_hint)
        uni.addStretch()
        lo.addLayout(uni)

        # Corner-angle control row: a compact label + live value +
        # hint, followed below by the interactive histogram. The
        # histogram itself IS the slider — the user drags its vertical
        # marker to set the threshold.
        corner = QtWidgets.QHBoxLayout()
        corner.setSpacing(6)
        self._lbl_corner = QtWidgets.QLabel(tr("es_lbl_corner_angle"))
        self._lbl_corner.setStyleSheet("color:#AAA;font-size:10px")
        corner.addWidget(self._lbl_corner)
        self._lbl_corner_val = QtWidgets.QLabel(u"60\u00B0")
        self._lbl_corner_val.setStyleSheet(
            "color:#FF9800;font-size:11px;font-weight:bold;min-width:36px")
        corner.addWidget(self._lbl_corner_val)
        self._lbl_corner_hint = QtWidgets.QLabel(tr("es_lbl_corner_hint"))
        self._lbl_corner_hint.setStyleSheet(
            "color:#777;font-size:9px;padding:0 4px")
        self._lbl_corner_hint.setWordWrap(True)
        corner.addWidget(self._lbl_corner_hint, 1)
        corner.addStretch()
        lo.addLayout(corner)

        # Interactive histogram of bend angles. Drag the orange marker
        # horizontally to change the threshold; clicking anywhere on
        # the chart jumps the marker there.
        self._angle_histogram = _EsAngleHistogram()
        self._angle_histogram.setFixedHeight(54)
        self._angle_histogram.setStyleSheet(
            "QWidget{background-color:#1A1A1A;border-radius:3px}")
        self._angle_histogram.threshold_changed.connect(
            self._on_histogram_threshold_changed)
        lo.addWidget(self._angle_histogram)

        # Pair table.
        self._table = QtWidgets.QTableWidget(0, 6)
        self._update_headers()
        h = self._table.horizontalHeader()
        self._table.setColumnWidth(0, 42)
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self._table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self._table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(22)
        self._table.setStyleSheet(_ES_TABLE_SS)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        lo.addWidget(self._table, 1)

        # Direction buttons row. Each button applies the uniform
        # target length to the currently selected rows (or all rows
        # if nothing is selected), with different anchor behaviour:
        #   Align-to-A : keep A endpoint, move B to exactly length away
        #   Align-to-B : keep B endpoint, move A to exactly length away
        #   Centre     : keep midpoint, scale both endpoints symmetrically
        dr = QtWidgets.QHBoxLayout()
        dr.setSpacing(4)
        self._btn_to_a = _mkbtn(tr("es_btn_align_a"), 26,
                                 "#2196F3", "#1976D2", fs=10)
        self._btn_to_a.clicked.connect(lambda: self._on_uniform_apply(0))
        dr.addWidget(self._btn_to_a)
        self._btn_to_b = _mkbtn(tr("es_btn_align_b"), 26,
                                 "#FF9800", "#F57C00", fs=10)
        self._btn_to_b.clicked.connect(lambda: self._on_uniform_apply(1))
        dr.addWidget(self._btn_to_b)
        self._btn_mid = _mkbtn(tr("es_btn_align_mid"), 26,
                                "#9C27B0", "#7B1FA2", fs=10)
        self._btn_mid.clicked.connect(lambda: self._on_uniform_apply(2))
        dr.addWidget(self._btn_mid)
        dr.addStretch()
        lo.addLayout(dr)

        # Confirm / revert / close.
        cr = QtWidgets.QHBoxLayout()
        cr.setSpacing(4)
        self._btn_confirm = _mkbtn(tr("es_btn_confirm"), 26,
                                    "#4CAF50", "#388E3C", fs=10)
        self._btn_confirm.clicked.connect(self._on_confirm)
        self._btn_confirm.setEnabled(False)
        cr.addWidget(self._btn_confirm)
        self._btn_revert = _mkbtn(tr("es_btn_revert"), 26,
                                   "#F44336", "#D32F2F", fs=10)
        self._btn_revert.clicked.connect(self._on_revert)
        self._btn_revert.setEnabled(False)
        cr.addWidget(self._btn_revert)
        cr.addStretch()
        self._btn_close = _mkbtn(tr("btn_close"), 26, "#555", "#444", fs=10)
        self._btn_close.clicked.connect(self.hide)
        cr.addWidget(self._btn_close)
        lo.addLayout(cr)

    def _update_headers(self):
        self._table.setHorizontalHeaderLabels([
            u"",
            tr("es_col_edge"),
            tr("es_col_length"),
            tr("es_col_region"),
            tr("es_col_status"),
            tr("es_col_log"),
        ])

    # -- Data setup --
    def set_data(self, edges):
        self._edges = list(edges)
        self._status = _es_bipartite_assign(self._edges)
        self._components = _es_compute_ring_components(
            self._edges, self._corner_angle)
        self._brim_data = None     # recomputed lazily when belt mode enabled
        self._snap_log = {}
        self._close_undo()
        # If belt mode is currently enabled, re-detect brims for the
        # new selection right away so the user sees correct values.
        if self._belt_mode:
            self._ensure_brim_data()
        # Feed the histogram widget with the current angles.
        self._update_histogram()
        self._refresh_scope_and_average()
        self._populate()
        self._update_confirm_state()

    def _update_histogram(self):
        """Recompute the bend-angle list for the current selection
        and push it into the histogram widget."""
        if not hasattr(self, "_angle_histogram"):
            return
        if not self._edges:
            self._angle_histogram.set_angles([])
            self._angle_histogram.set_threshold(self._corner_angle)
            return
        pairs = _es_compute_adjacency_pairs(self._edges)
        self._angle_histogram.set_angles([p[2] for p in pairs])
        self._angle_histogram.set_threshold(self._corner_angle)

    def _ensure_brim_data(self):
        """Compute brim polylines for the current selection if we
        haven't already for this edge-set."""
        if self._brim_data is not None:
            return
        if not self._edges:
            self._brim_data = {"brim_a_verts": {},
                                "brim_b_verts": {}}
            return
        self._brim_data = _es_detect_belt_brims(self._edges)

    def _on_mode_changed(self, _checked=False):
        """Handle toggle between simple length and belt-width modes."""
        new_belt = self._rb_mode_belt.isChecked()
        if new_belt == self._belt_mode:
            return
        self._belt_mode = new_belt
        if self._belt_mode:
            self._ensure_brim_data()
        self._refresh_scope_and_average()
        self._populate()
        self.status_msg.emit(
            tr("es_status_mode_belt") if self._belt_mode
            else tr("es_status_mode_length"))

    def _refresh_scope_and_average(self):
        """Recompute scope line + suggested target width + region chips.

        When the edges span multiple regions, we pick the largest
        region and use its average as the target width. Short corner
        regions therefore don't drag the default down.
        """
        n = len(self._edges)
        n_bad = sum(1 for s in self._status if s != "ok")
        n_regions = (max(self._components) + 1
                      if self._components else 0)

        # Build the text scope line.
        parts = []
        if n_bad > 0:
            parts.append(tr("es_scope_with_warn", count=n, warn=n_bad))
        else:
            parts.append(tr("es_scope", count=n))
        if n_regions > 1:
            parts.append(tr("es_scope_region_count", regions=n_regions))
        self._scope_lbl.setText(u"   |   ".join(parts))

        # Rebuild the clickable region chip strip.
        self._rebuild_region_chips()
        if hasattr(self, "_region_chip_wrapper"):
            self._region_chip_wrapper.setVisible(n_regions > 0)

        # Compute "default target width" from the largest region.
        target = self._largest_region_average()
        if target is not None:
            self._spin_uniform.blockSignals(True)
            try:
                self._spin_uniform.setValue(target)
            finally:
                self._spin_uniform.blockSignals(False)

    def _rebuild_region_chips(self):
        """Populate the region chip strip with one clickable QPushButton
        per region. Clicking a chip selects that region's rows in the
        table and loads its average into the target-width spinbox.
        """
        if not hasattr(self, "_region_chip_layout"):
            return
        # Remove any existing chip buttons first.
        for btn in self._region_chip_buttons:
            try:
                self._region_chip_layout.removeWidget(btn)
                btn.setParent(None)
                btn.deleteLater()
            except Exception:
                pass
        self._region_chip_buttons = []

        if not self._edges:
            self._region_chip_placeholder.setText(u"")
            return

        def _metric_for_chip(i, edge):
            if self._belt_mode and self._brim_data:
                a = self._brim_data["brim_a_verts"].get(i, [])
                b = self._brim_data["brim_b_verts"].get(i, [])
                w = _es_belt_width_from_rung(
                    edge["a_pos"], edge["b_pos"], a, b)
                if w is not None:
                    return w
            return _es_edge_length(edge)

        by_comp = {}
        for i, e in enumerate(self._edges):
            cid = self._components[i] if i < len(self._components) else 0
            by_comp.setdefault(cid, []).append((i, _metric_for_chip(i, e)))
        if not by_comp:
            self._region_chip_placeholder.setText(u"")
            return

        # Placeholder text acts as a compact header ("Region:").
        self._region_chip_placeholder.setText(tr("es_chip_header"))

        # Each chip goes before the trailing stretch + select-all button,
        # so we insert at index 1 (just after the placeholder label) for
        # each new chip in order.
        insert_at = 1
        for cid in sorted(by_comp.keys()):
            rows_lens = by_comp[cid]
            if not rows_lens:
                continue
            lens = [ln for _, ln in rows_lens]
            avg = sum(lens) / float(len(lens))
            col = _ES_REGION_COLOURS[cid % len(_ES_REGION_COLOURS)]
            text = tr("es_chip_label",
                      cid=cid + 1, n=len(lens),
                      avg=u"{0:.4f}".format(avg))
            btn = QtWidgets.QPushButton(text)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton{{"
                "background-color:{bg};color:#222;"
                "padding:2px 8px;border:1px solid {brd};"
                "border-radius:10px;font-size:10px;font-weight:bold}}"
                "QPushButton:hover{{background-color:{hov}}}"
                .format(bg=col, brd=col, hov=_es_darken(col)))
            # Capture cid in default-arg so the lambda closes over the
            # current value (Python late-binding guard).
            btn.clicked.connect(
                lambda _chk=False, c=cid: self._on_region_chip_clicked(c))
            self._region_chip_layout.insertWidget(insert_at, btn)
            insert_at += 1
            self._region_chip_buttons.append(btn)

    def _on_region_chip_clicked(self, cid):
        """Select only the rows belonging to region `cid` and load that
        region's average width into the target-width spinbox."""
        rows_in_region = [i for i, c in enumerate(self._components)
                           if c == cid]
        if not rows_in_region:
            return
        # Select those rows in the table.
        self._table.blockSignals(True)
        try:
            self._table.clearSelection()
            sel_model = self._table.selectionModel()
            mode = (QtCore.QItemSelectionModel.Select
                    | QtCore.QItemSelectionModel.Rows)
            for r in rows_in_region:
                idx = self._table.model().index(r, 0)
                sel_model.select(idx, mode)
        finally:
            self._table.blockSignals(False)
        # Sync Maya selection to match.
        if MAYA_AVAILABLE:
            try:
                comps = [self._edges[r]["edge"] for r in rows_in_region]
                cmds.select(comps, r=True)
            except Exception:
                pass
        # Load that region's average width into the spin.
        def _chip_metric(r):
            edge = self._edges[r]
            if self._belt_mode and self._brim_data:
                a = self._brim_data["brim_a_verts"].get(r, [])
                b = self._brim_data["brim_b_verts"].get(r, [])
                w = _es_belt_width_from_rung(
                    edge["a_pos"], edge["b_pos"], a, b)
                if w is not None:
                    return w
            return _es_edge_length(edge)
        lens = [_chip_metric(r) for r in rows_in_region]
        if lens:
            avg = sum(lens) / float(len(lens))
            self._spin_uniform.blockSignals(True)
            try:
                self._spin_uniform.setValue(avg)
            finally:
                self._spin_uniform.blockSignals(False)
        self.status_msg.emit(
            tr("es_status_region_selected",
                cid=cid + 1, count=len(rows_in_region),
                avg=u"{0:.4f}".format(
                    sum(lens) / float(len(lens)) if lens else 0.0)))

    def _on_select_all_rows(self):
        """Select every row in the table so direction buttons operate
        on the entire selection again."""
        if not self._edges:
            return
        self._table.blockSignals(True)
        try:
            self._table.clearSelection()
            sel_model = self._table.selectionModel()
            mode = (QtCore.QItemSelectionModel.Select
                    | QtCore.QItemSelectionModel.Rows)
            for r in range(len(self._edges)):
                idx = self._table.model().index(r, 0)
                sel_model.select(idx, mode)
        finally:
            self._table.blockSignals(False)
        if MAYA_AVAILABLE:
            try:
                comps = [e["edge"] for e in self._edges]
                cmds.select(comps, r=True)
            except Exception:
                pass
        # Restore target width to the largest region's average.
        target = self._largest_region_average()
        if target is not None:
            self._spin_uniform.blockSignals(True)
            try:
                self._spin_uniform.setValue(target)
            finally:
                self._spin_uniform.blockSignals(False)

    def _largest_region_average(self):
        if not self._edges:
            return None
        # Group lengths by component id, using belt-width metric if
        # belt mode is on (otherwise simple edge length).
        def _metric(i, edge):
            if self._belt_mode and self._brim_data:
                a = self._brim_data["brim_a_verts"].get(i, [])
                b = self._brim_data["brim_b_verts"].get(i, [])
                w = _es_belt_width_from_rung(
                    edge["a_pos"], edge["b_pos"], a, b)
                if w is not None:
                    return w
            return _es_edge_length(edge)
        by_comp = {}
        for i, e in enumerate(self._edges):
            cid = self._components[i] if i < len(self._components) else 0
            by_comp.setdefault(cid, []).append(_metric(i, e))
        if not by_comp:
            return None
        # Pick the component with the most edges (ties: highest total
        # length) so short corner regions don't drive the default.
        best_cid = max(by_comp.keys(),
                       key=lambda c: (len(by_comp[c]), sum(by_comp[c])))
        lens = by_comp[best_cid]
        if not lens:
            return None
        return sum(lens) / float(len(lens))

    def _populate(self):
        self._table.blockSignals(True)
        try:
            self._table.setRowCount(len(self._edges))
            for r, e in enumerate(self._edges):
                status = self._status[r]
                log = self._snap_log.get(e["edge"], "")
                cid = self._components[r] if r < len(self._components) else 0
                col = _ES_REGION_COLOURS[cid % len(_ES_REGION_COLOURS)]
                # Make a faint tinted background from the region colour
                # so each region paints visibly as a horizontal band.
                qcol = QtGui.QColor(col)
                tinted = QtGui.QColor(qcol.red(), qcol.green(), qcol.blue(), 60)
                bg_brush = QtGui.QBrush(tinted)
                fg_qcol = QtGui.QColor(col)

                # Col 0: snap mark (✓ if already snapped).
                mark = u"\u2714" if log else u""
                item = QtWidgets.QTableWidgetItem(mark)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                if log:
                    item.setForeground(QtGui.QColor("#4CAF50"))
                item.setBackground(bg_brush)
                self._table.setItem(r, 0, item)

                # Col 1: short edge name.
                short = e["edge"].split("|")[-1]
                item = QtWidgets.QTableWidgetItem(short)
                item.setBackground(bg_brush)
                self._table.setItem(r, 1, item)

                # Col 2: current length (or belt-width if belt mode).
                if self._belt_mode and self._brim_data:
                    brim_a = self._brim_data["brim_a_verts"].get(r, [])
                    brim_b = self._brim_data["brim_b_verts"].get(r, [])
                    w = _es_belt_width_from_rung(
                        e["a_pos"], e["b_pos"], brim_a, brim_b)
                    cur_len = w if w is not None else _es_edge_length(e)
                else:
                    cur_len = _es_edge_length(e)
                item = QtWidgets.QTableWidgetItem(
                    u"{0:.4f}".format(cur_len))
                item.setTextAlignment(QtCore.Qt.AlignRight
                                       | QtCore.Qt.AlignVCenter)
                item.setBackground(bg_brush)
                self._table.setItem(r, 2, item)

                # Col 3: region id (1-based for display) with full-
                # strength colour on the text for maximum scan-ability.
                region_item = QtWidgets.QTableWidgetItem(
                    u"#{0}".format(cid + 1))
                region_item.setTextAlignment(QtCore.Qt.AlignCenter)
                region_item.setForeground(fg_qcol)
                region_item.setBackground(bg_brush)
                f = region_item.font()
                f.setBold(True)
                region_item.setFont(f)
                self._table.setItem(r, 3, region_item)

                # Col 4: bipartite status.
                st_txt = (tr("es_status_ok") if status == "ok"
                          else tr("es_status_fallback"))
                item = QtWidgets.QTableWidgetItem(st_txt)
                if status != "ok":
                    item.setForeground(QtGui.QColor("#FF9800"))
                item.setBackground(bg_brush)
                self._table.setItem(r, 4, item)

                # Col 5: snap log.
                item = QtWidgets.QTableWidgetItem(log)
                item.setBackground(bg_brush)
                self._table.setItem(r, 5, item)
        finally:
            self._table.blockSignals(False)

    # -- Interaction --
    def _on_histogram_threshold_changed(self, val):
        """Fired while the user drags the histogram marker."""
        # Round to the nearest integer degree for stability of the
        # displayed value and to avoid spamming recomputations.
        new_deg = round(float(val))
        if abs(new_deg - self._corner_angle) < 0.5:
            # Still update the live label so drag feels responsive.
            self._lbl_corner_val.setText(
                u"{0}\u00B0".format(int(round(self._corner_angle))))
            return
        self._corner_angle = float(new_deg)
        self._lbl_corner_val.setText(
            u"{0}\u00B0".format(int(new_deg)))
        if not self._edges:
            return
        # Recompute ring components with the new threshold and refresh
        # table + chips so the user sees which rows moved.
        self._components = _es_compute_ring_components(
            self._edges, self._corner_angle)
        self._refresh_scope_and_average()
        self._populate()

    # Backwards compatibility in case anything else still calls this.
    def _on_corner_angle_changed(self, val):
        self._on_histogram_threshold_changed(val)

    def _on_selection_changed(self):
        if not MAYA_AVAILABLE:
            return
        rows = sorted(set(i.row()
                           for i in self._table.selectionModel().selectedRows()))
        if not rows:
            return
        comps = []
        for r in rows:
            if r < len(self._edges):
                comps.append(self._edges[r]["edge"])
        if comps:
            try:
                cmds.select(comps, r=True)
            except Exception:
                pass

    def _ensure_undo_open(self):
        if not self._undo_open:
            cmds.undoInfo(openChunk=True, chunkName="DW_EdgeSnap")
            self._undo_open = True

    def _selected_rows(self):
        rows = sorted(set(i.row()
                           for i in self._table.selectionModel().selectedRows()))
        return rows

    def _on_uniform_apply(self, anchor):
        """Apply the uniform target length to the selected (or all)
        edges, anchored as specified.

        anchor:
            0 = keep A, move B   (Align-to-A)
            1 = keep B, move A   (Align-to-B)
            2 = keep midpoint    (Centre)

        If the "per-region" checkbox is ticked, each edge uses the
        average length of its own smooth-region (computed from the
        corner-angle slider). Otherwise the spinbox value is used as
        a single global target for every row.

        When belt-width mode is active, "length" means the straight
        chord distance between the rung's endpoint projections onto
        the two brim edge loops, and the moving endpoint is slid
        ALONG its brim rather than along the rung direction.
        """
        if not MAYA_AVAILABLE:
            return
        rows = self._selected_rows()
        if not rows:
            # No selection → apply to all rows.
            rows = list(range(len(self._edges)))
        if not rows:
            self.status_msg.emit(tr("es_status_no_sel"))
            return

        per_region = (getattr(self, "_cb_per_region", None) is not None
                      and self._cb_per_region.isChecked())

        # Pick the width metric: simple edge length, or belt-width.
        def _edge_metric(ei, edge):
            if self._belt_mode and self._brim_data:
                brim_a = self._brim_data["brim_a_verts"].get(ei, [])
                brim_b = self._brim_data["brim_b_verts"].get(ei, [])
                w = _es_belt_width_from_rung(
                    edge["a_pos"], edge["b_pos"], brim_a, brim_b)
                if w is not None:
                    return w
            return _es_edge_length(edge)

        # Pre-compute per-region averages (once per call).
        region_avg = {}
        if per_region and self._components:
            region_lens = {}
            for i, e in enumerate(self._edges):
                cid = self._components[i] if i < len(self._components) else 0
                region_lens.setdefault(cid, []).append(_edge_metric(i, e))
            for cid, lens in region_lens.items():
                if lens:
                    region_avg[cid] = sum(lens) / float(len(lens))

        global_target = float(self._spin_uniform.value())
        if not per_region and global_target <= 0:
            self.status_msg.emit(tr("es_status_bad_length"))
            return

        self._ensure_undo_open()
        if anchor == 0:
            anchor_label = tr("es_log_align_a")
        elif anchor == 1:
            anchor_label = tr("es_log_align_b")
        else:
            anchor_label = tr("es_log_align_mid")
        for r in rows:
            if r >= len(self._edges):
                continue
            e = self._edges[r]
            # Resolve this edge's target length.
            if per_region:
                cid = self._components[r] if r < len(self._components) else 0
                target = region_avg.get(cid, global_target)
            else:
                target = global_target
            if target <= 0:
                continue
            if self._belt_mode and self._brim_data:
                brim_a = self._brim_data["brim_a_verts"].get(r, [])
                brim_b = self._brim_data["brim_b_verts"].get(r, [])
                _es_snap_belt_rung_to_width(
                    e, target, anchor, brim_a, brim_b)
            else:
                _es_snap_edge_to_length(e, target, anchor)
            self._snap_log[e["edge"]] = tr(
                "es_log_uniform_with_anchor",
                anchor=anchor_label,
                value=u"{0:.4f}".format(target))
        self._refresh_positions()
        self._populate()
        self._update_confirm_state()
        self.status_msg.emit(tr("es_status_snapped",
                                  count=len(self._snap_log)))

    def _refresh_positions(self):
        """Re-read world-space positions after a snap so length column
        reflects the latest state."""
        if not MAYA_AVAILABLE:
            return
        for e in self._edges:
            try:
                p0 = cmds.pointPosition(
                    u"{0}.vtx[{1}]".format(e["shape"], e["a_idx"]), w=True)
                p1 = cmds.pointPosition(
                    u"{0}.vtx[{1}]".format(e["shape"], e["b_idx"]), w=True)
                e["a_pos"] = (p0[0], p0[1], p0[2])
                e["b_pos"] = (p1[0], p1[1], p1[2])
            except Exception:
                pass

    # -- Confirm / Revert --
    def _on_confirm(self):
        n = len(self._snap_log)
        self._close_undo()
        self._snap_log = {}
        self._update_confirm_state()
        self._populate()
        self.status_msg.emit(tr("es_status_confirmed", count=n))

    def _on_revert(self):
        self._close_undo()
        if MAYA_AVAILABLE:
            try:
                cmds.undo()
            except Exception:
                pass
        self._snap_log = {}
        self._refresh_positions()
        self._update_confirm_state()
        self._populate()
        self.status_msg.emit(tr("es_status_reverted"))

    def _close_undo(self):
        if self._undo_open:
            try:
                cmds.undoInfo(closeChunk=True)
            except Exception:
                pass
            self._undo_open = False

    def _update_confirm_state(self):
        has_log = len(self._snap_log) > 0
        self._btn_confirm.setEnabled(has_log)
        self._btn_revert.setEnabled(has_log)

    # -- Language refresh --
    def refresh_labels(self):
        self.setWindowTitle(tr("es_result_title"))
        self._lbl_mode.setText(tr("es_lbl_mode"))
        self._rb_mode_length.setText(tr("es_mode_length"))
        self._rb_mode_belt.setText(tr("es_mode_belt"))
        self._lbl_mode_hint.setText(tr("es_lbl_mode_hint"))
        self._lbl_uniform.setText(tr("es_lbl_uniform"))
        self._lbl_uniform_hint.setText(tr("es_lbl_uniform_hint"))
        self._cb_per_region.setText(tr("es_chk_per_region"))
        self._cb_per_region.setToolTip(tr("es_chk_per_region_tip"))
        self._lbl_corner.setText(tr("es_lbl_corner_angle"))
        self._lbl_corner_hint.setText(tr("es_lbl_corner_hint"))
        self._btn_to_a.setText(tr("es_btn_align_a"))
        self._btn_to_b.setText(tr("es_btn_align_b"))
        self._btn_mid.setText(tr("es_btn_align_mid"))
        self._btn_confirm.setText(tr("es_btn_confirm"))
        self._btn_revert.setText(tr("es_btn_revert"))
        self._btn_close.setText(tr("btn_close"))
        if hasattr(self, "_btn_select_all"):
            self._btn_select_all.setText(tr("es_btn_select_all"))
        self._update_headers()
        # Rebuild chip labels to pick up the new language.
        self._rebuild_region_chips()

    def closeEvent(self, event):
        # Auto-revert uncommitted snaps when the dialog closes.
        if self._undo_open:
            self._close_undo()
            if MAYA_AVAILABLE:
                try:
                    cmds.undo()
                except Exception:
                    pass
        super(EdgeSnapResultWindow, self).closeEvent(event)


# ---------------------------------------------------------------------------
# Edge Snap: tab-side launcher + plumbing
# ---------------------------------------------------------------------------

class _EdgeModeButton(QtWidgets.QAbstractButton):
    """Small icon toggle button for Ring / Loop expansion mode.

    Draws a stylised cylinder with one edge direction highlighted:
      * "ring"  — horizontal belt around the cylinder (orange loop)
      * "loop"  — vertical line running down the cylinder (orange stripe)

    The cylinder silhouette stays visible in both states so the user
    sees "same object, different edge direction highlighted".
    Checked state swaps the frame/background to an orange tint to
    match the Edge Width Alignment group's accent colour.
    """

    _SIZE = 44   # square px — bigger so the cylinder icon reads well

    def __init__(self, orientation="ring", tooltip=u"", parent=None):
        super(_EdgeModeButton, self).__init__(parent)
        self._orient = orientation   # "ring" or "loop"
        self.setCheckable(True)
        self.setFixedSize(self._SIZE, self._SIZE)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setToolTip(tooltip)

    def sizeHint(self):
        return QtCore.QSize(self._SIZE, self._SIZE)

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)

        checked = self.isChecked()
        hover = self.underMouse()

        # Frame / background of the button itself.
        if checked:
            bg = QtGui.QColor("#FF9800")
            frame = QtGui.QColor("#F57C00")
        else:
            bg = QtGui.QColor("#4A4A4A") if hover else QtGui.QColor("#3C3C3C")
            frame = QtGui.QColor("#666")
        p.setPen(QtGui.QPen(frame, 1))
        p.setBrush(bg)
        p.drawRoundedRect(1, 1, self._SIZE - 2, self._SIZE - 2, 5, 5)

        # Colours for the cylinder shape.
        if checked:
            outline = QtGui.QColor("#5A3A00")
            body    = QtGui.QColor("#FFF5E0")   # light cream body
            hi      = QtGui.QColor("#E65100")   # darker orange for highlight
        else:
            outline = QtGui.QColor("#AAA")
            body    = QtGui.QColor("#2B2B2B")
            hi      = QtGui.QColor("#FF9800")   # orange highlight when inactive

        # Cylinder geometry: centred vertically, taller than wide.
        cx = self._SIZE / 2.0
        cyl_w = self._SIZE * 0.40            # body width
        cyl_h = self._SIZE * 0.70            # total cylinder height
        ell_h = self._SIZE * 0.16            # ellipse cap height
        cy_top = (self._SIZE - cyl_h) / 2.0
        cy_bot = cy_top + cyl_h
        left = cx - cyl_w / 2.0
        right = cx + cyl_w / 2.0

        # Body rect (the side walls area).
        side_pen = QtGui.QPen(outline, 1)
        p.setPen(side_pen)
        p.setBrush(body)
        # Fill the body as a plain rectangle first, then overlay
        # the two ellipse caps so the outline reads correctly.
        p.drawRect(QtCore.QRectF(left, cy_top + ell_h / 2.0,
                                  cyl_w, cyl_h - ell_h))
        # Left and right side verticals.
        p.drawLine(QtCore.QPointF(left,  cy_top + ell_h / 2.0),
                   QtCore.QPointF(left,  cy_bot - ell_h / 2.0))
        p.drawLine(QtCore.QPointF(right, cy_top + ell_h / 2.0),
                   QtCore.QPointF(right, cy_bot - ell_h / 2.0))

        # Bottom cap (full ellipse).
        p.setBrush(body)
        p.drawEllipse(QtCore.QRectF(left, cy_bot - ell_h,
                                     cyl_w, ell_h))

        # Top cap (ellipse).
        p.drawEllipse(QtCore.QRectF(left, cy_top, cyl_w, ell_h))

        # Highlight stroke on top of everything.
        hi_pen = QtGui.QPen(hi, 2.2)
        hi_pen.setCapStyle(QtCore.Qt.RoundCap)
        p.setPen(hi_pen)
        p.setBrush(QtCore.Qt.NoBrush)

        if self._orient == "ring":
            # A horizontal "belt" — a full ellipse around the cylinder
            # middle. This unambiguously reads as "ring".
            mid_y = cy_top + cyl_h * 0.55
            belt_rect = QtCore.QRectF(left, mid_y - ell_h / 2.0,
                                        cyl_w, ell_h)
            p.drawEllipse(belt_rect)
        else:
            # A vertical stripe — a line running top-to-bottom on the
            # cylinder's centre. This reads as "loop" (perpendicular
            # to the ring).
            stripe_x = cx
            stripe_top = cy_top + ell_h / 2.0
            stripe_bot = cy_bot - ell_h / 2.0
            p.drawLine(QtCore.QPointF(stripe_x, stripe_top),
                       QtCore.QPointF(stripe_x, stripe_bot))

        p.end()


def _build_edge_snap_group(tool_window, parent_layout):
    """Build the Edge Snap group for the Snap tab."""
    grp = QtWidgets.QGroupBox()
    grp.setStyleSheet(
        "QGroupBox{border:1px solid #FF9800;border-radius:6px;"
        "background-color:#2E2E2E;margin-top:6px}"
        "QGroupBox::title{subcontrol-origin:margin;left:10px;"
        "color:#EEE;font-size:11px;font-weight:bold}")
    lo = QtWidgets.QVBoxLayout(grp)
    lo.setContentsMargins(6, 10, 6, 6)
    lo.setSpacing(4)

    hdr = QtWidgets.QHBoxLayout()
    tool_window._es_grp_lbl = QtWidgets.QLabel(
        u"\u25A0 " + tr("es_grp_title"))
    tool_window._es_grp_lbl.setStyleSheet(
        "color:#FF9800;font-size:11px;font-weight:bold")
    hdr.addWidget(tool_window._es_grp_lbl)
    hdr.addStretch()
    tool_window._es_btn_launch = _mkbtn(
        tr("es_btn_launch"), 24, "#FF9800", "#F57C00", fs=10)
    tool_window._es_btn_launch.clicked.connect(
        lambda: _es_launch(tool_window))
    hdr.addWidget(tool_window._es_btn_launch)
    lo.addLayout(hdr)

    tool_window._es_desc_lbl = QtWidgets.QLabel(tr("es_grp_desc"))
    tool_window._es_desc_lbl.setStyleSheet(
        "color:#AAA;font-size:10px;padding:2px 4px")
    tool_window._es_desc_lbl.setWordWrap(True)
    lo.addWidget(tool_window._es_desc_lbl)

    # Auto-expand mode: Ring (belt direction, default) vs Loop.
    # Only matters when the user selects exactly one edge before
    # clicking Launch; both radios are ignored when 2+ edges are
    # already selected.
    mode_row = QtWidgets.QHBoxLayout()
    mode_row.setContentsMargins(4, 0, 4, 0)
    mode_row.setSpacing(8)
    tool_window._es_mode_lbl = QtWidgets.QLabel(tr("es_lbl_expand_mode"))
    tool_window._es_mode_lbl.setStyleSheet(
        "color:#AAA;font-size:10px")
    mode_row.addWidget(tool_window._es_mode_lbl)

    # Icon-driven toggle buttons. Ring = horizontal lines (belt);
    # Loop = vertical lines (perpendicular). Paint directly so we
    # get crisp icons at any DPI without shipping image files.
    tool_window._es_btn_ring = _EdgeModeButton(
        orientation="ring", tooltip=tr("es_mode_ring"))
    tool_window._es_btn_ring.setChecked(True)
    mode_row.addWidget(tool_window._es_btn_ring)
    tool_window._es_btn_loop = _EdgeModeButton(
        orientation="loop", tooltip=tr("es_mode_loop"))
    mode_row.addWidget(tool_window._es_btn_loop)

    # Mutex group — exactly one selected at a time.
    tool_window._es_mode_group = QtWidgets.QButtonGroup(tool_window)
    tool_window._es_mode_group.setExclusive(True)
    tool_window._es_mode_group.addButton(tool_window._es_btn_ring, 0)
    tool_window._es_mode_group.addButton(tool_window._es_btn_loop, 1)

    mode_row.addStretch()
    lo.addLayout(mode_row)

    tool_window._es_result_window = None
    parent_layout.addWidget(grp)
    return grp


def _es_launch(tool_window):
    """Collect selected edges, open/refresh the result window."""
    # Pick the expand mode from the icon buttons.
    mode = "ring"
    if getattr(tool_window, "_es_btn_loop", None) is not None \
            and tool_window._es_btn_loop.isChecked():
        mode = "loop"
    edges = _es_get_selected_edges(expand_mode=mode)
    if not edges:
        if hasattr(tool_window, "_status_bar"):
            tool_window._status_bar.setText(tr("es_status_no_edges"))
        return

    if tool_window._es_result_window is None:
        tool_window._es_result_window = EdgeSnapResultWindow(
            parent=tool_window)
        tool_window._es_result_window.status_msg.connect(
            lambda t: tool_window._status_bar.setText(t)
            if hasattr(tool_window, "_status_bar") else None)

    tool_window._es_result_window.set_data(edges)
    tool_window._es_result_window.show()
    tool_window._es_result_window.raise_()
    tool_window._es_result_window.activateWindow()


def _es_refresh_labels(tool_window):
    """Called from CollisionCheckToolWindow._refresh_labels()."""
    if hasattr(tool_window, "_es_grp_lbl"):
        tool_window._es_grp_lbl.setText(u"\u25A0 " + tr("es_grp_title"))
    if hasattr(tool_window, "_es_btn_launch"):
        tool_window._es_btn_launch.setText(tr("es_btn_launch"))
    if hasattr(tool_window, "_es_desc_lbl"):
        tool_window._es_desc_lbl.setText(tr("es_grp_desc"))
    if hasattr(tool_window, "_es_mode_lbl"):
        tool_window._es_mode_lbl.setText(tr("es_lbl_expand_mode"))
    if hasattr(tool_window, "_es_btn_ring"):
        tool_window._es_btn_ring.setToolTip(tr("es_mode_ring"))
    if hasattr(tool_window, "_es_btn_loop"):
        tool_window._es_btn_loop.setToolTip(tr("es_mode_loop"))
    w = getattr(tool_window, "_es_result_window", None)
    if w is not None:
        w.refresh_labels()


def _es_close_result_window(tool_window):
    """Called from CollisionCheckToolWindow close/reload."""
    w = getattr(tool_window, "_es_result_window", None)
    if w is not None:
        try:
            w.close()
        except Exception:
            pass
# -*- coding: utf-8 -*-
# ============================================================================
# 0380_vertex_align.txt
# Vertex Align feature for DW_CollisionCheck "Alignment" tab.
#
# Ported/simplified from AriStraightVertex (MEL, by Ari / cgjishu.net).
# Offers three modes:
#   * Linear 3D  — project selected verts onto the straight line through
#                  two reference points (auto-detected from selection
#                  end-points, or taken from edge selection), with an
#                  optional "equidistant" spacing for edge selections.
#   * Linear 2D  — project selected verts onto a line in one of the
#                  orthographic views (Top / Front / Side), preserving
#                  the axis perpendicular to the view.
#   * Flatten    — project selected verts onto the plane defined by
#                  three reference points.
#
# Dialog is modeled on Face Snap: preview → confirm / revert, all
# wrapped in a single undo chunk so the user can iterate safely.
#
# Depends on (defined earlier in the concatenated build):
#   VERSION, PY2, MAYA_AVAILABLE, cmds,
#   QtCore, QtGui, QtWidgets,
#   tr(), _STRINGS,
#   _mkbtn()
# ============================================================================


import math as _va_math


# ---------------------------------------------------------------------------
# Vertex Align: math helpers
# ---------------------------------------------------------------------------

def _va_project_point_on_line(a1, a2, p):
    """Foot of perpendicular from p onto the infinite line through a1-a2."""
    ax = a2[0] - a1[0]; ay = a2[1] - a1[1]; az = a2[2] - a1[2]
    denom = ax * ax + ay * ay + az * az
    if denom < 1.0e-18:
        return (a1[0], a1[1], a1[2])
    t = ((p[0] - a1[0]) * ax
         + (p[1] - a1[1]) * ay
         + (p[2] - a1[2]) * az) / denom
    return (a1[0] + ax * t,
            a1[1] + ay * t,
            a1[2] + az * t)


def _va_project_point_on_plane(a, b, c, p):
    """Orthogonal projection of p onto the plane through a, b, c."""
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    nm = (ab[1] * ac[2] - ab[2] * ac[1],
          ab[2] * ac[0] - ab[0] * ac[2],
          ab[0] * ac[1] - ab[1] * ac[0])
    nl2 = nm[0] * nm[0] + nm[1] * nm[1] + nm[2] * nm[2]
    if nl2 < 1.0e-18:
        return (p[0], p[1], p[2])
    ap = (p[0] - a[0], p[1] - a[1], p[2] - a[2])
    d  = (ap[0] * nm[0] + ap[1] * nm[1] + ap[2] * nm[2]) / nl2
    return (p[0] - nm[0] * d,
            p[1] - nm[1] * d,
            p[2] - nm[2] * d)


def _va_lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _va_project_line_2d(a1, a2, p, view_mode, drop_mode):
    """2-D projection helpers for the "Linear 2D" mode.

    view_mode: "top" | "front" | "side"
        Top   : work in the X/Z plane; Y stays put.
        Front : work in the X/Y plane; Z stays put.
        Side  : work in the Z/Y plane; X stays put.

    drop_mode: "shortest" | "horizontal" | "vertical"
        shortest  — drop perpendicular from p onto the 2-D line.
        horizontal — keep the view's vertical coordinate; find the
                     matching horizontal coordinate on the line.
        vertical  — keep the view's horizontal coordinate; find the
                     matching vertical coordinate on the line.

    Returns a new (x, y, z) for p.
    """
    if view_mode == "top":
        xi, yi = 0, 2           # horizontal = X, vertical = Z
        keep = 1                 # keep Y
    elif view_mode == "side":
        xi, yi = 2, 1
        keep = 0
    else:                          # "front"
        xi, yi = 0, 1
        keep = 2

    x1 = a1[xi]; y1 = a1[yi]
    x2 = a2[xi]; y2 = a2[yi]
    px = p[xi];  py = p[yi]

    dx = x2 - x1
    dy = y2 - y1
    vertical_line = abs(dx) < 1.0e-9     # line is pure x = const
    if not vertical_line:
        slope = dy / dx
        intercept = y2 - slope * x2
    else:
        slope = None
        intercept = None

    if drop_mode == "vertical":
        # Keep horizontal (x) coordinate of p. Find y on the line.
        if vertical_line:
            # Line has no y=f(x), but the user wants to move p
            # vertically — just snap x to the line's fixed x.
            new_x = x1
            new_y = py
        else:
            new_x = px
            new_y = slope * px + intercept
    elif drop_mode == "horizontal":
        # Keep vertical (y) coordinate of p. Find x on the line.
        if vertical_line:
            new_x = x1
            new_y = py
        else:
            if abs(slope) < 1.0e-12:
                new_x = px
                new_y = intercept    # horizontal line
            else:
                new_x = (py - intercept) / slope
                new_y = py
    else:  # shortest
        if vertical_line:
            new_x = x1
            new_y = py
        else:
            # Foot of perpendicular in 2-D.
            s2 = 1.0 + slope * slope
            new_x = (px + slope * py - slope * intercept) / s2
            new_y = slope * new_x + intercept

    out = [0.0, 0.0, 0.0]
    out[xi] = new_x
    out[yi] = new_y
    out[keep] = p[keep]
    return (out[0], out[1], out[2])


# ---------------------------------------------------------------------------
# Vertex Align: selection / scene helpers
# ---------------------------------------------------------------------------

def _va_selected_verts():
    """Return a list of long-path vertex names for the current selection.

    Expands edge / face selections to their vertices and dedupes.
    Returns [] if Maya unavailable or nothing mesh-component selected.
    """
    if not MAYA_AVAILABLE:
        return []
    sel = cmds.ls(sl=True, fl=True, long=True) or []
    if not sel:
        return []
    try:
        verts = cmds.polyListComponentConversion(sel, toVertex=True) or []
        verts = cmds.ls(verts, fl=True, long=True) or []
    except Exception:
        verts = []
    seen = set()
    out = []
    for v in verts:
        if u".vtx[" not in v:
            continue
        if v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


def _va_selected_edges_raw():
    """Return list of currently selected edges (long paths)."""
    if not MAYA_AVAILABLE:
        return []
    sel = cmds.ls(sl=True, fl=True, long=True) or []
    return [s for s in sel if u".e[" in s]


def _va_vtx_pos(vtx):
    try:
        p = cmds.pointPosition(vtx, w=True)
        return (p[0], p[1], p[2])
    except Exception:
        return None


def _va_sort_edge_chain(edges):
    """Sort a set of selected edges into a chain of ordered vertices.

    Returns a list of vertex long-path names in traversal order, or
    None if the edges don't form a single open/closed chain.

    Strategy: build a vertex→incident-edge graph. A valid chain has
    exactly two endpoint vertices (degree 1) for an open chain, or
    zero for a closed loop. Walk from an endpoint picking the
    unvisited neighbour each step.
    """
    if not edges:
        return None
    # Build adjacency.
    adj = {}
    edge_to_verts = {}
    for e in edges:
        try:
            vs = cmds.polyListComponentConversion(
                e, fromEdge=True, toVertex=True) or []
            vs = cmds.ls(vs, fl=True, long=True) or []
        except Exception:
            return None
        if len(vs) < 2:
            return None
        v0, v1 = vs[0], vs[1]
        edge_to_verts[e] = (v0, v1)
        adj.setdefault(v0, set()).add(v1)
        adj.setdefault(v1, set()).add(v0)

    # Must be connected — do a BFS and ensure we hit every vertex.
    if not adj:
        return None
    start = next(iter(adj))
    visited = set([start])
    queue = [start]
    while queue:
        v = queue.pop(0)
        for n in adj.get(v, ()):
            if n not in visited:
                visited.add(n)
                queue.append(n)
    if len(visited) != len(adj):
        return None

    # Find endpoints (degree 1). If none, treat as a loop and start
    # anywhere.
    endpoints = [v for v, nbrs in adj.items() if len(nbrs) == 1]
    if len(endpoints) not in (0, 2):
        return None      # branches or non-manifold-ish — can't chain
    start = endpoints[0] if endpoints else next(iter(adj))

    chain = [start]
    prev = None
    cur = start
    while True:
        nxt = None
        for n in adj[cur]:
            if n == prev:
                continue
            nxt = n
            break
        if nxt is None:
            break
        chain.append(nxt)
        prev = cur
        cur = nxt
        if cur == start:    # closed loop — stop
            break
    if len(chain) != len(adj):
        return None         # couldn't traverse everything
    return chain


def _va_autopair_from_verts(vert_names):
    """Pick the most distant pair of verts as auto-Pos1/Pos2.

    Returns (p1, p2, idx1, idx2) or (None, None, -1, -1) if <2 verts.
    Uses the AABB diagonal — fast and matches what the user would
    visually pick as "endpoints".
    """
    if len(vert_names) < 2:
        return None, None, -1, -1
    positions = [_va_vtx_pos(v) for v in vert_names]
    positions = [p for p in positions if p is not None]
    if len(positions) < 2:
        return None, None, -1, -1
    # Find the pair with maximum distance (brute force for N small;
    # N is in vertex counts so usually <10000 — still quadratic can
    # hurt, so use AABB diagonal instead).
    bb_min = [positions[0][0], positions[0][1], positions[0][2]]
    bb_max = [positions[0][0], positions[0][1], positions[0][2]]
    for p in positions[1:]:
        for i in range(3):
            if p[i] < bb_min[i]:
                bb_min[i] = p[i]
            if p[i] > bb_max[i]:
                bb_max[i] = p[i]
    # Longest axis.
    dims = [bb_max[i] - bb_min[i] for i in range(3)]
    axis = max(range(3), key=lambda i: dims[i])
    # The two verts with extreme value on that axis.
    i_min = 0; i_max = 0
    v_min = positions[0][axis]; v_max = positions[0][axis]
    for i, p in enumerate(positions):
        if p[axis] < v_min:
            v_min = p[axis]; i_min = i
        if p[axis] > v_max:
            v_max = p[axis]; i_max = i
    return positions[i_min], positions[i_max], i_min, i_max


def _va_autopair_plane_from_verts(vert_names):
    """Pick 3 non-colinear verts from the selection for plane fit.

    Greedy strategy: first point at min-extreme along the dominant
    axis, second at max-extreme along that axis, third = point that
    maximises distance from the line p1-p2.
    Returns (p1, p2, p3) or (None, None, None) if < 3 usable verts.
    """
    if len(vert_names) < 3:
        return None, None, None
    positions = [_va_vtx_pos(v) for v in vert_names]
    positions = [p for p in positions if p is not None]
    if len(positions) < 3:
        return None, None, None
    p1, p2, _, _ = _va_autopair_from_verts(vert_names)
    if p1 is None or p2 is None:
        return None, None, None
    # Find point maximising perpendicular distance from p1-p2.
    best = None
    best_d2 = -1.0
    for p in positions:
        proj = _va_project_point_on_line(p1, p2, p)
        dx = p[0] - proj[0]; dy = p[1] - proj[1]; dz = p[2] - proj[2]
        d2 = dx * dx + dy * dy + dz * dz
        if d2 > best_d2:
            best_d2 = d2
            best = p
    if best is None or best_d2 < 1.0e-12:
        return None, None, None
    return p1, p2, best


def _va_detect_view_from_panel():
    """Return 'top' / 'front' / 'side' based on the focus model panel's
    camera. If the focus panel is persp or unknown, returns None.
    """
    if not MAYA_AVAILABLE:
        return None
    try:
        panel = cmds.getPanel(withFocus=True)
        if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
            return None
        cam = cmds.modelPanel(panel, query=True, camera=True)
        if not cam:
            return None
        # Normalise — may be a transform or shape name.
        if cmds.nodeType(cam) == "transform":
            cam_xf = cam
        else:
            parents = cmds.listRelatives(cam, parent=True, fullPath=True) or []
            cam_xf = parents[0] if parents else cam
        short = cam_xf.split("|")[-1].lower()
        if short in ("top", "topshape"):
            return "top"
        if short in ("front", "frontshape"):
            return "front"
        if short in ("side", "sideshape"):
            return "side"
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Vertex Align: dialog
# ---------------------------------------------------------------------------

class VertexAlignDialog(QtWidgets.QDialog):
    """Three-mode vertex-align tool with Face-Snap-style preview flow."""

    status_msg = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(VertexAlignDialog, self).__init__(parent)
        self.setObjectName("DW_VertexAlign_Dialog")
        self.setWindowTitle(tr("va_dlg_title"))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumSize(460, 520)
        self.setStyleSheet(
            "QDialog{background-color:#333;color:#EEE}"
            "QLabel{color:#EEE}")
        # Preview state.
        self._snapshot = None        # dict {vtx: (x,y,z)}
        self._preview_active = False
        self._undo_open = False
        # Manual reference points, per mode.
        self._pos_3d_1 = None        # (x,y,z) | None
        self._pos_3d_2 = None
        self._pos_2d_1 = None
        self._pos_2d_2 = None
        self._pos_flat_1 = None
        self._pos_flat_2 = None
        self._pos_flat_3 = None
        self._build()

    # -- UI construction -------------------------------------------------
    def _build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(8, 8, 8, 8)
        lo.setSpacing(6)

        self._tabs = QtWidgets.QTabWidget()
        self._tabs.setStyleSheet(
            "QTabWidget::pane{border:1px solid #444;background:#2B2B2B;"
            "border-radius:4px;top:-1px}"
            "QTabBar::tab{background:#3C3C3C;color:#BBB;padding:6px 14px;"
            "border:1px solid #444;border-bottom:none;margin-right:1px;"
            "font-size:11px}"
            "QTabBar::tab:selected{background:#2B2B2B;color:#EEE;"
            "font-weight:bold}")
        self._tabs.addTab(self._build_tab_linear_3d(), tr("va_tab_linear3d"))
        self._tabs.addTab(self._build_tab_linear_2d(), tr("va_tab_linear2d"))
        self._tabs.addTab(self._build_tab_flatten(),   tr("va_tab_flatten"))
        self._tabs.currentChanged.connect(self._on_tab_changed)
        lo.addWidget(self._tabs, 1)

        # Preview status line.
        self._preview_lbl = QtWidgets.QLabel(tr("va_status_ready"))
        self._preview_lbl.setWordWrap(True)
        self._preview_lbl.setStyleSheet(
            "color:#8BC34A;background-color:#2B2B2B;"
            "padding:3px 8px;border-radius:3px;font-size:10px")
        lo.addWidget(self._preview_lbl)

        # Preview/confirm/revert row.
        pr = QtWidgets.QHBoxLayout()
        pr.setSpacing(4)
        self._btn_preview = _mkbtn(tr("va_btn_preview"), 28,
                                    "#2196F3", "#1976D2", fs=11)
        self._btn_preview.clicked.connect(self._on_preview)
        pr.addWidget(self._btn_preview, 1)
        self._btn_confirm = _mkbtn(tr("va_btn_confirm"), 28,
                                    "#4CAF50", "#388E3C", fs=11)
        self._btn_confirm.clicked.connect(self._on_confirm)
        self._btn_confirm.setEnabled(False)
        pr.addWidget(self._btn_confirm)
        self._btn_revert = _mkbtn(tr("va_btn_revert"), 28,
                                   "#F44336", "#D32F2F", fs=11)
        self._btn_revert.clicked.connect(self._on_revert)
        self._btn_revert.setEnabled(False)
        pr.addWidget(self._btn_revert)
        self._btn_close = _mkbtn(tr("btn_close"), 28, "#555", "#444", fs=11)
        self._btn_close.clicked.connect(self.close)
        pr.addWidget(self._btn_close)
        lo.addLayout(pr)

    def _build_tab_linear_3d(self):
        w = QtWidgets.QWidget()
        lo = QtWidgets.QVBoxLayout(w)
        lo.setContentsMargins(8, 10, 8, 8)
        lo.setSpacing(8)

        desc = QtWidgets.QLabel(tr("va_l3d_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#BBB;font-size:10px")
        lo.addWidget(desc)

        # Reference-point source group.
        grp_src = QtWidgets.QGroupBox()
        grp_src.setStyleSheet(_VA_GRP_SS)
        grp_src_lo = QtWidgets.QVBoxLayout(grp_src)
        grp_src_lo.setContentsMargins(6, 10, 6, 6)
        grp_src_lo.setSpacing(4)
        src_hdr = QtWidgets.QLabel(
            u"\u25A0 " + tr("va_lbl_reference"))
        src_hdr.setStyleSheet("color:#2196F3;font-size:11px;font-weight:bold")
        grp_src_lo.addWidget(src_hdr)

        self._l3d_rb_auto = QtWidgets.QRadioButton(tr("va_l3d_auto"))
        self._l3d_rb_auto.setStyleSheet(_VA_RB_SS)
        self._l3d_rb_auto.setChecked(True)
        grp_src_lo.addWidget(self._l3d_rb_auto)
        self._l3d_rb_manual = QtWidgets.QRadioButton(tr("va_l3d_manual"))
        self._l3d_rb_manual.setStyleSheet(_VA_RB_SS)
        grp_src_lo.addWidget(self._l3d_rb_manual)

        # Manual Pos1 / Pos2 capture rows.
        self._l3d_pos1_lbl = QtWidgets.QLabel(tr("va_lbl_pos_empty", n=1))
        self._l3d_pos2_lbl = QtWidgets.QLabel(tr("va_lbl_pos_empty", n=2))
        for l in (self._l3d_pos1_lbl, self._l3d_pos2_lbl):
            l.setStyleSheet(
                "color:#888;background-color:#2B2B2B;"
                "padding:3px 8px;border-radius:3px;"
                "font-size:10px;font-family:monospace")
        self._l3d_btn_pos1 = _mkbtn(tr("va_btn_set_pos", n=1), 22,
                                     "#607D8B", "#455A64", fs=10)
        self._l3d_btn_pos1.clicked.connect(
            lambda: self._capture_pos("3d", 1))
        self._l3d_btn_pos2 = _mkbtn(tr("va_btn_set_pos", n=2), 22,
                                     "#607D8B", "#455A64", fs=10)
        self._l3d_btn_pos2.clicked.connect(
            lambda: self._capture_pos("3d", 2))

        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(6)
        row1.addWidget(self._l3d_btn_pos1)
        row1.addWidget(self._l3d_pos1_lbl, 1)
        grp_src_lo.addLayout(row1)
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(6)
        row2.addWidget(self._l3d_btn_pos2)
        row2.addWidget(self._l3d_pos2_lbl, 1)
        grp_src_lo.addLayout(row2)

        lo.addWidget(grp_src)

        # Options group (equidistant).
        self._l3d_cb_equal = QtWidgets.QCheckBox(tr("va_l3d_chk_equal"))
        self._l3d_cb_equal.setStyleSheet(
            "QCheckBox{color:#DDD;font-size:10px}"
            "QCheckBox::indicator{width:12px;height:12px}")
        lo.addWidget(self._l3d_cb_equal)

        hint = QtWidgets.QLabel(tr("va_l3d_chk_equal_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#888;font-size:9px;padding:0 18px")
        lo.addWidget(hint)

        lo.addStretch()
        return w

    def _build_tab_linear_2d(self):
        w = QtWidgets.QWidget()
        lo = QtWidgets.QVBoxLayout(w)
        lo.setContentsMargins(8, 10, 8, 8)
        lo.setSpacing(8)

        desc = QtWidgets.QLabel(tr("va_l2d_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#BBB;font-size:10px")
        lo.addWidget(desc)

        # View group.
        grp_view = QtWidgets.QGroupBox()
        grp_view.setStyleSheet(_VA_GRP_SS)
        grp_view_lo = QtWidgets.QVBoxLayout(grp_view)
        grp_view_lo.setContentsMargins(6, 10, 6, 6)
        grp_view_lo.setSpacing(4)
        view_hdr = QtWidgets.QLabel(
            u"\u25A0 " + tr("va_lbl_view"))
        view_hdr.setStyleSheet(
            "color:#2196F3;font-size:11px;font-weight:bold")
        grp_view_lo.addWidget(view_hdr)
        view_row = QtWidgets.QHBoxLayout()
        view_row.setSpacing(8)
        self._l2d_rb_top = QtWidgets.QRadioButton(tr("va_view_top"))
        self._l2d_rb_top.setStyleSheet(_VA_RB_SS)
        self._l2d_rb_top.setChecked(True)
        view_row.addWidget(self._l2d_rb_top)
        self._l2d_rb_front = QtWidgets.QRadioButton(tr("va_view_front"))
        self._l2d_rb_front.setStyleSheet(_VA_RB_SS)
        view_row.addWidget(self._l2d_rb_front)
        self._l2d_rb_side = QtWidgets.QRadioButton(tr("va_view_side"))
        self._l2d_rb_side.setStyleSheet(_VA_RB_SS)
        view_row.addWidget(self._l2d_rb_side)
        view_row.addStretch()
        self._l2d_btn_auto_view = _mkbtn(
            tr("va_btn_auto_view"), 22, "#607D8B", "#455A64", fs=10)
        self._l2d_btn_auto_view.clicked.connect(self._auto_detect_view)
        view_row.addWidget(self._l2d_btn_auto_view)
        grp_view_lo.addLayout(view_row)
        lo.addWidget(grp_view)

        # Drop-direction group.
        grp_drop = QtWidgets.QGroupBox()
        grp_drop.setStyleSheet(_VA_GRP_SS)
        grp_drop_lo = QtWidgets.QVBoxLayout(grp_drop)
        grp_drop_lo.setContentsMargins(6, 10, 6, 6)
        grp_drop_lo.setSpacing(4)
        drop_hdr = QtWidgets.QLabel(
            u"\u25A0 " + tr("va_lbl_drop_mode"))
        drop_hdr.setStyleSheet(
            "color:#2196F3;font-size:11px;font-weight:bold")
        grp_drop_lo.addWidget(drop_hdr)
        drop_row = QtWidgets.QHBoxLayout()
        drop_row.setSpacing(8)
        self._l2d_rb_short = QtWidgets.QRadioButton(tr("va_drop_shortest"))
        self._l2d_rb_short.setStyleSheet(_VA_RB_SS)
        self._l2d_rb_short.setChecked(True)
        drop_row.addWidget(self._l2d_rb_short)
        self._l2d_rb_horiz = QtWidgets.QRadioButton(tr("va_drop_horizontal"))
        self._l2d_rb_horiz.setStyleSheet(_VA_RB_SS)
        drop_row.addWidget(self._l2d_rb_horiz)
        self._l2d_rb_vert = QtWidgets.QRadioButton(tr("va_drop_vertical"))
        self._l2d_rb_vert.setStyleSheet(_VA_RB_SS)
        drop_row.addWidget(self._l2d_rb_vert)
        drop_row.addStretch()
        grp_drop_lo.addLayout(drop_row)
        lo.addWidget(grp_drop)

        hint = QtWidgets.QLabel(tr("va_l2d_ref_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#888;font-size:9px;padding:0 4px")
        lo.addWidget(hint)

        lo.addStretch()
        return w

    def _build_tab_flatten(self):
        w = QtWidgets.QWidget()
        lo = QtWidgets.QVBoxLayout(w)
        lo.setContentsMargins(8, 10, 8, 8)
        lo.setSpacing(8)

        desc = QtWidgets.QLabel(tr("va_flat_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#BBB;font-size:10px")
        lo.addWidget(desc)

        grp = QtWidgets.QGroupBox()
        grp.setStyleSheet(_VA_GRP_SS)
        grp_lo = QtWidgets.QVBoxLayout(grp)
        grp_lo.setContentsMargins(6, 10, 6, 6)
        grp_lo.setSpacing(4)
        hdr = QtWidgets.QLabel(u"\u25A0 " + tr("va_lbl_reference"))
        hdr.setStyleSheet(
            "color:#2196F3;font-size:11px;font-weight:bold")
        grp_lo.addWidget(hdr)

        self._flat_rb_auto = QtWidgets.QRadioButton(tr("va_flat_auto"))
        self._flat_rb_auto.setStyleSheet(_VA_RB_SS)
        self._flat_rb_auto.setChecked(True)
        grp_lo.addWidget(self._flat_rb_auto)
        self._flat_rb_manual = QtWidgets.QRadioButton(tr("va_flat_manual"))
        self._flat_rb_manual.setStyleSheet(_VA_RB_SS)
        grp_lo.addWidget(self._flat_rb_manual)

        self._flat_pos_lbls = []
        self._flat_pos_btns = []
        for i in (1, 2, 3):
            lbl = QtWidgets.QLabel(tr("va_lbl_pos_empty", n=i))
            lbl.setStyleSheet(
                "color:#888;background-color:#2B2B2B;"
                "padding:3px 8px;border-radius:3px;"
                "font-size:10px;font-family:monospace")
            btn = _mkbtn(tr("va_btn_set_pos", n=i), 22,
                         "#607D8B", "#455A64", fs=10)
            btn.clicked.connect(lambda _=False, n=i: self._capture_pos("flat", n))
            row = QtWidgets.QHBoxLayout()
            row.setSpacing(6)
            row.addWidget(btn)
            row.addWidget(lbl, 1)
            grp_lo.addLayout(row)
            self._flat_pos_lbls.append(lbl)
            self._flat_pos_btns.append(btn)
        lo.addWidget(grp)

        hint = QtWidgets.QLabel(tr("va_flat_auto_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#888;font-size:9px;padding:0 4px")
        lo.addWidget(hint)

        lo.addStretch()
        return w

    # -- Mode / reference capture ---------------------------------------
    def _on_tab_changed(self, _idx):
        # If there's a pending preview, auto-revert before switching
        # mode so we don't leave half-applied edits around.
        if self._preview_active:
            self._on_revert()

    def _capture_pos(self, mode, n):
        """Capture the current selection's centroid as Pos N for the
        indicated mode ("3d", "2d", or "flat")."""
        if not MAYA_AVAILABLE:
            return
        verts = _va_selected_verts()
        if not verts:
            self._set_status(tr("va_status_no_sel_for_pos"), warn=True)
            return
        # Use centroid of the selection for robustness when user picks
        # multiple vertices.
        positions = [_va_vtx_pos(v) for v in verts]
        positions = [p for p in positions if p is not None]
        if not positions:
            self._set_status(tr("va_status_no_sel_for_pos"), warn=True)
            return
        cx = sum(p[0] for p in positions) / len(positions)
        cy = sum(p[1] for p in positions) / len(positions)
        cz = sum(p[2] for p in positions) / len(positions)
        pos = (cx, cy, cz)
        label_text = tr("va_lbl_pos_value", n=n,
                         x=u"{0:.3f}".format(pos[0]),
                         y=u"{0:.3f}".format(pos[1]),
                         z=u"{0:.3f}".format(pos[2]))
        if mode == "3d":
            if n == 1:
                self._pos_3d_1 = pos
                self._l3d_pos1_lbl.setText(label_text)
                self._l3d_pos1_lbl.setStyleSheet(_VA_POS_LBL_SS_SET)
            else:
                self._pos_3d_2 = pos
                self._l3d_pos2_lbl.setText(label_text)
                self._l3d_pos2_lbl.setStyleSheet(_VA_POS_LBL_SS_SET)
            self._l3d_rb_manual.setChecked(True)
        elif mode == "flat":
            if n == 1:
                self._pos_flat_1 = pos
            elif n == 2:
                self._pos_flat_2 = pos
            else:
                self._pos_flat_3 = pos
            lbl = self._flat_pos_lbls[n - 1]
            lbl.setText(label_text)
            lbl.setStyleSheet(_VA_POS_LBL_SS_SET)
            self._flat_rb_manual.setChecked(True)
        self._set_status(tr("va_status_pos_captured", n=n), warn=False)

    def _auto_detect_view(self):
        view = _va_detect_view_from_panel()
        if view == "top":
            self._l2d_rb_top.setChecked(True)
        elif view == "front":
            self._l2d_rb_front.setChecked(True)
        elif view == "side":
            self._l2d_rb_side.setChecked(True)
        else:
            self._set_status(tr("va_status_no_ortho_view"), warn=True)
            return
        self._set_status(tr("va_status_view_detected",
                             view=tr(u"va_view_" + view)),
                          warn=False)

    # -- Preview / confirm / revert -------------------------------------
    def _set_status(self, msg, warn):
        self._preview_lbl.setText(msg)
        colour = "#FF9800" if warn else "#8BC34A"
        self._preview_lbl.setStyleSheet(
            "color:%s;background-color:#2B2B2B;"
            "padding:3px 8px;border-radius:3px;font-size:10px" % colour)
        self.status_msg.emit(msg)

    def _on_preview(self):
        if not MAYA_AVAILABLE:
            return
        # If a preview is already active, revert first so the new
        # preview starts from the ORIGINAL geometry.
        if self._preview_active:
            self._revert_only()

        verts = _va_selected_verts()
        if not verts:
            self._set_status(tr("va_status_no_selection"), warn=True)
            return

        mode_idx = self._tabs.currentIndex()
        try:
            if mode_idx == 0:
                self._preview_linear_3d(verts)
            elif mode_idx == 1:
                self._preview_linear_2d(verts)
            else:
                self._preview_flatten(verts)
        except _VertexAlignError as err:
            self._set_status(str(err), warn=True)

    def _begin_undo(self):
        cmds.undoInfo(openChunk=True, chunkName="DW_VertexAlign")
        self._undo_open = True

    def _close_undo(self):
        if self._undo_open:
            try:
                cmds.undoInfo(closeChunk=True)
            except Exception:
                pass
            self._undo_open = False

    def _capture_snapshot(self, verts):
        snap = {}
        for v in verts:
            p = _va_vtx_pos(v)
            if p is not None:
                snap[v] = p
        return snap

    def _apply_new_positions(self, new_positions):
        """Apply {vtx: (x,y,z)} to the scene."""
        for v, pos in new_positions.items():
            try:
                cmds.xform(v, ws=True, t=(pos[0], pos[1], pos[2]))
            except Exception:
                pass

    # -- Mode 1: Linear 3D ----------------------------------------------
    def _preview_linear_3d(self, verts):
        # Resolve reference line.
        p1, p2 = self._resolve_3d_reference(verts)
        # Determine vertex traversal order for equidistant mode.
        ordered = None
        want_equal = self._l3d_cb_equal.isChecked()
        if want_equal:
            edges = _va_selected_edges_raw()
            if edges:
                chain = _va_sort_edge_chain(edges)
                if chain is not None and len(chain) >= 2:
                    ordered = chain
        # Compute new positions.
        new_positions = {}
        source_verts = ordered if ordered else verts
        n = len(source_verts)
        if want_equal and ordered is not None and n >= 2:
            # Re-anchor p1/p2 to the chain endpoints so endpoints stay
            # in place (they're what defines the line to distribute on).
            ep1 = _va_vtx_pos(ordered[0])
            ep2 = _va_vtx_pos(ordered[-1])
            if ep1 and ep2:
                p1, p2 = ep1, ep2
            for i, v in enumerate(ordered):
                t = float(i) / float(n - 1)
                new_positions[v] = _va_lerp(p1, p2, t)
        else:
            for v in source_verts:
                p = _va_vtx_pos(v)
                if p is None:
                    continue
                new_positions[v] = _va_project_point_on_line(p1, p2, p)

        self._commit_preview(new_positions, n_verts=len(new_positions),
                              label_key="va_status_preview_linear_3d")

    def _resolve_3d_reference(self, verts):
        if self._l3d_rb_manual.isChecked():
            if self._pos_3d_1 is None or self._pos_3d_2 is None:
                raise _VertexAlignError(tr("va_status_manual_not_set"))
            return self._pos_3d_1, self._pos_3d_2
        # Auto: prefer edge-chain endpoints, else AABB diagonal.
        edges = _va_selected_edges_raw()
        if edges:
            chain = _va_sort_edge_chain(edges)
            if chain is not None and len(chain) >= 2:
                p1 = _va_vtx_pos(chain[0])
                p2 = _va_vtx_pos(chain[-1])
                if p1 is not None and p2 is not None:
                    return p1, p2
        p1, p2, _, _ = _va_autopair_from_verts(verts)
        if p1 is None or p2 is None:
            raise _VertexAlignError(tr("va_status_need_2_verts"))
        return p1, p2

    # -- Mode 2: Linear 2D ----------------------------------------------
    def _preview_linear_2d(self, verts):
        view = "top"
        if self._l2d_rb_front.isChecked():
            view = "front"
        elif self._l2d_rb_side.isChecked():
            view = "side"
        drop = "shortest"
        if self._l2d_rb_horiz.isChecked():
            drop = "horizontal"
        elif self._l2d_rb_vert.isChecked():
            drop = "vertical"
        # Reference line = AABB extremes along the view's horizontal axis.
        p1, p2 = self._resolve_2d_reference(verts, view)
        new_positions = {}
        for v in verts:
            p = _va_vtx_pos(v)
            if p is None:
                continue
            new_positions[v] = _va_project_line_2d(p1, p2, p, view, drop)
        self._commit_preview(
            new_positions,
            n_verts=len(new_positions),
            label_key="va_status_preview_linear_2d",
            view=tr(u"va_view_" + view))

    def _resolve_2d_reference(self, verts, view):
        # The "reference line" in 2D mode is derived automatically from
        # the selection extremes along the view's horizontal axis.
        positions = [_va_vtx_pos(v) for v in verts]
        positions = [p for p in positions if p is not None]
        if len(positions) < 2:
            raise _VertexAlignError(tr("va_status_need_2_verts"))
        # Horizontal-axis index per view.
        if view == "top":
            hi = 0         # X
        elif view == "side":
            hi = 2         # Z
        else:              # front
            hi = 0
        i_min = 0; i_max = 0
        v_min = positions[0][hi]; v_max = positions[0][hi]
        for i, p in enumerate(positions):
            if p[hi] < v_min:
                v_min = p[hi]; i_min = i
            if p[hi] > v_max:
                v_max = p[hi]; i_max = i
        return positions[i_min], positions[i_max]

    # -- Mode 3: Flatten -------------------------------------------------
    def _preview_flatten(self, verts):
        p1, p2, p3 = self._resolve_flat_reference(verts)
        new_positions = {}
        for v in verts:
            p = _va_vtx_pos(v)
            if p is None:
                continue
            new_positions[v] = _va_project_point_on_plane(p1, p2, p3, p)
        self._commit_preview(new_positions,
                              n_verts=len(new_positions),
                              label_key="va_status_preview_flatten")

    def _resolve_flat_reference(self, verts):
        if self._flat_rb_manual.isChecked():
            if (self._pos_flat_1 is None or self._pos_flat_2 is None
                    or self._pos_flat_3 is None):
                raise _VertexAlignError(tr("va_status_manual_not_set"))
            return self._pos_flat_1, self._pos_flat_2, self._pos_flat_3
        p1, p2, p3 = _va_autopair_plane_from_verts(verts)
        if p1 is None or p2 is None or p3 is None:
            raise _VertexAlignError(tr("va_status_flat_autofail"))
        return p1, p2, p3

    # -- Commit helpers --------------------------------------------------
    def _commit_preview(self, new_positions, n_verts, label_key, **kw):
        if not new_positions:
            self._set_status(tr("va_status_nothing_to_move"), warn=True)
            return
        self._snapshot = self._capture_snapshot(new_positions.keys())
        self._begin_undo()
        self._apply_new_positions(new_positions)
        self._preview_active = True
        self._btn_confirm.setEnabled(True)
        self._btn_revert.setEnabled(True)
        self._set_status(tr(label_key, count=n_verts, **kw), warn=False)

    def _on_confirm(self):
        self._close_undo()
        self._preview_active = False
        self._snapshot = None
        self._btn_confirm.setEnabled(False)
        self._btn_revert.setEnabled(False)
        self._set_status(tr("va_status_confirmed"), warn=False)

    def _on_revert(self):
        self._revert_only()
        self._set_status(tr("va_status_reverted"), warn=False)

    def _revert_only(self):
        self._close_undo()
        if MAYA_AVAILABLE:
            try:
                cmds.undo()
            except Exception:
                pass
        self._preview_active = False
        self._snapshot = None
        self._btn_confirm.setEnabled(False)
        self._btn_revert.setEnabled(False)

    # -- Labels ----------------------------------------------------------
    def refresh_labels(self):
        self.setWindowTitle(tr("va_dlg_title"))
        self._tabs.setTabText(0, tr("va_tab_linear3d"))
        self._tabs.setTabText(1, tr("va_tab_linear2d"))
        self._tabs.setTabText(2, tr("va_tab_flatten"))
        self._btn_preview.setText(tr("va_btn_preview"))
        self._btn_confirm.setText(tr("va_btn_confirm"))
        self._btn_revert.setText(tr("va_btn_revert"))
        self._btn_close.setText(tr("btn_close"))

    def closeEvent(self, event):
        # Auto-revert unconfirmed preview on close.
        if self._preview_active:
            self._revert_only()
        super(VertexAlignDialog, self).closeEvent(event)


class _VertexAlignError(Exception):
    """Internal exception for short-circuiting preview with a status msg."""
    pass


# ---------------------------------------------------------------------------
# Vertex Align: stylesheet scraps
# ---------------------------------------------------------------------------

_VA_GRP_SS = (
    "QGroupBox{border:1px solid #555;border-radius:5px;"
    "background-color:#2B2B2B;margin-top:4px}")

_VA_RB_SS = (
    "QRadioButton{color:#DDD;font-size:10px}"
    "QRadioButton::indicator{width:11px;height:11px}")

_VA_POS_LBL_SS_SET = (
    "color:#8BC34A;background-color:#2B2B2B;"
    "padding:3px 8px;border-radius:3px;"
    "font-size:10px;font-family:monospace")


# ---------------------------------------------------------------------------
# Vertex Align: tab-side launcher + plumbing
# ---------------------------------------------------------------------------

def _build_vertex_align_group(tool_window, parent_layout):
    """Build the Vertex Align group for the Alignment tab."""
    grp = QtWidgets.QGroupBox()
    grp.setStyleSheet(
        "QGroupBox{border:1px solid #9C27B0;border-radius:6px;"
        "background-color:#2E2E2E;margin-top:6px}"
        "QGroupBox::title{subcontrol-origin:margin;left:10px;"
        "color:#EEE;font-size:11px;font-weight:bold}")
    lo = QtWidgets.QVBoxLayout(grp)
    lo.setContentsMargins(6, 10, 6, 6)
    lo.setSpacing(4)

    hdr = QtWidgets.QHBoxLayout()
    tool_window._va_grp_lbl = QtWidgets.QLabel(
        u"\u25A0 " + tr("va_grp_title"))
    tool_window._va_grp_lbl.setStyleSheet(
        "color:#9C27B0;font-size:11px;font-weight:bold")
    hdr.addWidget(tool_window._va_grp_lbl)
    hdr.addStretch()
    tool_window._va_btn_launch = _mkbtn(
        tr("va_btn_launch"), 24, "#9C27B0", "#7B1FA2", fs=10)
    tool_window._va_btn_launch.clicked.connect(
        lambda: _va_launch(tool_window))
    hdr.addWidget(tool_window._va_btn_launch)
    lo.addLayout(hdr)

    tool_window._va_desc_lbl = QtWidgets.QLabel(tr("va_grp_desc"))
    tool_window._va_desc_lbl.setStyleSheet(
        "color:#AAA;font-size:10px;padding:2px 4px")
    tool_window._va_desc_lbl.setWordWrap(True)
    lo.addWidget(tool_window._va_desc_lbl)

    tool_window._va_dialog = None
    parent_layout.addWidget(grp)
    return grp


def _va_launch(tool_window):
    """Open/raise the Vertex Align dialog."""
    if tool_window._va_dialog is None:
        tool_window._va_dialog = VertexAlignDialog(parent=tool_window)
        tool_window._va_dialog.status_msg.connect(
            lambda t: tool_window._status_bar.setText(t)
            if hasattr(tool_window, "_status_bar") else None)
    tool_window._va_dialog.show()
    tool_window._va_dialog.raise_()
    tool_window._va_dialog.activateWindow()


def _va_refresh_labels(tool_window):
    """Called from CollisionCheckToolWindow._refresh_labels()."""
    if hasattr(tool_window, "_va_grp_lbl"):
        tool_window._va_grp_lbl.setText(u"\u25A0 " + tr("va_grp_title"))
    if hasattr(tool_window, "_va_btn_launch"):
        tool_window._va_btn_launch.setText(tr("va_btn_launch"))
    if hasattr(tool_window, "_va_desc_lbl"):
        tool_window._va_desc_lbl.setText(tr("va_grp_desc"))
    w = getattr(tool_window, "_va_dialog", None)
    if w is not None:
        w.refresh_labels()


def _va_close_dialog(tool_window):
    w = getattr(tool_window, "_va_dialog", None)
    if w is not None:
        try:
            w.close()
        except Exception:
            pass
# ---------------------------------------------------------------------------
# CollisionCheckToolWindow  (Main UI — reference architecture compliant)
# ---------------------------------------------------------------------------
_MAIN_SS = (
    "QDialog{background-color:#333}"
    "QScrollArea{border:none;background-color:transparent}"
    "QScrollBar:vertical{background:#2B2B2B;width:10px}"
    "QScrollBar::handle:vertical{background:#555;border-radius:4px}"
    "QGroupBox{border-radius:6px;background-color:#2E2E2E;margin-top:6px}"
    "QGroupBox::title{subcontrol-origin:margin;left:10px;"
    "color:#EEE;font-size:11px;font-weight:bold}"
    "QLabel{color:#EEE}"
)

class CollisionCheckToolWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        if parent is None and MAYA_AVAILABLE:
            try:
                ptr    = omui.MQtUtil.mainWindow()
                if PY2:
                    parent = wrapInstance(long(ptr), QtWidgets.QWidget)  # noqa: F821
                else:
                    parent = wrapInstance(int(ptr), QtWidgets.QWidget)
            except Exception:
                pass

        super(CollisionCheckToolWindow, self).__init__(parent)
        self.setWindowTitle(tr("window_title"))
        self.setMinimumWidth(460)
        self.setMinimumHeight(560)
        # Initial resize: comfortably shows all Check-tab content
        # (Static + thresholds + Animation Scan) without scrolling.
        self.resize(480, 680)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setStyleSheet(_MAIN_SS)

        self._check_instances = []   # list of CheckItem instances
        self._check_widgets   = []   # list of CheckItemWidget
        self._result_window   = None
        self._anim_result_window = None
        self._vs_result_window = None
        self._anim_scanning   = False
        self._anim_cancelled  = False
        self._anim_results    = []

        self._build()

        if _saved_geometry:
            x, y, w, h = _saved_geometry
            self.setGeometry(x, y, w, h)
        else:
            self.adjustSize()

    # ------------------------------------------------------------------
    def _build(self):
        main_lo = QtWidgets.QVBoxLayout(self)
        main_lo.setContentsMargins(8, 8, 8, 8)
        main_lo.setSpacing(4)

        # ---- Header bar ----
        header = QtWidgets.QHBoxLayout()
        header.setSpacing(4)

        self._title_lbl = QtWidgets.QLabel(
            u"<b>{0}</b> <span style='color:#888;font-size:10px'>v{1}</span>".format(
                tr("window_title"), VERSION))
        self._title_lbl.setStyleSheet(
            "color:#EEE;font-size:14px;padding:4px")
        header.addWidget(self._title_lbl)
        header.addStretch()

        # Reload button
        reload_btn = QtWidgets.QPushButton(u"\u21BB")
        reload_btn.setFixedSize(28, 24)
        reload_btn.setToolTip(tr("btn_reload"))
        reload_btn.setStyleSheet(
            "QPushButton{background-color:#555;color:#EEE;"
            "border:1px solid #777;border-radius:3px;font-size:14px}"
            "QPushButton:hover{background-color:#4CAF50}")
        reload_btn.clicked.connect(self._on_reload)
        header.addWidget(reload_btn)

        # Update button - color indicates version state
        #   gray  = unknown / offline
        #   blue  = up to date
        #   red   = new version available
        self._update_btn = QtWidgets.QPushButton(u"\u2B07")  # down arrow
        self._update_btn.setFixedSize(28, 24)
        self._update_btn.setToolTip(tr("btn_update"))
        self._update_btn.clicked.connect(self._on_check_update)
        header.addWidget(self._update_btn)
        self._set_update_btn_state("unknown")

        # Help button
        help_btn = QtWidgets.QPushButton("?")
        help_btn.setFixedSize(24, 24)
        help_btn.setStyleSheet(
            "QPushButton{background-color:#555;color:#EEE;"
            "border:1px solid #777;border-radius:3px;font-size:12px;font-weight:bold}"
            "QPushButton:hover{background-color:#2196F3}")
        help_btn.clicked.connect(self._open_help)
        header.addWidget(help_btn)

        # Language toggle
        self._lang_btn = QtWidgets.QPushButton(tr("btn_lang"))
        self._lang_btn.setFixedSize(36, 24)
        self._lang_btn.setStyleSheet(
            "QPushButton{background-color:#555;color:#EEE;"
            "border:1px solid #777;border-radius:3px;font-size:10px;font-weight:bold}"
            "QPushButton:hover{background-color:#607D8B}")
        self._lang_btn.clicked.connect(self._toggle_lang)
        header.addWidget(self._lang_btn)

        # Static Results button
        self._btn_static_results = QtWidgets.QPushButton(tr("btn_static_results"))
        self._btn_static_results.setFixedHeight(24)
        self._btn_static_results.setEnabled(False)
        self._btn_static_results.setStyleSheet(
            "QPushButton{background-color:#2196F3;color:white;border:none;"
            "border-radius:4px;font-size:10px;font-weight:bold;padding:0 8px}"
            "QPushButton:hover{background-color:#1976D2}"
            "QPushButton:disabled{background-color:#444;color:#666}")
        self._btn_static_results.clicked.connect(self._show_static_results)
        header.addWidget(self._btn_static_results)

        # Anim Results button
        self._btn_anim_results = QtWidgets.QPushButton(tr("btn_anim_results"))
        self._btn_anim_results.setFixedHeight(24)
        self._btn_anim_results.setEnabled(False)
        self._btn_anim_results.setStyleSheet(
            "QPushButton{background-color:#FF9800;color:white;border:none;"
            "border-radius:4px;font-size:10px;font-weight:bold;padding:0 8px}"
            "QPushButton:hover{background-color:#F57C00}"
            "QPushButton:disabled{background-color:#444;color:#666}")
        self._btn_anim_results.clicked.connect(self._show_anim_results)
        header.addWidget(self._btn_anim_results)

        main_lo.addLayout(header)

        # ---- Selection mode row (built here; placed inside Check tab below) ----
        sel_row = QtWidgets.QHBoxLayout()
        sel_row.setContentsMargins(4, 0, 4, 0)
        self._cb_selected_only = QtWidgets.QCheckBox(tr("chk_selected_only"))
        self._cb_selected_only.setChecked(_use_selected_only[0])
        self._cb_selected_only.setStyleSheet(
            "QCheckBox{color:#AAA;font-size:10px}"
            "QCheckBox::indicator{width:12px;height:12px}")
        self._cb_selected_only.toggled.connect(self._on_selected_only_toggled)
        sel_row.addWidget(self._cb_selected_only)

        self._cb_self_intersect = QtWidgets.QCheckBox(tr("chk_self_intersect"))
        self._cb_self_intersect.setChecked(_self_intersect[0])
        self._cb_self_intersect.setStyleSheet(
            "QCheckBox{color:#AAA;font-size:10px}"
            "QCheckBox::indicator{width:12px;height:12px}")
        self._cb_self_intersect.toggled.connect(self._on_self_intersect_toggled)
        sel_row.addWidget(self._cb_self_intersect)

        sel_row.addStretch()
        # NOTE: sel_row is added to the Check tab's scroll area below
        #       (not to main_lo) so that the toggles only apply to checks.

        # ---- Tab widget (Check / Snap) ----
        self._tabs = QtWidgets.QTabWidget()
        self._tabs.setStyleSheet(
            "QTabWidget::pane{border:1px solid #444;background-color:#2B2B2B;"
            "border-radius:4px;top:-1px}"
            "QTabBar::tab{background-color:#3C3C3C;color:#CCC;padding:6px 16px;"
            "border:1px solid #444;border-bottom:none;"
            "border-top-left-radius:4px;border-top-right-radius:4px;"
            "font-size:10px}"
            "QTabBar::tab:selected{background-color:#2B2B2B;color:#FFF;"
            "border-color:#2196F3}"
            "QTabBar::tab:hover{background-color:#4A4A4A}")

        # ---- Check tab ----
        check_tab = QtWidgets.QWidget()
        check_tab_lo = QtWidgets.QVBoxLayout(check_tab)
        check_tab_lo.setContentsMargins(0, 0, 0, 0)
        check_tab_lo.setSpacing(0)
        check_scroll = QtWidgets.QScrollArea()
        check_scroll.setWidgetResizable(True)
        check_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        check_scroll_w = QtWidgets.QWidget()
        scroll_lo = QtWidgets.QVBoxLayout(check_scroll_w)
        scroll_lo.setContentsMargins(4, 4, 4, 4)
        scroll_lo.setSpacing(8)

        # Selection toggles (moved here from outside the tabs)
        scroll_lo.addLayout(sel_row)

        # ---- Static Check Group (blue border) ----
        static_grp = QtWidgets.QGroupBox()
        static_grp.setStyleSheet(
            "QGroupBox{border:1px solid #2196F3;border-radius:6px;"
            "background-color:#2E2E2E;margin-top:6px}"
            "QGroupBox::title{subcontrol-origin:margin;left:10px;"
            "color:#EEE;font-size:11px;font-weight:bold}")

        static_lo = QtWidgets.QVBoxLayout(static_grp)
        static_lo.setContentsMargins(6, 10, 6, 6)
        static_lo.setSpacing(4)

        # Group header row
        grp_header = QtWidgets.QHBoxLayout()
        self._static_grp_lbl = QtWidgets.QLabel(
            u"\u25A0 " + tr("grp_static"))
        self._static_grp_lbl.setStyleSheet(
            "color:#2196F3;font-size:11px;font-weight:bold")
        grp_header.addWidget(self._static_grp_lbl)
        grp_header.addStretch()

        self._btn_run_all = _mkbtn(tr("run_static"), 24, "#2196F3", "#1976D2")
        self._btn_run_all.clicked.connect(self._run_all_static)
        grp_header.addWidget(self._btn_run_all)
        static_lo.addLayout(grp_header)

        # CheckItem widgets
        for cls in STATIC_CHECKS:
            inst = cls()
            widget = CheckItemWidget(inst, has_settings=False)
            widget.check_requested.connect(self._on_check_done)
            self._check_instances.append(inst)
            self._check_widgets.append(widget)
            static_lo.addWidget(widget)

        # Depth threshold row (inline)
        thresh_row = QtWidgets.QHBoxLayout()
        self._lbl_depth_thresh = QtWidgets.QLabel(tr("lbl_depth_threshold"))
        self._lbl_depth_thresh.setStyleSheet("color:#AAA;font-size:10px")
        thresh_row.addWidget(self._lbl_depth_thresh)
        self._spin_depth = QtWidgets.QDoubleSpinBox()
        self._spin_depth.setRange(0.0, 10.0)
        self._spin_depth.setDecimals(3)
        self._spin_depth.setSingleStep(0.005)
        self._spin_depth.setValue(_depth_threshold[0])
        self._spin_depth.setFixedWidth(75)
        self._spin_depth.setStyleSheet(
            "QDoubleSpinBox{background-color:#2B2B2B;color:#EEE;"
            "border:1px solid #555;border-radius:3px;padding:1px;font-size:10px}")
        self._spin_depth.valueChanged.connect(self._on_depth_threshold_changed)
        thresh_row.addWidget(self._spin_depth)
        thresh_row.addStretch()
        static_lo.addLayout(thresh_row)

        # Vertex-share tolerance row (below depth threshold)
        vst_row = QtWidgets.QHBoxLayout()
        self._lbl_vert_share_tol = QtWidgets.QLabel(tr("lbl_vert_share_tol"))
        self._lbl_vert_share_tol.setStyleSheet("color:#AAA;font-size:10px")
        self._lbl_vert_share_tol.setToolTip(tr("tip_vert_share_tol"))
        vst_row.addWidget(self._lbl_vert_share_tol)
        self._spin_vert_share_tol = QtWidgets.QDoubleSpinBox()
        self._spin_vert_share_tol.setRange(0.0, 1.0)
        self._spin_vert_share_tol.setDecimals(6)
        self._spin_vert_share_tol.setSingleStep(0.0001)
        self._spin_vert_share_tol.setValue(_get_vert_share_tolerance())
        self._spin_vert_share_tol.setFixedWidth(85)
        self._spin_vert_share_tol.setToolTip(tr("tip_vert_share_tol"))
        self._spin_vert_share_tol.setStyleSheet(
            "QDoubleSpinBox{background-color:#2B2B2B;color:#EEE;"
            "border:1px solid #555;border-radius:3px;padding:1px;font-size:10px}")
        self._spin_vert_share_tol.valueChanged.connect(
            self._on_vert_share_tol_changed)
        vst_row.addWidget(self._spin_vert_share_tol)
        vst_row.addStretch()
        static_lo.addLayout(vst_row)

        scroll_lo.addWidget(static_grp)


        # ---- Animation Scan Group (amber border) ----
        anim_grp = QtWidgets.QGroupBox()
        anim_grp.setStyleSheet(
            "QGroupBox{border:1px solid #FF9800;border-radius:6px;"
            "background-color:#2E2E2E;margin-top:6px}"
            "QGroupBox::title{subcontrol-origin:margin;left:10px;"
            "color:#EEE;font-size:11px;font-weight:bold}")

        anim_lo = QtWidgets.QVBoxLayout(anim_grp)
        anim_lo.setContentsMargins(6, 10, 6, 6)
        anim_lo.setSpacing(4)

        # Group header row
        anim_header = QtWidgets.QHBoxLayout()
        self._anim_grp_lbl = QtWidgets.QLabel(
            u"\u25A0 " + tr("grp_anim"))
        self._anim_grp_lbl.setStyleSheet(
            "color:#FF9800;font-size:11px;font-weight:bold")
        anim_header.addWidget(self._anim_grp_lbl)
        anim_header.addStretch()

        # Run button
        self._btn_run_anim = _mkbtn(
            tr("run_anim"), 24, "#FF9800", "#F57C00")
        self._btn_run_anim.clicked.connect(self._run_anim_scan)
        anim_header.addWidget(self._btn_run_anim)

        # Stop button (hidden by default)
        self._btn_stop_anim = _mkbtn(
            tr("btn_stop_anim"), 24, "#F44336", "#C62828")
        self._btn_stop_anim.setVisible(False)
        self._btn_stop_anim.clicked.connect(self._stop_anim_scan)
        anim_header.addWidget(self._btn_stop_anim)

        anim_lo.addLayout(anim_header)

        # ---- Inline anim settings ----
        _ss_small = "color:#AAA;font-size:10px"
        _ss_spin = ("QSpinBox{background-color:#2B2B2B;color:#EEE;"
                    "border:1px solid #555;border-radius:3px;"
                    "padding:1px;font-size:10px}")
        _ss_cb = ("QCheckBox{color:#AAA;font-size:10px}"
                  "QCheckBox::indicator{width:12px;height:12px}")

        # Frame range row
        fr_row = QtWidgets.QHBoxLayout()
        self._cb_use_timeline = QtWidgets.QCheckBox(tr("chk_use_timeline"))
        self._cb_use_timeline.setChecked(_anim_use_timeline[0])
        self._cb_use_timeline.setStyleSheet(_ss_cb)
        self._cb_use_timeline.toggled.connect(self._on_use_timeline_toggled)
        fr_row.addWidget(self._cb_use_timeline)

        self._lbl_fr = QtWidgets.QLabel(tr("lbl_frame_range"))
        self._lbl_fr.setStyleSheet(_ss_small)
        fr_row.addWidget(self._lbl_fr)
        self._spin_anim_start = QtWidgets.QSpinBox()
        self._spin_anim_start.setRange(-100000, 100000)
        self._spin_anim_start.setFixedWidth(55)
        self._spin_anim_start.setStyleSheet(_ss_spin)
        fr_row.addWidget(self._spin_anim_start)
        fr_row.addWidget(QtWidgets.QLabel("-"))
        self._spin_anim_end = QtWidgets.QSpinBox()
        self._spin_anim_end.setRange(-100000, 100000)
        self._spin_anim_end.setFixedWidth(55)
        self._spin_anim_end.setStyleSheet(_ss_spin)
        fr_row.addWidget(self._spin_anim_end)

        self._lbl_step = QtWidgets.QLabel(tr("lbl_frame_step"))
        self._lbl_step.setStyleSheet(_ss_small)
        fr_row.addWidget(self._lbl_step)
        self._spin_anim_step = QtWidgets.QSpinBox()
        self._spin_anim_step.setRange(1, 100)
        self._spin_anim_step.setFixedWidth(40)
        self._spin_anim_step.setStyleSheet(_ss_spin)
        fr_row.addWidget(self._spin_anim_step)
        fr_row.addStretch()
        anim_lo.addLayout(fr_row)

        # Ignore static checkbox + baseline frame
        ig_row = QtWidgets.QHBoxLayout()
        self._cb_ignore_static = QtWidgets.QCheckBox(tr("chk_ignore_static"))
        self._cb_ignore_static.setChecked(_anim_ignore_static[0])
        self._cb_ignore_static.setStyleSheet(_ss_cb)
        self._cb_ignore_static.toggled.connect(self._on_ignore_static_toggled)
        ig_row.addWidget(self._cb_ignore_static)

        self._lbl_baseline = QtWidgets.QLabel(tr("lbl_baseline_frame"))
        self._lbl_baseline.setStyleSheet(_ss_small)
        ig_row.addWidget(self._lbl_baseline)
        self._spin_baseline = QtWidgets.QSpinBox()
        self._spin_baseline.setRange(-100000, 100000)
        self._spin_baseline.setValue(_anim_baseline_frame[0])
        self._spin_baseline.setFixedWidth(55)
        self._spin_baseline.setStyleSheet(_ss_spin)
        self._spin_baseline.setEnabled(_anim_ignore_static[0])
        ig_row.addWidget(self._spin_baseline)
        ig_row.addStretch()
        anim_lo.addLayout(ig_row)

        # Load initial values
        self._load_anim_settings()

        # Progress bar
        self._anim_progress = QtWidgets.QProgressBar()
        self._anim_progress.setFixedHeight(16)
        self._anim_progress.setVisible(False)
        self._anim_progress.setStyleSheet(
            "QProgressBar{border:1px solid #555;border-radius:3px;"
            "background-color:#2B2B2B;text-align:center;color:#EEE;font-size:9px}"
            "QProgressBar::chunk{background-color:#FF9800;border-radius:2px}")
        anim_lo.addWidget(self._anim_progress)

        # Anim status label
        self._anim_status_lbl = QtWidgets.QLabel("")
        self._anim_status_lbl.setStyleSheet(
            "color:#AAA;font-size:10px;padding:2px")
        anim_lo.addWidget(self._anim_status_lbl)

        scroll_lo.addWidget(anim_grp)

        scroll_lo.addStretch()

        # Finalize Check tab
        check_scroll.setWidget(check_scroll_w)
        check_tab_lo.addWidget(check_scroll)
        self._tabs.addTab(check_tab, tr("tab_check"))

        # ---- Alignment tab (vertex snap + edge width + face snap + vertex align) ----
        snap_tab = QtWidgets.QWidget()
        snap_tab_lo = QtWidgets.QVBoxLayout(snap_tab)
        snap_tab_lo.setContentsMargins(0, 0, 0, 0)
        snap_tab_lo.setSpacing(0)
        snap_scroll = QtWidgets.QScrollArea()
        snap_scroll.setWidgetResizable(True)
        snap_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        snap_scroll_w = QtWidgets.QWidget()
        snap_scroll_lo = QtWidgets.QVBoxLayout(snap_scroll_w)
        snap_scroll_lo.setContentsMargins(4, 4, 4, 4)
        snap_scroll_lo.setSpacing(8)
        _build_vertex_snap_group(self, snap_scroll_lo)
        _build_edge_snap_group(self, snap_scroll_lo)
        _build_mesh_landing_group(self, snap_scroll_lo)
        _build_vertex_align_group(self, snap_scroll_lo)
        snap_scroll_lo.addStretch()
        snap_scroll.setWidget(snap_scroll_w)
        snap_tab_lo.addWidget(snap_scroll)
        self._tabs.addTab(snap_tab, tr("tab_snap"))

        main_lo.addWidget(self._tabs)

        # ---- Status bar ----
        self._status_bar = QtWidgets.QLabel(tr("status_ready"))
        self._status_bar.setStyleSheet(
            "color:#AAA;font-size:10px;padding:4px")

        # Progress bar for static checks (hidden until running)
        self._static_progress = QtWidgets.QProgressBar()
        self._static_progress.setFixedHeight(14)
        self._static_progress.setVisible(False)
        self._static_progress.setTextVisible(True)
        self._static_progress.setStyleSheet(
            "QProgressBar{border:1px solid #555;border-radius:3px;"
            "background-color:#2B2B2B;text-align:center;color:#EEE;font-size:9px}"
            "QProgressBar::chunk{background-color:#2196F3;border-radius:2px}")

        status_row = QtWidgets.QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        status_row.addWidget(self._status_bar, 1)
        status_row.addWidget(self._static_progress, 1)
        main_lo.addLayout(status_row)

    # ------------------------------------------------------------------
    def _on_selected_only_toggled(self, checked):
        _use_selected_only[0] = checked

    def _on_self_intersect_toggled(self, checked):
        _self_intersect[0] = checked

    def _on_vert_share_tol_changed(self, value):
        _set_vert_share_tolerance(value)

    def _run_all_static(self):
        self._status_bar.setText(tr("status_checking"))
        self._btn_run_all.setEnabled(False)

        # Clear caches to ensure fresh topology data
        MayaBridge.clear_caches()

        enabled_widgets = [w for w in self._check_widgets
                            if w.check_item.enabled]
        n_checks = len(enabled_widgets)

        # Show progress bar
        self._static_progress.setVisible(True)
        self._static_progress.setMaximum(max(1, n_checks))
        self._static_progress.setValue(0)
        self._status_bar.setVisible(False)
        QtWidgets.QApplication.processEvents()

        total = 0
        for idx, widget in enumerate(enabled_widgets):
            self._static_progress.setFormat(
                u"{0} ({1}/{2})".format(widget.check_item.label, idx + 1, n_checks))
            QtWidgets.QApplication.processEvents()
            widget.check_item.run_check()
            widget._update_ui()
            total += len(widget.check_item.issues)
            self._static_progress.setValue(idx + 1)
            QtWidgets.QApplication.processEvents()

        # Hide progress bar
        self._static_progress.setVisible(False)
        self._status_bar.setVisible(True)

        self._btn_run_all.setEnabled(True)
        total_elapsed = sum(
            getattr(w.check_item, "elapsed_sec", 0.0)
            for w in self._check_widgets if w.check_item.enabled)
        self._status_bar.setText(
            tr("status_done", count=total)
            + "  |  {0:.2f}s".format(total_elapsed))
        self._btn_static_results.setEnabled(True)
        self._refresh_result_window()

        # Auto-show results window if any issues were found
        if total > 0:
            self._show_static_results()

    def _on_check_done(self, check_item):
        any_results = any(len(ci.issues) > 0 for ci in self._check_instances)
        any_run = any(ci.status != "unchecked" for ci in self._check_instances)
        self._btn_static_results.setEnabled(any_run)
        total = sum(len(ci.issues) for ci in self._check_instances)
        elapsed = getattr(check_item, "elapsed_sec", 0.0)
        self._status_bar.setText(
            tr("status_done", count=total)
            + "  |  {0:.2f}s".format(elapsed))
        self._refresh_result_window()

        # Auto-show results window if any issues were found
        if len(check_item.issues) > 0:
            self._show_static_results()

    def _refresh_result_window(self):
        if self._result_window and not self._result_window.isHidden():
            self._result_window.populate(self._check_instances)

    def _show_static_results(self):
        if self._result_window is None:
            self._result_window = StaticResultWindow(
                self._check_instances, parent=self)
        else:
            self._result_window.populate(self._check_instances)
        self._result_window.show()
        self._result_window.raise_()

    # ------------------------------------------------------------------
    # Animation Scan
    # ------------------------------------------------------------------
    def _load_anim_settings(self):
        """Load anim settings into inline widgets."""
        if MAYA_AVAILABLE and _anim_use_timeline[0]:
            try:
                self._spin_anim_start.setValue(
                    int(cmds.playbackOptions(query=True, minTime=True)))
                self._spin_anim_end.setValue(
                    int(cmds.playbackOptions(query=True, maxTime=True)))
            except Exception:
                self._spin_anim_start.setValue(_anim_start_frame[0])
                self._spin_anim_end.setValue(_anim_end_frame[0])
        else:
            self._spin_anim_start.setValue(_anim_start_frame[0])
            self._spin_anim_end.setValue(_anim_end_frame[0])
        self._spin_anim_step.setValue(_anim_step[0])

    def _on_depth_threshold_changed(self, val):
        _depth_threshold[0] = val

    def _on_use_timeline_toggled(self, checked):
        _anim_use_timeline[0] = checked
        if checked and MAYA_AVAILABLE:
            try:
                self._spin_anim_start.setValue(
                    int(cmds.playbackOptions(query=True, minTime=True)))
                self._spin_anim_end.setValue(
                    int(cmds.playbackOptions(query=True, maxTime=True)))
            except Exception:
                pass

    def _on_ignore_static_toggled(self, checked):
        _anim_ignore_static[0] = checked
        self._spin_baseline.setEnabled(checked)

    def _save_anim_settings(self):
        """Save inline anim settings to globals before scan."""
        _anim_use_timeline[0] = self._cb_use_timeline.isChecked()
        _anim_ignore_static[0] = self._cb_ignore_static.isChecked()
        _anim_baseline_frame[0] = self._spin_baseline.value()
        _anim_start_frame[0] = self._spin_anim_start.value()
        _anim_end_frame[0] = self._spin_anim_end.value()
        _anim_step[0] = self._spin_anim_step.value()

    def _run_anim_scan(self):
        if self._anim_scanning:
            return

        self._save_anim_settings()

        # Early check: bail out if no mesh pairs available
        pairs_preview = _get_pairs_to_check()
        if not pairs_preview:
            self._anim_status_lbl.setText(
                tr("status_no_meshes") if MAYA_AVAILABLE else "")
            return

        # Collect unique meshes from pairs and check if any has animation
        unique_meshes = set()
        for a, b in pairs_preview:
            unique_meshes.add(a)
            unique_meshes.add(b)
        if MAYA_AVAILABLE and not MayaBridge.any_has_animation(unique_meshes):
            self._anim_status_lbl.setText(tr("status_no_anim"))
            return

        self._anim_scanning  = True
        self._anim_cancelled = False
        self._anim_results   = []

        # UI state
        self._btn_run_anim.setVisible(False)
        self._btn_stop_anim.setVisible(True)
        self._btn_run_all.setEnabled(False)
        self._anim_progress.setVisible(True)
        self._anim_progress.setValue(0)

        # Determine total frames for progress bar
        start = _anim_start_frame[0]
        end   = _anim_end_frame[0]
        step  = max(1, _anim_step[0])
        total_frames = len(range(start, end + 1, step))
        self._anim_progress.setMaximum(total_frames)
        self._anim_frame_idx = 0

        def on_progress(frame, total, issues):
            self._anim_frame_idx += 1
            self._anim_progress.setValue(
                min(self._anim_frame_idx, total_frames))
            self._anim_status_lbl.setText(
                tr("anim_scanning",
                   frame=self._anim_frame_idx, total=total_frames))
            QtWidgets.QApplication.processEvents()

        def is_cancelled():
            QtWidgets.QApplication.processEvents()
            return self._anim_cancelled

        scanner = AnimationScanner(
            progress_cb=on_progress, cancelled_cb=is_cancelled)
        results = scanner.scan()

        # Scan finished
        self._anim_scanning = False
        self._anim_results  = results
        self._btn_run_anim.setVisible(True)
        self._btn_stop_anim.setVisible(False)
        self._btn_run_all.setEnabled(True)
        self._anim_progress.setVisible(False)

        if self._anim_cancelled:
            self._anim_status_lbl.setText(tr("anim_cancelled"))
        else:
            frames_with_issues = len(results)
            msg = tr("anim_done", count=frames_with_issues)
            if _anim_ignore_static[0]:
                msg += "  (baseline filtered)"
            msg += "  |  {0:.2f}s".format(getattr(scanner, "elapsed_sec", 0.0))
            self._anim_status_lbl.setText(msg)

        if results:
            self._btn_anim_results.setEnabled(True)
            self._show_anim_results()

    def _stop_anim_scan(self):
        self._anim_cancelled = True

    def _show_anim_results(self):
        if self._anim_result_window is None:
            self._anim_result_window = AnimResultWindow(parent=self)
        self._anim_result_window.populate(self._anim_results)
        self._anim_result_window.show()
        self._anim_result_window.raise_()

    # ------------------------------------------------------------------
    def _toggle_lang(self):
        global _current_lang
        _current_lang = LANG_JP if _current_lang == LANG_EN else LANG_EN
        self._refresh_labels()

    def _refresh_labels(self):
        self._title_lbl.setText(
            u"<b>{0}</b> <span style='color:#888;font-size:10px'>v{1}</span>".format(
                tr("window_title"), VERSION))
        self.setWindowTitle(tr("window_title"))
        self._lang_btn.setText(tr("btn_lang"))
        self._btn_static_results.setText(tr("btn_static_results"))
        self._btn_anim_results.setText(tr("btn_anim_results"))
        self._btn_run_all.setText(tr("run_static"))
        self._static_grp_lbl.setText(u"\u25A0 " + tr("grp_static"))
        self._anim_grp_lbl.setText(u"\u25A0 " + tr("grp_anim"))
        self._btn_run_anim.setText(tr("run_anim"))
        self._btn_stop_anim.setText(tr("btn_stop_anim"))
        self._status_bar.setText(tr("status_ready"))
        self._cb_selected_only.setText(tr("chk_selected_only"))
        self._cb_self_intersect.setText(tr("chk_self_intersect"))
        self._lbl_depth_thresh.setText(tr("lbl_depth_threshold"))
        self._lbl_vert_share_tol.setText(tr("lbl_vert_share_tol"))
        self._lbl_vert_share_tol.setToolTip(tr("tip_vert_share_tol"))
        self._spin_vert_share_tol.setToolTip(tr("tip_vert_share_tol"))
        # Mesh Landing labels
        _ml_refresh_labels(self)
        # Tab labels
        try:
            self._tabs.setTabText(0, tr("tab_check"))
            self._tabs.setTabText(1, tr("tab_snap"))
        except Exception:
            pass
        # Vertex Snap labels
        _vs_refresh_labels(self)
        # Edge Snap labels
        _es_refresh_labels(self)
        # Vertex Align labels
        _va_refresh_labels(self)
        self._cb_use_timeline.setText(tr("chk_use_timeline"))
        self._lbl_fr.setText(tr("lbl_frame_range"))
        self._lbl_step.setText(tr("lbl_frame_step"))
        self._cb_ignore_static.setText(tr("chk_ignore_static"))
        self._lbl_baseline.setText(tr("lbl_baseline_frame"))
        for w in self._check_widgets:
            w.refresh_labels()
        if self._result_window:
            self._result_window.refresh_labels()
            self._result_window.populate(self._check_instances)
        if self._anim_result_window:
            self._anim_result_window.refresh_labels()

    # ------------------------------------------------------------------
    def _open_help(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(tr("help_title"))
        dlg.setWindowFlags(dlg.windowFlags() | QtCore.Qt.Tool)
        dlg.setMinimumSize(560, 520)
        dlg.setStyleSheet(
            "QDialog{background-color:#333}"
            "QTextBrowser{background-color:#2B2B2B;color:#EEE;"
            "border:1px solid #444;padding:8px;font-size:11px}"
            "QTabWidget::pane{border:1px solid #444;background:#2B2B2B;top:-1px}"
            "QTabBar::tab{background:#3C3C3C;color:#BBB;padding:6px 14px;"
            "border:1px solid #444;border-bottom:none;margin-right:1px;"
            "font-size:11px}"
            "QTabBar::tab:selected{background:#2B2B2B;color:#EEE;font-weight:bold}")
        lo = QtWidgets.QVBoxLayout(dlg)
        lo.setContentsMargins(8, 8, 8, 8)
        lo.setSpacing(6)
        tabs = QtWidgets.QTabWidget()
        for tab_key, body_key in [
                ("tab_check", "help_body_check"),
                ("tab_snap",  "help_body_snap")]:
            tb = QtWidgets.QTextBrowser()
            tb.setHtml(tr(body_key))
            tb.setOpenExternalLinks(True)
            tabs.addTab(tb, tr(tab_key))
        lo.addWidget(tabs)
        btn_lo = QtWidgets.QHBoxLayout()
        btn_lo.addStretch()
        close = _mkbtn(tr("btn_close"), 26, "#555", "#444")
        close.clicked.connect(dlg.accept)
        btn_lo.addWidget(close)
        lo.addLayout(btn_lo)
        dlg.exec_()

    # ------------------------------------------------------------------
    def _on_reload(self):
        global _saved_geometry, _saved_lang
        geo = self.geometry()
        _saved_geometry = (geo.x(), geo.y(), geo.width(), geo.height())
        _saved_lang = _current_lang
        self.close()

        # Find the module that contains this class.
        # __module__ may be '__main__' when run from Script Editor,
        # so fall back to searching sys.modules by filename or known name.
        mn = self.__class__.__module__
        mod = sys.modules.get(mn)

        if mod is None or mn == "__main__":
            # Search sys.modules for the module containing this file
            for name, m in list(sys.modules.items()):
                if name == "__main__":
                    continue
                f = getattr(m, "__file__", None)
                if f and "DW_CollisionCheck" in f:
                    mn = name
                    mod = m
                    break

        if mod is not None and mn != "__main__":
            _reload(mod)
            mod._saved_geometry = _saved_geometry
            mod._saved_lang = _saved_lang
            mod.show()
        else:
            # Fallback: try the known module name directly
            if "DW_CollisionCheck" in sys.modules:
                mod = sys.modules["DW_CollisionCheck"]
                _reload(mod)
                mod._saved_geometry = _saved_geometry
                mod._saved_lang = _saved_lang
                mod.show()

    def _on_check_update(self):
        """Trigger the auto-update workflow (interactive)."""
        result = check_for_updates(silent=False)
        self._set_update_btn_state(result)

    def _set_update_btn_state(self, state):
        """Update the button color based on version-check state.
        state: 'latest' | 'newer_available' | 'unknown'
        """
        if state == "newer_available":
            bg = "#D32F2F"        # red
            hv = "#E53935"
            tip = tr("btn_update") + " (NEW!)"
        elif state == "latest":
            bg = "#1976D2"        # blue
            hv = "#2196F3"
            tip = tr("btn_update") + " (up to date)"
        else:
            bg = "#555"           # gray
            hv = "#9C27B0"
            tip = tr("btn_update")
        self._update_btn.setStyleSheet(
            "QPushButton{{background-color:{0};color:#EEE;"
            "border:1px solid #777;border-radius:3px;font-size:12px}}"
            "QPushButton:hover{{background-color:{1}}}".format(bg, hv))
        self._update_btn.setToolTip(tip)

    def _startup_version_check(self):
        """Background version check at startup (silent).
        Never shows any dialog; only updates the button color.
        """
        try:
            state = check_for_updates(silent=True)
            self._set_update_btn_state(state)
        except Exception:
            self._set_update_btn_state("unknown")


def _url_read(url, timeout=10):
    """Read a URL and return the decoded string. Py2/3 compatible."""
    if PY2:
        import urllib2
        resp = urllib2.urlopen(url, timeout=timeout)
        data = resp.read()
    else:
        import urllib.request
        resp = urllib.request.urlopen(url, timeout=timeout)
        data = resp.read()
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("utf-8", errors="replace")
    return data


def _extract_remote_version(source_text):
    """Extract 'VERSION = "..."' line from source code."""
    import re
    m = re.search(r'^VERSION\s*=\s*"([^"]+)"', source_text, re.MULTILINE)
    return m.group(1) if m else None


def check_for_updates(silent=False):
    """
    Check GitHub for a newer version.

    silent=False (default, interactive):
        Shows dialogs. If a newer version is available, asks the user
        to download and installs it to Maya scripts folder.

    silent=True (background check at startup):
        Never shows any dialog. Only returns a state string.

    Returns:
        'latest'          — local version matches remote (up to date)
        'newer_available' — remote has a newer version
        'unknown'         — offline, parse error, or Maya not available
    """
    if not MAYA_AVAILABLE:
        return "unknown"

    # Fetch remote source
    try:
        source = _url_read(_GITHUB_RAW_URL, timeout=5 if silent else 10)
    except Exception as e:
        if not silent:
            QtWidgets.QMessageBox.warning(
                None, "Update Check",
                "Failed to connect to GitHub.\n{0}".format(str(e)))
        return "unknown"

    remote_ver = _extract_remote_version(source)
    if not remote_ver:
        if not silent:
            QtWidgets.QMessageBox.warning(
                None, "Update Check",
                "Could not read remote version.")
        return "unknown"

    local_ver = VERSION

    if remote_ver == local_ver:
        if not silent:
            QtWidgets.QMessageBox.information(
                None, "Update Check",
                u"\u6700\u65b0\u7248\u3067\u3059\u3002\n"
                u"Version: {0}".format(local_ver))
        return "latest"

    # Lexical comparison works for YYYY.MM.DD.HHMM format
    is_newer = remote_ver > local_ver

    if not is_newer:
        # Local is ahead of remote (dev state). Treat as up to date.
        if not silent:
            msg = (u"\u30ed\u30fc\u30ab\u30eb\u7248\u306e\u65b9\u304c\u65b0"
                   u"\u3057\u3044\u3088\u3046\u3067\u3059\u3002\n\n"
                   u"Local:  {0}\nRemote: {1}").format(local_ver, remote_ver)
            QtWidgets.QMessageBox.information(None, "Update Check", msg)
        return "latest"

    # A newer remote version exists
    if silent:
        return "newer_available"

    # Interactive: ask to download
    msg = (u"\u65b0\u3057\u3044\u30d0\u30fc\u30b8\u30e7\u30f3\u304c\u3042"
           u"\u308a\u307e\u3059\u3002\n\n"
           u"Local:  {0}\nRemote: {1}\n\n"
           u"\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9\u3057\u3066\u66f4\u65b0"
           u"\u3057\u307e\u3059\u304b\uff1f").format(local_ver, remote_ver)
    reply = QtWidgets.QMessageBox.question(
        None, "Update Check", msg,
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if reply != QtWidgets.QMessageBox.Yes:
        return "newer_available"

    # Save to Maya scripts folder
    try:
        scripts_dir = cmds.internalVar(userScriptDir=True)
        if scripts_dir.endswith("/") or scripts_dir.endswith("\\"):
            scripts_dir = scripts_dir[:-1]
        dest = os.path.join(scripts_dir, "DW_CollisionCheck.py")

        # Backup existing
        if os.path.exists(dest):
            bak = dest + ".bak"
            if os.path.exists(bak):
                try:
                    os.remove(bak)
                except Exception:
                    pass
            try:
                os.rename(dest, bak)
            except Exception:
                pass

        if PY2:
            with open(dest, "wb") as f:
                f.write(source.encode("utf-8"))
        else:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(source)

        done_msg = (u"v{0} \u306b\u66f4\u65b0\u3057\u307e\u3057\u305f\u3002\n\n"
                    u"\u4fdd\u5b58\u5148: {1}\n\n"
                    u"\u30c4\u30fc\u30eb\u3092\u518d\u8d77\u52d5\u3057\u3066"
                    u"\u304f\u3060\u3055\u3044\u3002\n"
                    u"(\u30e1\u30a4\u30f3\u30a6\u30a3\u30f3\u30c9\u30a6\u306e"
                    u"\u30ea\u30ed\u30fc\u30c9\u30dc\u30bf\u30f3\u3092\u30af"
                    u"\u30ea\u30c3\u30af)").format(remote_ver, dest)
        QtWidgets.QMessageBox.information(None, "Update Check", done_msg)
        return "latest"  # after update, local matches remote
    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None, "Update Check",
            "Failed to save update.\n{0}".format(str(e)))
        return "newer_available"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def show():
    global _saved_geometry, _saved_lang, _current_lang

    # Close existing instance
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, CollisionCheckToolWindow):
            w.close()
            w.deleteLater()

    if _saved_lang:
        _current_lang = _saved_lang
        _saved_lang = None

    win = CollisionCheckToolWindow()
    win.show()

    # Background version check. Delayed so the UI shows immediately
    # and the user never waits for the network. Never blocks or fails.
    try:
        QtCore.QTimer.singleShot(500, win._startup_version_check)
    except Exception:
        pass

    return win


if __name__ == "__main__":
    # Standalone test (outside Maya)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    win = show()
    app.exec_()

