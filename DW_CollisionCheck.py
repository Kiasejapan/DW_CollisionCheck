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
VERSION = "2026.04.16.1055"

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

    # ---- Move-to-Origin group ------------------------------------------
    "grp_move":             {"en": "Move to Origin (BETA)",         "jp": u"\u539f\u70b9\u79fb\u52d5\uff08BETA\uff09"},
    "run_move_all":         {"en": "Run Move All",                  "jp": u"\u4e00\u62ec\u5b9f\u884c"},
    "lbl_move_offset":      {"en": "Stop offset:",                  "jp": u"\u505c\u6b62\u30aa\u30d5\u30bb\u30c3\u30c8:"},
    "tip_move_offset":      {"en": "Distance to keep between the moved element and the collision/origin.",
                             "jp": u"\u79fb\u52d5\u8981\u7d20\u3068\u8870\u7a81\u9762/\u539f\u70b9\u3068\u306e\u9593\u306b\u6b8b\u3059\u9694\u305f\u308a\u8ddd\u96e2\u3002"},

    "move_mesh":            {"en": "Move Mesh",                     "jp": u"\u30e1\u30c3\u30b7\u30e5\u3092\u539f\u70b9\u3078"},
    "move_mesh_desc":       {"en": "Move each selected mesh transform toward the origin until it nearly touches another mesh or the origin.",
                             "jp": u"\u9078\u629e\u30e1\u30c3\u30b7\u30e5\u3092\u4ed6\u30e1\u30c3\u30b7\u30e5\u307e\u305f\u306f\u539f\u70b9\u306b\u63a5\u3059\u308b\u624b\u524d\u307e\u3067\u539f\u70b9\u65b9\u5411\u306b\u79fb\u52d5\u3002"},
    "move_vertex":          {"en": "Move Vertices",                 "jp": u"\u9802\u70b9\u3092\u539f\u70b9\u3078"},
    "move_vertex_desc":     {"en": "Move each selected vertex individually toward the origin.",
                             "jp": u"\u9078\u629e\u9802\u70b9\u3092\u3001\u305d\u308c\u305e\u308c\u500b\u5225\u306b\u539f\u70b9\u65b9\u5411\u3078\u79fb\u52d5\u3002"},
    "move_edge":            {"en": "Move Edges",                    "jp": u"\u30a8\u30c3\u30b8\u3092\u539f\u70b9\u3078"},
    "move_edge_desc":       {"en": "Move each selected edge (as a rigid pair of endpoints) toward the origin.",
                             "jp": u"\u9078\u629e\u30a8\u30c3\u30b8\u3092\u4e21\u7aef\u70b9\u3054\u3068\u306b\u539f\u70b9\u65b9\u5411\u3078\u79fb\u52d5\u3002"},
    "move_face":            {"en": "Move Faces",                    "jp": u"\u30d5\u30a7\u30fc\u30b9\u3092\u539f\u70b9\u3078"},
    "move_face_desc":       {"en": "Move each selected face (with all its vertices) toward the origin.",
                             "jp": u"\u9078\u629e\u30d5\u30a7\u30fc\u30b9\u3092\u9802\u70b9\u3054\u3068\u539f\u70b9\u65b9\u5411\u3078\u79fb\u52d5\u3002"},

    "move_status_done":     {"en": "Moved {n} element(s)",          "jp": u"{n} \u8981\u7d20\u3092\u79fb\u52d5\u3057\u307e\u3057\u305f"},
    "move_status_skipped":  {"en": "{n} skipped (near origin / no center)",
                             "jp": u"{n} \u8981\u7d20\u3092\u30b9\u30ad\u30c3\u30d7\uff08\u539f\u70b9\u8fd1\u508d/\u4e2d\u5fc3\u4e0d\u660e\uff09"},
    "move_status_no_selection": {"en": "No matching selection for this operation.",
                                  "jp": u"\u3053\u306e\u64cd\u4f5c\u306b\u5408\u3046\u9078\u629e\u304c\u3042\u308a\u307e\u305b\u3093\u3002"},

    # ---- Tabs --------------------------------------------------------
    "tab_check":            {"en": "Check",                         "jp": u"\u30c1\u30a7\u30c3\u30af"},
    "tab_other":            {"en": "Other",                         "jp": u"\u305d\u306e\u4ed6"},

    # ---- Move axis / mode --------------------------------------------
    "lbl_move_axis":        {"en": "Axis:",                         "jp": u"\u8ef8:"},
    "tip_move_axis":        {"en": "Direction is along this axis. Sign is auto (toward origin from element center).",
                             "jp": u"\u9078\u629e\u8ef8\u306b\u6cbf\u3063\u3066\u79fb\u52d5\u3057\u307e\u3059\u3002\u6b63\u8ca0\u306f\u8981\u7d20\u4e2d\u5fc3\u304b\u3089\u539f\u70b9\u65b9\u5411\u306b\u81ea\u52d5\u5224\u5b9a\u3002"},
    "axis_x":               {"en": "X",                             "jp": u"X"},
    "axis_y":               {"en": "Y",                             "jp": u"Y"},
    "axis_z":               {"en": "Z",                             "jp": u"Z"},

    "btn_move":             {"en": "Move",                          "jp": u"\u79fb\u52d5"},
    "mode_rigid":           {"en": "Keep Shape",                    "jp": u"\u5f62\u72b6\u7dad\u6301"},
    "mode_individual":      {"en": "Free",                          "jp": u"\u500b\u5225\u5909\u5f62"},
    "tip_mode_rigid":       {"en": "Move the entire selection as ONE rigid element (preserves shape).",
                             "jp": u"\u9078\u629e\u5168\u4f53\u3092\u4e00\u3064\u306e\u5264\u4f53\u3068\u3057\u3066\u79fb\u52d5\uff08\u5f62\u72b6\u3092\u4fdd\u3061\u307e\u3059\uff09\u3002"},
    "tip_mode_individual":  {"en": "Move each sub-element (vertex/edge/face) independently (shape may collapse).",
                             "jp": u"\u5404\u8981\u7d20\uff08\u9802\u70b9/\u30a8\u30c3\u30b8/\u30d5\u30a7\u30fc\u30b9\uff09\u3092\u500b\u5225\u306b\u79fb\u52d5\uff08\u5f62\u72b6\u306f\u5d29\u308c\u308b\u53ef\u80fd\u6027\u3042\u308a\uff09\u3002"},    "anim_scanning":        {"en": "Scanning frame {frame}/{total}...",
                             "jp": u"\u30d5\u30ec\u30fc\u30e0 {frame}/{total} \u3092\u30b9\u30ad\u30e3\u30f3\u4e2d..."},
    "anim_done":            {"en": "Animation scan done: {count} frame(s) with issues.",
                             "jp": u"\u30a2\u30cb\u30e1\u30b9\u30ad\u30e3\u30f3\u5b8c\u4e86: {count} \u30d5\u30ec\u30fc\u30e0\u3067\u554f\u984c\u691c\u51fa\u3002"},
    "anim_cancelled":       {"en": "Animation scan cancelled.",     "jp": u"\u30a2\u30cb\u30e1\u30b9\u30ad\u30e3\u30f3\u304c\u30ad\u30e3\u30f3\u30bb\u30eb\u3055\u308c\u307e\u3057\u305f\u3002"},
    "result_title_anim":    {"en": "Animation Scan Results",        "jp": u"\u30a2\u30cb\u30e1\u30b9\u30ad\u30e3\u30f3\u7d50\u679c"},
    "col_frame":            {"en": "Frame",                         "jp": u"\u30d5\u30ec\u30fc\u30e0"},
    "btn_goto_frame":       {"en": "Go to Frame",                   "jp": u"\u30d5\u30ec\u30fc\u30e0\u3078\u79fb\u52d5"},
    "lbl_anim_summary":     {"en": "{total} issues across {frames} frame(s)",
                             "jp": u"{frames} \u30d5\u30ec\u30fc\u30e0\u3067 {total} \u4ef6\u306e\u554f\u984c"},
    "help_text": {
        "en": "<h3>DW Collision Check</h3>"
              "<p>Detects polygon intersections (hair/cloth collisions) in the current frame or across an animation range.</p>"
              "<h4>Check Tab</h4>"
              "<ul><li><b>Intersection Check</b>: Finds faces that physically penetrate each other.</li>"
              "<li><b>Overlap Check</b>: Finds coplanar overlapping faces (z-fighting / double faces).</li>"
              "<li><b>Animation Scan</b>: Sweeps a frame range and reports collisions per frame, with optional baseline filtering.</li></ul>"
              "<p><b>Depth threshold</b>: minimum penetration depth to report.<br>"
              "<b>Vertex-share tolerance</b>: triangles sharing a vertex within this distance are skipped.</p>"
              "<h4>Other Tab</h4>"
              "<ul><li><b>Move to Origin (BETA)</b>: Moves the selection toward the world origin along the chosen axis (X/Y/Z), stopping just before another mesh or the origin.</li>"
              "<ul><li><i>Keep Shape</i>: the entire selection moves as one rigid element.</li>"
              "<li><i>Free</i>: each sub-element (vertex/edge/face) moves independently.</li>"
              "<li><i>Stop offset</i>: distance kept between the moved element and the collision/origin.</li></ul></ul>"
              "<h4>Usage</h4>"
              "<ol><li>Select meshes/components in the viewport.</li>"
              "<li>For checks: click [Check] per item or [Run Static Checks].</li>"
              "<li>For moves: pick the axis, mode, then click [Move] per item or [Run Move All].</li>"
              "<li>Click a result row to select the faces in the viewport.</li></ol>",
        "jp": u"<h3>DW \u5e72\u6e09\u30c1\u30a7\u30c3\u30af</h3>"
              u"<p>\u73fe\u5728\u30d5\u30ec\u30fc\u30e0\u307e\u305f\u306f\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u7bc4\u56f2\u5185\u3067\u30dd\u30ea\u30b4\u30f3\u306e\u5e72\u6e09\uff08\u9aea\u30fb\u5e03\u306e\u523a\u3055\u308a\uff09\u3092\u691c\u51fa\u3057\u307e\u3059\u3002</p>"
              u"<h4>\u30c1\u30a7\u30c3\u30af\u30bf\u30d6</h4>"
              u"<ul><li><b>\u4ea4\u5dee\u30c1\u30a7\u30c3\u30af</b>\uff1a\u5b9f\u969b\u306b\u8cab\u901a\u3057\u3066\u3044\u308b\u30d5\u30a7\u30fc\u30b9\u3092\u691c\u51fa\u3002</li>"
              u"<li><b>\u91cd\u306a\u308a\u30c1\u30a7\u30c3\u30af</b>\uff1a\u540c\u4e00\u5e73\u9762\u4e0a\u3067\u91cd\u306a\u308b\u30d5\u30a7\u30fc\u30b9\uff08Z\u30d5\u30a1\u30a4\u30c8/\u4e8c\u91cd\u9762\uff09\u3092\u691c\u51fa\u3002</li>"
              u"<li><b>\u30a2\u30cb\u30e1\u30fc\u30b7\u30e7\u30f3\u30b9\u30ad\u30e3\u30f3</b>\uff1a\u30d5\u30ec\u30fc\u30e0\u7bc4\u56f2\u3092\u8d70\u67fb\u3057\u3066\u30d5\u30ec\u30fc\u30e0\u3054\u3068\u306e\u5e72\u6e09\u3092\u8a18\u9332\u3002\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u30d5\u30ec\u30fc\u30e0\u3092\u9664\u5916\u53ef\u80fd\u3002</li></ul>"
              u"<p><b>\u6df1\u5ea6\u95be\u5024</b>\uff1a\u5831\u544a\u3059\u308b\u6700\u5c0f\u8cab\u5165\u6df1\u3055\u3002<br>"
              u"<b>\u540c\u4e00\u9802\u70b9\u3068\u307f\u306a\u3059\u8ddd\u96e2</b>\uff1a\u3053\u306e\u8ddd\u96e2\u4ee5\u5185\u3067\u9802\u70b9\u3092\u5171\u6709\u3059\u308b\u4e09\u89d2\u5f62\u30da\u30a2\u306f\u4ea4\u5dee\u5224\u5b9a\u3092\u30b9\u30ad\u30c3\u30d7\u3002</p>"
              u"<h4>\u305d\u306e\u4ed6\u30bf\u30d6</h4>"
              u"<ul><li><b>\u539f\u70b9\u79fb\u52d5\uff08BETA\uff09</b>\uff1a\u9078\u629e\u3092\u6307\u5b9a\u8ef8\uff08X/Y/Z\uff09\u306b\u6cbf\u3063\u3066\u539f\u70b9\u65b9\u5411\u3078\u79fb\u52d5\u3057\u3001\u4ed6\u30e1\u30c3\u30b7\u30e5\u307e\u305f\u306f\u539f\u70b9\u306e\u624b\u524d\u3067\u505c\u6b62\u3002</li>"
              u"<ul><li><i>\u5f62\u72b6\u7dad\u6301</i>\uff1a\u9078\u629e\u5168\u4f53\u3092\u4e00\u3064\u306e\u5264\u4f53\u3068\u3057\u3066\u79fb\u52d5\u3002</li>"
              u"<li><i>\u500b\u5225\u5909\u5f62</i>\uff1a\u5404\u9802\u70b9/\u30a8\u30c3\u30b8/\u30d5\u30a7\u30fc\u30b9\u3092\u500b\u5225\u306b\u79fb\u52d5\u3002</li>"
              u"<li><i>\u505c\u6b62\u30aa\u30d5\u30bb\u30c3\u30c8</i>\uff1a\u8870\u7a81\u9762\u30fb\u539f\u70b9\u3068\u306e\u9593\u306b\u6b8b\u3059\u9694\u305f\u308a\u8ddd\u96e2\u3002</li></ul></ul>"
              u"<h4>\u4f7f\u3044\u65b9</h4>"
              u"<ol><li>\u30d3\u30e5\u30fc\u30dd\u30fc\u30c8\u3067\u30e1\u30c3\u30b7\u30e5\u30fb\u30b3\u30f3\u30dd\u30fc\u30cd\u30f3\u30c8\u3092\u9078\u629e\u3002</li>"
              u"<li>\u30c1\u30a7\u30c3\u30af\uff1a[\u30c1\u30a7\u30c3\u30af] \u307e\u305f\u306f [\u30b9\u30bf\u30c6\u30a3\u30c3\u30af\u5b9f\u884c]\u3002</li>"
              u"<li>\u79fb\u52d5\uff1a\u8ef8\u3068\u30e2\u30fc\u30c9\u3092\u9078\u3093\u3067 [\u79fb\u52d5] \u307e\u305f\u306f [\u4e00\u62ec\u5b9f\u884c]\u3002</li>"
              u"<li>\u7d50\u679c\u884c\u3092\u30af\u30ea\u30c3\u30af\u3059\u308b\u3068\u30d3\u30e5\u30fc\u30dd\u30fc\u30c8\u3067\u30d5\u30a7\u30fc\u30b9\u3092\u9078\u629e\u3002</li></ol>",
    },
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
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(
            _TABLE_SS + "QTableWidget{alternate-background-color:#323232}")
        self._table.verticalHeader().setVisible(False)
        self._table.currentCellChanged.connect(self._on_row_changed)
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

    def _on_row_changed(self, row, col, prev_row, prev_col):
        if row < 0 or row >= len(self._rows):
            return
        self._highlight_row(row)

    def _highlight_row(self, row):
        """Select the grouped faces stored in the issue."""
        if not MAYA_AVAILABLE:
            return
        data = self._rows[row]
        issue = data["issue"]
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

    def _select_current_faces(self):
        row = self._table.currentRow()
        if row >= 0:
            self._highlight_row(row)

    def refresh_labels(self):
        """Re-apply localized strings (called on language toggle)."""
        self.setWindowTitle(tr("result_title_static"))
        headers = [tr("col_status"), tr("col_check"),
                   tr("col_mesh_a"), tr("col_mesh_b"), tr("col_detail")]
        for i, h in enumerate(headers):
            self._table.horizontalHeaderItem(i).setText(h)
        self._btn_select.setText(tr("btn_select_faces"))



