# -*- mode: python ; coding: utf-8 -*-
# SPDX-FileCopyrightText: Lada Authors
# SPDX-License-Identifier: AGPL-3.0

import argparse
import shutil
import os
import sys
import pathlib
from os.path import join as ospj

def get_project_root() -> str:
    project_root = pathlib.Path(".").absolute()
    assert (project_root / "pyproject.toml").exists(), "This script must be run from the root of the project"
    return str(project_root)

def get_intel_xpu_runtime_libs(project_root):
    venv_root = pathlib.Path(project_root) / "venv_release_win_arc"
    found_binaries = []
    
    patterns = [
        "sycl*.dll", "ur_win*.dll", "UR_LOADER.dll", "libmmd.dll", 
        "pti_*.dll", "pi_*.dll", "mkl_*.dll", "svml_*.dll", "impi.dll",
        "libintel*.dll", "tbb*.dll", "ze_loader.dll", "ze_intel_gpu64.dll",
        "ur_adapter_level_zero.dll"
    ]
    
    if venv_root.exists():
        for p_file in venv_root.rglob("*.dll"):
            if any(p_file.name.lower().startswith(pat.replace('*', '').lower()) for pat in patterns):
                found_binaries.append((str(p_file), "torch/lib"))
                found_binaries.append((str(p_file), "."))
    
    sys32 = pathlib.Path("C:/Windows/System32")
    for dll in ["ze_loader.dll", "ze_intel_gpu64.dll"]:
        if (sys32 / dll).exists():
            found_binaries.append((str(sys32 / dll), "."))
            
    return found_binaries

def _update_env_var(env_var, paths, separator=";"):
    assert sys.platform == "win32", "_update_env_var() only works on Windows"
    paths_to_add = [str(path).lower() for path in paths]
    if env_var in os.environ:
        existing_paths = os.environ[env_var].lower().split(separator)
        paths_to_add = [path for path in paths_to_add if path not in existing_paths]
        os.environ[env_var] = separator.join(paths_to_add + existing_paths)
    else:
        os.environ[env_var] = separator.join(paths_to_add)

def set_environment_variables(project_root_dir: str):
    release_dir = (pathlib.Path(project_root_dir) / "build_gtk_release" / "gtk" / "x64" / "release").absolute()
    bin_dir = release_dir / "bin"
    lib_dir = release_dir / "lib"
    includes = [
        release_dir / "include",
        release_dir / "include" / "cairo",
        release_dir / "include" / "glib-2.0",
        release_dir / "include" / "gobject-introspection-1.0",
        release_dir / "lib" / "glib-2.0" / "include",
    ]
    _update_env_var("PATH", [bin_dir])
    _update_env_var("LIB", [lib_dir])
    _update_env_var("INCLUDE", includes)

def get_common_binaries(project_root):
    bin_ffmpeg = shutil.which("ffmpeg.exe")
    bin_ffprobe = shutil.which("ffprobe.exe")
    common_binaries = [
        (bin_ffmpeg, "bin"),
        (bin_ffprobe, "bin"),
    ]
    common_binaries += get_intel_xpu_runtime_libs(project_root)
    return common_binaries