# ---------------------------------------------------------------------------
# CheckItemWidget  (reusable row widget — matches reference architecture)
# ---------------------------------------------------------------------------
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

        # Mode toggle (Rigid/Indiv) - only for items declaring supports_modes
        self._btn_mode = None
        if getattr(self.check_item, "supports_modes", False):
            self._btn_mode = QtWidgets.QPushButton(self._mode_label())
            self._btn_mode.setFixedSize(74, 22)
            self._btn_mode.setCheckable(True)
            self._btn_mode.setChecked(
                getattr(self.check_item, "mode", u"") == u"individual")
            self._btn_mode.setStyleSheet(
                "QPushButton{background-color:#455A64;color:#EEE;"
                "border:1px solid #607D8B;border-radius:3px;font-size:10px}"
                "QPushButton:hover{background-color:#546E7A}"
                "QPushButton:checked{background-color:#FF7043;color:white;"
                "border-color:#FF8A65}")
            self._btn_mode.setToolTip(self._mode_tip())
            self._btn_mode.toggled.connect(self._on_mode_toggled)
            hl.addWidget(self._btn_mode)

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
        if self._btn_mode is not None:
            self._btn_mode.setText(self._mode_label())
            self._btn_mode.setToolTip(self._mode_tip())

    def _action_button_label(self):
        # Move/action items use btn_move; checks use btn_check
        if getattr(self.check_item, "is_action", False):
            return tr("btn_move")
        return tr("btn_check")

    def _mode_label(self):
        m = getattr(self.check_item, "mode", u"rigid")
        return tr("mode_individual" if m == u"individual" else "mode_rigid")

    def _mode_tip(self):
        m = getattr(self.check_item, "mode", u"rigid")
        return tr("tip_mode_individual" if m == u"individual" else "tip_mode_rigid")

    def _on_mode_toggled(self, checked):
        new_mode = u"individual" if checked else u"rigid"
        if hasattr(self.check_item, "set_mode"):
            self.check_item.set_mode(new_mode)
        if self._btn_mode is not None:
            self._btn_mode.setText(self._mode_label())
            self._btn_mode.setToolTip(self._mode_tip())

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
        self.setMinimumWidth(440)
        self.setMinimumHeight(320)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setStyleSheet(_MAIN_SS)

        self._check_instances = []   # list of CheckItem instances
        self._check_widgets   = []   # list of CheckItemWidget
        self._result_window   = None
        self._anim_result_window = None
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

        # ---- Tab widget (Check / Other) ----
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

        # ---- Move-to-Origin Group (purple border) - placed in Other tab --
        move_grp = QtWidgets.QGroupBox()
        move_grp.setStyleSheet(
            "QGroupBox{border:1px solid #9C27B0;border-radius:6px;"
            "background-color:#2E2E2E;margin-top:6px}"
            "QGroupBox::title{subcontrol-origin:margin;left:10px;"
            "color:#EEE;font-size:11px;font-weight:bold}")

        move_lo = QtWidgets.QVBoxLayout(move_grp)
        move_lo.setContentsMargins(6, 10, 6, 6)
        move_lo.setSpacing(4)

        # Group header row
        move_header = QtWidgets.QHBoxLayout()
        self._move_grp_lbl = QtWidgets.QLabel(
            u"\u25A0 " + tr("grp_move"))
        self._move_grp_lbl.setStyleSheet(
            "color:#CE93D8;font-size:11px;font-weight:bold")
        move_header.addWidget(self._move_grp_lbl)
        move_header.addStretch()
        self._btn_run_move_all = _mkbtn(
            tr("run_move_all"), 24, "#9C27B0", "#7B1FA2")
        self._btn_run_move_all.clicked.connect(self._run_all_move)
        move_header.addWidget(self._btn_run_move_all)
        move_lo.addLayout(move_header)

        # Axis selector row (X / Y / Z radio)
        axis_row = QtWidgets.QHBoxLayout()
        self._lbl_move_axis = QtWidgets.QLabel(tr("lbl_move_axis"))
        self._lbl_move_axis.setStyleSheet("color:#AAA;font-size:10px")
        self._lbl_move_axis.setToolTip(tr("tip_move_axis"))
        axis_row.addWidget(self._lbl_move_axis)
        self._axis_group = QtWidgets.QButtonGroup(self)
        self._rb_axis_x = QtWidgets.QRadioButton(tr("axis_x"))
        self._rb_axis_y = QtWidgets.QRadioButton(tr("axis_y"))
        self._rb_axis_z = QtWidgets.QRadioButton(tr("axis_z"))
        for i, rb in enumerate(
                (self._rb_axis_x, self._rb_axis_y, self._rb_axis_z)):
            rb.setStyleSheet(
                "QRadioButton{color:#EEE;font-size:11px;padding:0px 4px}"
                "QRadioButton::indicator{width:11px;height:11px}")
            rb.setToolTip(tr("tip_move_axis"))
            self._axis_group.addButton(rb, i)
            axis_row.addWidget(rb)
        # default selection from module state
        cur = _get_move_axis()
        (self._rb_axis_x, self._rb_axis_y, self._rb_axis_z)[cur].setChecked(True)
        try:
            self._axis_group.idClicked.connect(self._on_axis_changed)
        except AttributeError:
            # PySide2 older signature fallback
            self._axis_group.buttonClicked[int].connect(self._on_axis_changed)
        axis_row.addStretch()
        move_lo.addLayout(axis_row)

        # MoveItem widgets (re-use CheckItemWidget for consistent UI)
        self._move_instances = []
        self._move_widgets   = []
        for cls in MOVE_ITEMS:
            inst = cls()
            widget = CheckItemWidget(inst, has_settings=False)
            widget.check_requested.connect(self._on_move_done)
            self._move_instances.append(inst)
            self._move_widgets.append(widget)
            move_lo.addWidget(widget)

        # Stop-offset row
        off_row = QtWidgets.QHBoxLayout()
        self._lbl_move_offset = QtWidgets.QLabel(tr("lbl_move_offset"))
        self._lbl_move_offset.setStyleSheet("color:#AAA;font-size:10px")
        self._lbl_move_offset.setToolTip(tr("tip_move_offset"))
        off_row.addWidget(self._lbl_move_offset)
        self._spin_move_offset = QtWidgets.QDoubleSpinBox()
        self._spin_move_offset.setRange(0.0, 1.0e6)
        self._spin_move_offset.setDecimals(4)
        self._spin_move_offset.setSingleStep(0.001)
        self._spin_move_offset.setValue(_get_move_offset())
        self._spin_move_offset.setFixedWidth(85)
        self._spin_move_offset.setToolTip(tr("tip_move_offset"))
        self._spin_move_offset.setStyleSheet(
            "QDoubleSpinBox{background-color:#2B2B2B;color:#EEE;"
            "border:1px solid #555;border-radius:3px;padding:1px;font-size:10px}")
        self._spin_move_offset.valueChanged.connect(
            self._on_move_offset_changed)
        off_row.addWidget(self._spin_move_offset)
        off_row.addStretch()
        move_lo.addLayout(off_row)

        # NOTE: move_grp is added to Other tab below, not to scroll_lo

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

        # ---- Other tab (auxiliary tools, contains Move-to-Origin) ----
        other_tab = QtWidgets.QWidget()
        other_tab_lo = QtWidgets.QVBoxLayout(other_tab)
        other_tab_lo.setContentsMargins(0, 0, 0, 0)
        other_tab_lo.setSpacing(0)
        other_scroll = QtWidgets.QScrollArea()
        other_scroll.setWidgetResizable(True)
        other_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        other_scroll_w = QtWidgets.QWidget()
        other_scroll_lo = QtWidgets.QVBoxLayout(other_scroll_w)
        other_scroll_lo.setContentsMargins(4, 4, 4, 4)
        other_scroll_lo.setSpacing(8)
        other_scroll_lo.addWidget(move_grp)
        other_scroll_lo.addStretch()
        other_scroll.setWidget(other_scroll_w)
        other_tab_lo.addWidget(other_scroll)
        self._tabs.addTab(other_tab, tr("tab_other"))

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

    # ---- Move-to-Origin handlers --------------------------------------
    def _on_move_offset_changed(self, value):
        _set_move_offset(value)

    def _on_axis_changed(self, idx):
        _set_move_axis(int(idx))

    def _on_axis_changed(self, idx):
        _set_move_axis(int(idx))

    def _run_all_move(self):
        """Run every move item that has a matching selection."""
        self._status_bar.setText(tr("status_checking"))
        QtWidgets.QApplication.processEvents()
        any_done = False
        last_summary = u""
        for w in self._move_widgets:
            inst = w.check_item
            inst.run_check()  # actually performs the move
            w._update_ui()
            if inst.status == "pass" or inst.issues:
                any_done = True
                if hasattr(inst, "_last_summary") and inst._last_summary:
                    last_summary = inst._last_summary
                elif inst.issues:
                    last_summary = inst.issues[0].get("detail", u"")
        if any_done and last_summary:
            self._status_bar.setText(last_summary)
        else:
            self._status_bar.setText(tr("status_ready"))

    def _on_move_done(self, check_item):
        """Single move-item completed (badge / status bar update)."""
        # Prefer the in-instance summary when fully successful
        msg = u""
        if hasattr(check_item, "_last_summary") and check_item._last_summary:
            msg = check_item._last_summary
        elif check_item.issues:
            msg = check_item.issues[0].get("detail", u"")
        if msg:
            self._status_bar.setText(msg)

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
        # Move-to-Origin labels
        self._move_grp_lbl.setText(u"\u25A0 " + tr("grp_move"))
        self._btn_run_move_all.setText(tr("run_move_all"))
        self._lbl_move_offset.setText(tr("lbl_move_offset"))
        self._lbl_move_offset.setToolTip(tr("tip_move_offset"))
        self._spin_move_offset.setToolTip(tr("tip_move_offset"))
        self._lbl_move_axis.setText(tr("lbl_move_axis"))
        self._lbl_move_axis.setToolTip(tr("tip_move_axis"))
        self._rb_axis_x.setText(tr("axis_x"))
        self._rb_axis_y.setText(tr("axis_y"))
        self._rb_axis_z.setText(tr("axis_z"))
        for rb in (self._rb_axis_x, self._rb_axis_y, self._rb_axis_z):
            rb.setToolTip(tr("tip_move_axis"))
        # Tab labels
        try:
            self._tabs.setTabText(0, tr("tab_check"))
            self._tabs.setTabText(1, tr("tab_other"))
        except Exception:
            pass
        for w in self._move_widgets:
            w.refresh_labels()
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
        dlg.setWindowTitle("Help")
        dlg.setWindowFlags(dlg.windowFlags() | QtCore.Qt.Tool)
        dlg.setMinimumSize(400, 300)
        dlg.setStyleSheet("QDialog{background-color:#333} QTextBrowser{background-color:#2B2B2B;color:#EEE;border:none}")
        lo = QtWidgets.QVBoxLayout(dlg)
        tb = QtWidgets.QTextBrowser()
        tb.setHtml(tr("help_text"))
        lo.addWidget(tb)
        btn_lo = QtWidgets.QHBoxLayout()
        btn_lo.addStretch()
        close = _mkbtn("Close", 26, "#555", "#444")
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



# ---------------------------------------------------------------------------
# Auto-update from GitHub
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Origin-directed Raycaster (Maya OpenMaya api1, MFnMesh.allIntersections)
# ---------------------------------------------------------------------------
# Casts a ray from a world-space point toward the world origin (0,0,0)
# and returns the list of valid hit distances against ALL visible mesh
# shapes in the scene.
#
# Filtering:
#   - self-hit (distance <= EPSILON) is removed
#   - NaN / inf are removed
#   - vertices coincident with the source within `_vert_share_tol` are
#     treated as "shared" and the corresponding face is filtered out
#     (re-uses the same tolerance as IntersectionCheck).
# ---------------------------------------------------------------------------

_RAY_EPS = 1.0e-5  # epsilon used for self-hit / numerical filtering


class OriginRaycaster(object):
    """
    Reusable ray-caster. Build once per move-batch and re-use across
    many source points; accelParams are cached per shape.
    """

    def __init__(self, target_shapes=None):
        """
        target_shapes: list of mesh shape names. None = all visible meshes.
        """
        if target_shapes is None:
            target_shapes = MayaBridge.get_mesh_shapes()
        self._fn_cache  = {}   # shape -> MFnMesh
        self._acc_cache = {}   # shape -> accelParams
        self._tris_cache = {}  # shape -> (triangles, tri_to_poly)
        self._targets = []
        for s in target_shapes:
            fn = self._make_mfn(s)
            if fn is None:
                continue
            self._fn_cache[s] = fn
            try:
                self._acc_cache[s] = fn.autoUniformGridParams()
            except Exception:
                self._acc_cache[s] = None
            self._targets.append(s)

    @staticmethod
    def _make_mfn(shape):
        """Build MFnMesh (api1) for a shape name."""
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

    def shapes(self):
        return list(self._targets)

    def _hit_face_world_verts(self, shape, face_id):
        """Return world-space vertex positions of polygon face `face_id`."""
        try:
            pts = []
            sel = om.MSelectionList()
            sel.add(shape)
            dag = om.MDagPath()
            sel.getDagPath(0, dag)
            try:
                dag.extendToShape()
            except Exception:
                pass
            it = om.MItMeshPolygon(dag)
            # advance to face_id
            util = om.MScriptUtil()
            util.createFromInt(0)
            prev_idx = util.asIntPtr()
            it.setIndex(face_id, prev_idx)
            ws_pts = om.MPointArray()
            it.getPoints(ws_pts, om.MSpace.kWorld)
            for i in range(ws_pts.length()):
                p = ws_pts[i]
                pts.append((p.x, p.y, p.z))
            return pts
        except Exception:
            return []

    def cast(self, source_point, direction, exclude_vert_positions=None,
             max_distance=None, self_shape=None):
        """
        Cast a ray and return a sorted list of valid hit distances.

        Args:
            source_point:  (x,y,z) world-space ray origin
            direction:     (dx,dy,dz) world-space direction (will be normalized)
            exclude_vert_positions:
                iterable of (x,y,z) world positions belonging to the moving
                element. Used together with `self_shape` to skip self-hits
                on the source mesh near the moving element. Hits on OTHER
                meshes are NEVER filtered by this list (so walls always count).
            max_distance:  cap (world units). None = unbounded.
            self_shape:    long shape name of the moving element's mesh.
                Vertex-share filtering is applied ONLY to hits on this mesh.

        Returns:
            list of float distances, ascending.
        """
        if not MAYA_AVAILABLE:
            return []

        # Validate inputs (NaN/inf guard)
        if not _is_finite_vec(source_point) or not _is_finite_vec(direction):
            return []
        L = _len(direction)
        if L < _RAY_EPS:
            return []
        nd = (direction[0] / L, direction[1] / L, direction[2] / L)

        ray_src = om.MFloatPoint(float(source_point[0]),
                                 float(source_point[1]),
                                 float(source_point[2]))
        ray_dir = om.MFloatVector(float(nd[0]),
                                  float(nd[1]),
                                  float(nd[2]))

        max_param = float(max_distance) if (max_distance is not None) else 1.0e9

        tol = _get_vert_share_tolerance()
        tol_sq = tol * tol if tol > 0.0 else 0.0
        ex_pts = list(exclude_vert_positions) if exclude_vert_positions else []

        all_distances = []

        for shape in self._targets:
            fn = self._fn_cache[shape]
            accel = self._acc_cache.get(shape)
            is_self = (self_shape is not None and shape == self_shape)

            hit_pts   = om.MFloatPointArray()
            hit_rps   = om.MFloatArray()
            hit_faces = om.MIntArray()
            hit_tris  = om.MIntArray()
            hit_b1    = om.MFloatArray()
            hit_b2    = om.MFloatArray()

            try:
                # api1 allIntersections fills the output arrays in-place.
                # The return value is unreliable across Maya versions
                # (sometimes None, sometimes MStatus, sometimes self) -
                # we MUST NOT branch on it. Instead we trust the output
                # arrays.
                fn.allIntersections(
                    ray_src, ray_dir,
                    None,            # faceIds filter
                    None,            # triIds filter
                    False,           # idsSorted
                    om.MSpace.kWorld,
                    max_param,
                    False,           # testBothDirections
                    accel,           # accelParams
                    True,            # sortHits
                    hit_pts, hit_rps, hit_faces, hit_tris, hit_b1, hit_b2,
                    _RAY_EPS,        # tolerance
                )
            except Exception:
                # On a real failure we just skip this shape
                continue

            n = hit_rps.length()
            if n == 0:
                continue

            # Vertex-share cache only built when needed (self mesh + ex_pts)
            face_verts_cache = {}

            for i in range(n):
                d = float(hit_rps[i])
                if not _is_finite(d):
                    continue
                if d < 0.0:
                    continue
                if d <= _RAY_EPS:
                    # epsilon hit — typically self-touch at the source
                    continue
                if max_distance is not None and d > max_distance:
                    continue

                # Vertex-share filter: ONLY for self-mesh hits.
                # Cross-mesh hits (walls, other geometry) MUST be kept,
                # even if their vertex positions happen to be close to
                # the moving element (e.g. when meshes are touching).
                if is_self and ex_pts and tol_sq > 0.0:
                    face_id = int(hit_faces[i])
                    fv = face_verts_cache.get(face_id)
                    if fv is None:
                        fv = self._hit_face_world_verts(shape, face_id)
                        face_verts_cache[face_id] = fv
                    if _any_vertex_within(fv, ex_pts, tol_sq):
                        continue

                all_distances.append(d)

        all_distances.sort()
        return all_distances