def get_gui_components(project_root_dir, common_datas, common_binaries, common_runtime_hooks, common_icon):
    gtk_release_dir = pathlib.Path(project_root_dir) / "build_gtk_release" / "gtk" / "x64" / "release"
    gtk_bin_dir = gtk_release_dir / "bin"
    
    gui_binaries = common_binaries + [
        (str(p), ".") for p in gtk_bin_dir.glob("*.dll")
    ] + [
        (str(gtk_bin_dir / "gdbus.exe"), "."),
        (str(gtk_release_dir / "lib" / "girepository-1.0" / "GioWin32-2.0.typelib"), "gi_typelibs"),
    ]

    conflict_excludes = [
        'mkl_blacs_msmpi_ilp64.2', 'mkl_blacs_msmpi_lp64.2', 
        'mkl_blacs_intelmpi_ilp64.2', 'mkl_blacs_intelmpi_lp64.2'
    ]

    gui_a = Analysis(
        [ospj(project_root_dir, 'lada/gui/main.py')],
        binaries=gui_binaries,
        datas=common_datas + [
            (str(p), str(p.relative_to(project_root_dir).parent)) for p in (pathlib.Path(project_root_dir) / "lada" / "gui").rglob("*.ui")
        ] + [
            (ospj(project_root_dir, 'lada/gui/style.css'), 'lada/gui'),
            (ospj(project_root_dir, 'lada/gui/resources.gresource'), 'lada/gui'),
        ],
        excludes=conflict_excludes,
        hooksconfig={
            "gi": {
                "icons": ["Adwaita"],
                "themes": ["Adwaita"],
                "module-versions": {"Gtk": "4.0"},
            },
        },
        runtime_hooks=common_runtime_hooks,
    )
    gui_pyz = PYZ(gui_a.pure)
    gui_exe = EXE(gui_pyz, gui_a.scripts, [], exclude_binaries=True, name='lada', console=False, icon=common_icon)
    return gui_a, gui_pyz, gui_exe

def get_cli_components(project_root_dir, common_datas, common_binaries, common_runtime_hooks, common_icon):
    cli_a = Analysis(
        [ospj(project_root_dir, 'lada/cli/main.py')],
        binaries=common_binaries,
        datas=common_datas,
        excludes=['mkl_blacs_msmpi_ilp64.2', 'mkl_blacs_msmpi_lp64.2'],
        runtime_hooks=common_runtime_hooks,
    )
    cli_pyz = PYZ(cli_a.pure)
    cli_exe = EXE(cli_pyz, cli_a.scripts, [], exclude_binaries=True, name='lada-cli', console=True, icon=common_icon)
    return cli_a, cli_pyz, cli_exe

def get_common_datas(project_root):
    common_datas = [
        (ospj(project_root, 'model_weights/lada_mosaic_detection_model_v2.pt'), 'model_weights'),
        (ospj(project_root, 'model_weights/lada_mosaic_detection_model_v4_accurate.pt'), 'model_weights'),
        (ospj(project_root, 'model_weights/lada_mosaic_detection_model_v4_fast.pt'), 'model_weights'),
        (ospj(project_root, 'model_weights/lada_mosaic_restoration_model_generic_v1.2.pth'), 'model_weights'),
        (ospj(project_root, 'model_weights/3rd_party/clean_youknow_video.pth'), 'model_weights/3rd_party'),
        (ospj(project_root, 'lada/utils/encoding_presets.csv'), 'lada/utils'),
    ]
    common_datas += [(str(p), str(p.relative_to(project_root).parent)) for p in pathlib.Path(ospj(project_root, "lada/locale")).rglob("*.mo")]
    return common_datas

def parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli-only", action="store_true")
    return parser.parse_args()

# ---------------------
# MAIN
# ---------------------
args = parser_args()
project_root = get_project_root()
if not args.cli_only:
    set_environment_variables(project_root)

common_datas = get_common_datas(project_root)
common_binaries = get_common_binaries(project_root)
common_runtime_hooks = [ospj(project_root, "packaging/windows/pyinstaller_runtime_hook_lada_arc.py")]
common_icon = [ospj(project_root, 'assets/io.github.ladaapp.lada.png')]

cli_a, cli_pyz, cli_exe = get_cli_components(project_root, common_datas, common_binaries, common_runtime_hooks, common_icon)

if args.cli_only:
    coll = COLLECT(cli_exe, cli_a.binaries, cli_a.datas, name='lada')
else:
    gui_a, gui_pyz, gui_exe = get_gui_components(project_root, common_datas, common_binaries, common_runtime_hooks, common_icon)
    coll = COLLECT(gui_exe, gui_a.binaries, gui_a.datas, cli_exe, cli_a.binaries, cli_a.datas, name='lada')