def _any_vertex_within(face_verts, exclude_pts, tol_sq):
    """True if any face vertex is within sqrt(tol_sq) of any exclude point."""
    for fv in face_verts:
        for ep in exclude_pts:
            dx = fv[0] - ep[0]
            dy = fv[1] - ep[1]
            dz = fv[2] - ep[2]
            if (dx * dx + dy * dy + dz * dz) <= tol_sq:
                return True
    return False


def _is_finite(v):
    try:
        return not (math.isnan(v) or math.isinf(v))
    except Exception:
        return False


def _is_finite_vec(v):
    return _is_finite(v[0]) and _is_finite(v[1]) and _is_finite(v[2])
# ---------------------------------------------------------------------------
# Move-to-Origin Core (axis-constrained)
# ---------------------------------------------------------------------------
# Per-element move logic. Each element (mesh / vertex / edge / face) is
# moved as a single unit toward the world origin ALONG ONE AXIS (X, Y, or
# Z). The sign is auto-determined by the element center: if center is on
# the +axis side, motion is along -axis; if on the -axis side, motion is
# along +axis. If center is exactly on the axis-plane (|coord| < EPSILON),
# the element is skipped.
#
# Two modes per item type:
#   - "rigid"      : selection moves as ONE element (one center, one delta,
#                    same delta applied to all member vertices)
#   - "individual" : each sub-element (each vertex, each edge, each face)
#                    moves independently
# ---------------------------------------------------------------------------

_MOVE_EPS = 1.0e-5
_DEFAULT_MOVE_OFFSET = [0.001]   # cm
_DEFAULT_MOVE_AXIS   = [0]       # 0=X, 1=Y, 2=Z


def _get_move_offset():
    return _DEFAULT_MOVE_OFFSET[0]


def _set_move_offset(v):
    try:
        v = float(v)
    except Exception:
        return
    if v < 0.0:
        v = 0.0
    _DEFAULT_MOVE_OFFSET[0] = v


def _get_move_axis():
    return _DEFAULT_MOVE_AXIS[0]


def _set_move_axis(idx):
    try:
        i = int(idx)
    except Exception:
        return
    if i in (0, 1, 2):
        _DEFAULT_MOVE_AXIS[0] = i


# Mode constants
MOVE_MODE_RIGID      = "rigid"
MOVE_MODE_INDIVIDUAL = "individual"


class MoveToOriginCore(object):
    """Stateful core. axis: 0/1/2 (X/Y/Z). Sign auto from element center."""

    def __init__(self, offset=None, axis=None, target_shapes=None):
        self.offset = float(_get_move_offset() if offset is None else offset)
        self.axis   = int(_get_move_axis() if axis is None else axis)
        if self.axis not in (0, 1, 2):
            self.axis = 0
        self.raycaster = OriginRaycaster(target_shapes=target_shapes)
        self.moved   = 0
        self.skipped = 0

    def _compute_delta(self, center, exclude_pts, self_shape=None):
        coord = center[self.axis]
        if abs(coord) < _MOVE_EPS:
            return (0.0, 0.0, 0.0), False
        sign = -1.0 if coord > 0.0 else 1.0
        direction = [0.0, 0.0, 0.0]
        direction[self.axis] = sign
        direction = tuple(direction)
        dist_to_plane = abs(coord)

        hits = self.raycaster.cast(
            center, direction,
            exclude_vert_positions=exclude_pts,
            max_distance=None,
            self_shape=self_shape)

        candidates = list(hits)
        candidates.append(dist_to_plane)
        move_dist = min(candidates)
        final_dist = move_dist - self.offset
        if final_dist < 0.0:
            final_dist = 0.0

        delta = (direction[0] * final_dist,
                 direction[1] * final_dist,
                 direction[2] * final_dist)
        return delta, True

    def _find_leading_point(self, pts):
        """Among `pts`, return the one closest to the origin along self.axis."""
        ax = self.axis
        best = None
        best_abs = None
        for p in pts:
            a = abs(p[ax])
            if best_abs is None or a < best_abs:
                best = p
                best_abs = a
        return best

    def _compute_rigid_delta(self, pts, self_shape=None):
        """Compute a single delta for rigid-body move of a set of points.

        Strategy: cast a ray from EVERY vertex toward the origin along the
        chosen axis. For each vertex, collect the shortest hit distance
        (including the dist-to-origin-plane as a virtual hit). Then take
        the MINIMUM across ALL vertices. This guarantees no vertex will
        penetrate any wall.

        The distance for each vertex is measured from *that* vertex's own
        axis-coordinate, so we convert each per-vertex safe-distance into
        a "move distance from the leading point" to keep them comparable.
        """
        if not pts:
            return (0.0, 0.0, 0.0), False

        ax = self.axis

        # Determine sign from the leading vertex (closest to 0)
        leader = self._find_leading_point(pts)
        if leader is None:
            return (0.0, 0.0, 0.0), False
        leader_coord = leader[ax]
        if abs(leader_coord) < _MOVE_EPS:
            return (0.0, 0.0, 0.0), False

        sign = -1.0 if leader_coord > 0.0 else 1.0
        direction = [0.0, 0.0, 0.0]
        direction[ax] = sign
        direction = tuple(direction)

        # For each vertex, compute its own safe travel distance.
        # safe_travel = (shortest hit dist from vertex) - offset
        # Then convert to how far the *whole group* can move:
        #   group_move_limit = safe_travel
        # because all vertices move the same delta along the axis.

        min_safe = None
        for p in pts:
            p_coord = p[ax]
            if abs(p_coord) < _MOVE_EPS:
                # This vertex is already on the plane -> group can't move
                return (0.0, 0.0, 0.0), False

            # Check this vertex faces the same direction as the group
            p_sign = -1.0 if p_coord > 0.0 else 1.0
            if p_sign != sign:
                # Mixed sides of the origin; skip this vertex
                continue

            dist_to_plane = abs(p_coord)

            hits = self.raycaster.cast(
                p, direction,
                exclude_vert_positions=pts,
                max_distance=None,
                self_shape=self_shape)

            candidates = list(hits)
            candidates.append(dist_to_plane)
            vertex_safe = min(candidates)

            if min_safe is None or vertex_safe < min_safe:
                min_safe = vertex_safe

        if min_safe is None:
            return (0.0, 0.0, 0.0), False

        final_dist = min_safe - self.offset
        if final_dist < 0.0:
            final_dist = 0.0

        delta = (direction[0] * final_dist,
                 direction[1] * final_dist,
                 direction[2] * final_dist)
        return delta, True

    # ---- Mesh ---------------------------------------------------------
    def move_mesh(self, mesh_shape):
        if not MAYA_AVAILABLE:
            return
        tr_node = MayaBridge.get_transform(mesh_shape)
        if not tr_node:
            self.skipped += 1
            return
        try:
            bb = cmds.exactWorldBoundingBox(mesh_shape)
        except Exception:
            self.skipped += 1
            return

        # Build 8 bounding-box corners + center as representative points
        corners = [
            (bb[0], bb[1], bb[2]), (bb[3], bb[1], bb[2]),
            (bb[0], bb[4], bb[2]), (bb[3], bb[4], bb[2]),
            (bb[0], bb[1], bb[5]), (bb[3], bb[1], bb[5]),
            (bb[0], bb[4], bb[5]), (bb[3], bb[4], bb[5]),
        ]
        delta, moved = self._compute_rigid_delta(corners, self_shape=mesh_shape)
        if not moved:
            self.skipped += 1
            return
        try:
            cmds.xform(tr_node, ws=True, r=True,
                       t=(delta[0], delta[1], delta[2]))
            self.moved += 1
        except Exception:
            self.skipped += 1

    # ---- Vertices -----------------------------------------------------
    def move_vertices_rigid(self, mesh_shape, vert_indices):
        if not vert_indices:
            return
        pts = self._get_vert_positions(mesh_shape, vert_indices)
        if not pts:
            self.skipped += 1
            return
        delta, moved = self._compute_rigid_delta(pts, self_shape=mesh_shape)
        if not moved:
            self.skipped += 1
            return
        self._translate_vertices(mesh_shape, vert_indices, delta)
        self.moved += 1

    def move_vertices_individual(self, mesh_shape, vert_indices):
        self._move_individual_with_collision_check(
            mesh_shape, vert_indices, vert_indices)

    # ---- Edges --------------------------------------------------------
    def move_edges_rigid(self, mesh_shape, edge_indices):
        if not edge_indices:
            return
        vidx = self._verts_from_edges(mesh_shape, edge_indices)
        if not vidx:
            self.skipped += 1
            return
        pts = self._get_vert_positions(mesh_shape, vidx)
        if not pts:
            self.skipped += 1
            return
        delta, moved = self._compute_rigid_delta(pts, self_shape=mesh_shape)
        if not moved:
            self.skipped += 1
            return
        self._translate_vertices(mesh_shape, vidx, delta)
        self.moved += 1

    def move_edges_individual(self, mesh_shape, edge_indices):
        all_vidx = self._verts_from_edges(mesh_shape, edge_indices)
        if not all_vidx:
            self.skipped += 1
            return
        self._move_individual_with_collision_check(
            mesh_shape, all_vidx, all_vidx)

    # ---- Faces --------------------------------------------------------
    def move_faces_rigid(self, mesh_shape, face_indices):
        if not face_indices:
            return
        vidx = self._verts_from_faces(mesh_shape, face_indices)
        if not vidx:
            self.skipped += 1
            return
        pts = self._get_vert_positions(mesh_shape, vidx)
        if not pts:
            self.skipped += 1
            return
        delta, moved = self._compute_rigid_delta(pts, self_shape=mesh_shape)
        if not moved:
            self.skipped += 1
            return
        self._translate_vertices(mesh_shape, vidx, delta)
        self.moved += 1

    def move_faces_individual(self, mesh_shape, face_indices):
        all_vidx = self._verts_from_faces(mesh_shape, face_indices)
        if not all_vidx:
            self.skipped += 1
            return
        self._move_individual_with_collision_check(
            mesh_shape, all_vidx, all_vidx)

    # =================================================================
    # Individual move with post-move collision check (binary search)
    # =================================================================
    def _move_individual_with_collision_check(self, mesh_shape, vert_indices,
                                              all_involved_verts):
        """
        Move each vertex individually toward origin, then verify that the
        resulting mesh does not intersect other meshes. If it does, scale
        back ALL vertex deltas by a binary-searched factor until no
        intersection remains.

        Steps:
          1. Compute per-vertex delta via raycast (individual distances).
          2. Apply full deltas.
          3. Run CollisionDetector (self mesh vs all other meshes).
          4. If intersection found, undo the move, try with factor *= 0.5,
             repeat (binary search up to 8 iterations).
          5. Settle on the largest factor that causes no intersection.
        """
        if not vert_indices:
            return

        # unique vertex indices
        vidx_unique = list(set(vert_indices))

        # 1. Compute per-vertex deltas
        pts_orig = {}  # {vi: (x,y,z)}
        deltas   = {}  # {vi: (dx,dy,dz)}
        any_moved = False
        for vi in vidx_unique:
            p = self._get_vert_positions(mesh_shape, [vi])
            if not p:
                continue
            pts_orig[vi] = p[0]
            d, ok = self._compute_delta(p[0], p, self_shape=mesh_shape)
            if ok and (abs(d[0]) > _MOVE_EPS or abs(d[1]) > _MOVE_EPS
                       or abs(d[2]) > _MOVE_EPS):
                deltas[vi] = d
                any_moved = True
            else:
                deltas[vi] = (0.0, 0.0, 0.0)

        if not any_moved:
            self.skipped += len(vidx_unique)
            return

        # Get other mesh shapes for collision check
        other_shapes = []
        for s in MayaBridge.get_mesh_shapes():
            if s != mesh_shape:
                other_shapes.append(s)

        # 2. Binary search for safe factor
        _MAX_ITER = 8
        lo = 0.0
        hi = 1.0
        best_factor = 0.0  # 0.0 = no move (safe fallback)

        for iteration in range(_MAX_ITER):
            mid = (lo + hi) * 0.5

            # Apply deltas at factor = mid
            new_positions = {}
            for vi in vidx_unique:
                ox, oy, oz = pts_orig[vi]
                dx, dy, dz = deltas[vi]
                new_positions[vi] = (ox + dx * mid,
                                     oy + dy * mid,
                                     oz + dz * mid)
            self._set_vertex_positions(mesh_shape, new_positions)

            # 3. Check for intersection with other meshes
            has_collision = self._check_collision_with_others(
                mesh_shape, other_shapes)

            if has_collision:
                # Too far; reduce
                hi = mid
            else:
                # Safe; try going further
                best_factor = mid
                lo = mid

        # 4. Apply the best safe factor
        final_positions = {}
        for vi in vidx_unique:
            ox, oy, oz = pts_orig[vi]
            dx, dy, dz = deltas[vi]
            final_positions[vi] = (ox + dx * best_factor,
                                   oy + dy * best_factor,
                                   oz + dz * best_factor)
        self._set_vertex_positions(mesh_shape, final_positions)

        moved_count = sum(1 for vi in vidx_unique
                          if abs(deltas[vi][0]) > _MOVE_EPS
                          or abs(deltas[vi][1]) > _MOVE_EPS
                          or abs(deltas[vi][2]) > _MOVE_EPS)
        self.moved += moved_count if best_factor > _MOVE_EPS else 0
        if best_factor <= _MOVE_EPS:
            self.skipped += len(vidx_unique)

    def _check_collision_with_others(self, mesh_shape, other_shapes):
        """Quick intersection check: mesh_shape vs each other_shape.
        Returns True if ANY intersection is found.
        Uses CollisionDetector (existing BVH-based checker).
        """
        try:
            tris_a, map_a, vids_a = MayaBridge.get_triangles(mesh_shape)
        except Exception:
            return False
        if not tris_a:
            return False

        for other in other_shapes:
            try:
                tris_b, map_b, vids_b = MayaBridge.get_triangles(other)
            except Exception:
                continue
            if not tris_b:
                continue
            # Quick AABB pre-check
            aabb_a = _compute_tris_aabb(tris_a)
            aabb_b = _compute_tris_aabb(tris_b)
            if not _aabbs_overlap(aabb_a, aabb_b):
                continue
            det = CollisionDetector(tris_a, tris_b)
            hits = det.check(threshold=0.0, backface_cull=True)
            if hits:
                return True
        return False

    @staticmethod
    def _set_vertex_positions(mesh_shape, vi_to_pos):
        """Set absolute world-space positions for multiple vertices."""
        for vi, pos in vi_to_pos.items():
            try:
                cmds.xform("{0}.vtx[{1}]".format(mesh_shape, vi),
                           ws=True, t=(pos[0], pos[1], pos[2]))
            except Exception:
                pass

    # ---- helpers ------------------------------------------------------
    @staticmethod
    def _verts_from_edges(mesh_shape, edge_indices):
        comps = ["{0}.e[{1}]".format(mesh_shape, ei) for ei in edge_indices]
        try:
            verts = cmds.polyListComponentConversion(
                comps, fromEdge=True, toVertex=True) or []
            verts = cmds.ls(verts, fl=True) or []
        except Exception:
            return []
        out = []
        for v in verts:
            try:
                out.append(int(v.split("[")[-1].rstrip("]")))
            except Exception:
                pass
        return out

    @staticmethod
    def _verts_from_faces(mesh_shape, face_indices):
        comps = ["{0}.f[{1}]".format(mesh_shape, fi) for fi in face_indices]
        try:
            verts = cmds.polyListComponentConversion(
                comps, fromFace=True, toVertex=True) or []
            verts = cmds.ls(verts, fl=True) or []
        except Exception:
            return []
        out = []
        for v in verts:
            try:
                out.append(int(v.split("[")[-1].rstrip("]")))
            except Exception:
                pass
        return out

    @staticmethod
    def _get_vert_positions(mesh_shape, vert_indices):
        out = []
        for vi in vert_indices:
            try:
                p = cmds.xform("{0}.vtx[{1}]".format(mesh_shape, vi),
                               q=True, ws=True, t=True)
                out.append((p[0], p[1], p[2]))
            except Exception:
                pass
        return out

    @staticmethod
    def _translate_vertices(mesh_shape, vert_indices, delta):
        if not vert_indices:
            return
        comps = ["{0}.vtx[{1}]".format(mesh_shape, vi) for vi in vert_indices]
        try:
            cmds.xform(comps, ws=True, r=True,
                       t=(delta[0], delta[1], delta[2]))
        except Exception:
            for c in comps:
                try:
                    cmds.xform(c, ws=True, r=True,
                               t=(delta[0], delta[1], delta[2]))
                except Exception:
                    pass


def _avg_point(pts):
    sx = sy = sz = 0.0
    for p in pts:
        sx += p[0]; sy += p[1]; sz += p[2]
    n = float(len(pts))
    return (sx / n, sy / n, sz / n)
# ---------------------------------------------------------------------------
# MoveItem base + Selection parsing
# ---------------------------------------------------------------------------


def _parse_selection_for_move():
    """Inspect current Maya selection and return:
       {"vertices": {shape: [idx, ...]},
        "edges":    {shape: [idx, ...]},
        "faces":    {shape: [idx, ...]},
        "objects":  [shape, ...]}
    """
    out = {"vertices": {}, "edges": {}, "faces": {}, "objects": []}
    if not MAYA_AVAILABLE:
        return out
    try:
        sel = cmds.ls(sl=True, fl=True, long=True) or []
    except Exception:
        sel = []
    if not sel:
        return out

    seen_objs = set()
    for it in sel:
        if ".vtx[" in it:
            shape, _, rest = it.partition(".vtx[")
            try:
                idx = int(rest.rstrip("]"))
            except Exception:
                continue
            out["vertices"].setdefault(shape, []).append(idx)
        elif ".e[" in it:
            shape, _, rest = it.partition(".e[")
            try:
                idx = int(rest.rstrip("]"))
            except Exception:
                continue
            out["edges"].setdefault(shape, []).append(idx)
        elif ".f[" in it:
            shape, _, rest = it.partition(".f[")
            try:
                idx = int(rest.rstrip("]"))
            except Exception:
                continue
            out["faces"].setdefault(shape, []).append(idx)
        else:
            try:
                t = cmds.nodeType(it)
            except Exception:
                continue
            if t == "transform":
                shapes = cmds.listRelatives(
                    it, allDescendents=True, type="mesh",
                    fullPath=True, ni=True) or []
                for s in shapes:
                    if s in seen_objs:
                        continue
                    try:
                        if cmds.getAttr(s + ".intermediateObject"):
                            continue
                    except Exception:
                        pass
                    seen_objs.add(s)
                    out["objects"].append(s)
            elif t == "mesh":
                if it in seen_objs:
                    continue
                try:
                    if cmds.getAttr(it + ".intermediateObject"):
                        continue
                except Exception:
                    pass
                seen_objs.add(it)
                out["objects"].append(it)
    return out


# ---------------------------------------------------------------------------
class MoveItem(CheckItem):
    """
    Base for move-to-origin actions. Subclasses implement `_perform`.

    Class attributes:
        accepts_kind   : "objects" / "vertices" / "edges" / "faces"
        supports_modes : True if user can toggle rigid/individual
        is_action      : True (used by CheckItemWidget to switch button label)
    """
    can_auto_fix    = False
    default_enabled = True
    accepts_kind    = None
    supports_modes  = False
    is_action       = True
    _default_mode   = MOVE_MODE_RIGID

    def __init__(self):
        super(MoveItem, self).__init__()
        self.mode = self._default_mode  # "rigid" or "individual"
        self._last_summary = u""

    def set_mode(self, mode):
        if mode in (MOVE_MODE_RIGID, MOVE_MODE_INDIVIDUAL):
            self.mode = mode

    def check(self):
        """Performs the move; returns issues list as a status carrier."""
        parsed = _parse_selection_for_move()
        bucket = parsed.get(self.accepts_kind) if self.accepts_kind else None
        is_empty = (not bucket)
        if is_empty:
            return [{
                "mesh_a": "", "mesh_b": "",
                "face_a": -1, "face_b": -1,
                "depth": 0.0, "point": None,
                "detail": tr("move_status_no_selection"),
            }]

        cmds.undoInfo(openChunk=True, chunkName="DW_MoveToOrigin")
        try:
            core = MoveToOriginCore()  # uses module defaults (offset, axis)
            self._perform(parsed, core)
        finally:
            try:
                cmds.undoInfo(closeChunk=True)
            except Exception:
                pass

        moved = core.moved
        skipped = core.skipped
        if moved == 0 and skipped == 0:
            return [{
                "mesh_a": "", "mesh_b": "",
                "face_a": -1, "face_b": -1,
                "depth": 0.0, "point": None,
                "detail": tr("move_status_no_selection"),
            }]
        summary = tr("move_status_done", n=moved)
        if skipped > 0:
            summary += u"  /  " + tr("move_status_skipped", n=skipped)
        if skipped > 0:
            return [{
                "mesh_a": "", "mesh_b": "",
                "face_a": -1, "face_b": -1,
                "depth": 0.0, "point": None,
                "detail": summary,
            }]
        self._last_summary = summary
        return []

    def _perform(self, parsed, core):
        raise NotImplementedError
# ---------------------------------------------------------------------------
# Concrete MoveItem subclasses (Mesh / Vertex / Edge / Face)
# Each item has a `mode` ("rigid" or "individual") that the UI can toggle.
# Mesh has only "rigid" semantics (each transform is one element).
# ---------------------------------------------------------------------------


class MoveMeshToOrigin(MoveItem):
    label_key      = "move_mesh"
    desc_key       = "move_mesh_desc"
    accepts_kind   = "objects"
    supports_modes = False  # Mesh = always per-transform

    def _perform(self, parsed, core):
        for shape in parsed["objects"]:
            core.move_mesh(shape)


class MoveVertexToOrigin(MoveItem):
    label_key      = "move_vertex"
    desc_key       = "move_vertex_desc"
    accepts_kind   = "vertices"
    supports_modes = True

    def _perform(self, parsed, core):
        for shape, idxs in parsed["vertices"].items():
            if self.mode == MOVE_MODE_INDIVIDUAL:
                core.move_vertices_individual(shape, idxs)
            else:
                core.move_vertices_rigid(shape, idxs)


class MoveEdgeToOrigin(MoveItem):
    label_key      = "move_edge"
    desc_key       = "move_edge_desc"
    accepts_kind   = "edges"
    supports_modes = True

    def _perform(self, parsed, core):
        for shape, idxs in parsed["edges"].items():
            if self.mode == MOVE_MODE_INDIVIDUAL:
                core.move_edges_individual(shape, idxs)
            else:
                core.move_edges_rigid(shape, idxs)


class MoveFaceToOrigin(MoveItem):
    label_key      = "move_face"
    desc_key       = "move_face_desc"
    accepts_kind   = "faces"
    supports_modes = True

    def _perform(self, parsed, core):
        for shape, idxs in parsed["faces"].items():
            if self.mode == MOVE_MODE_INDIVIDUAL:
                core.move_faces_individual(shape, idxs)
            else:
                core.move_faces_rigid(shape, idxs)


# Registry consumed by the main window
MOVE_ITEMS = [
    MoveMeshToOrigin,
    MoveVertexToOrigin,
    MoveEdgeToOrigin,
    MoveFaceToOrigin,
]
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

