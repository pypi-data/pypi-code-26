#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
Copyright (c) 2018 Simon Wu <swprojects@runbox.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
translate = {

    'buildertron': {
        'targetname': 'targetname',
    },

    'app': {
        'title': 'title',
        'package.name': 'package_name',
        'package.domain': 'package_domain',
        'source.dir': 'source_dir',
        'source.include_exts': 'source_include_exts',
        'source.include_patterns': 'source_include_patterns',
        'source.exclude_dirs': 'source_exclude_dirs',
        'source.exclude_exts': 'source_exclude_exts',
        'source.exclude_patterns': 'source_exclude_patterns',
        'version': 'version',
        'version.regex': 'version_regex',
        'version.filename': 'version_filename',
        'requirements': 'requirements',
        'requirements.source.kivy': 'requirements_source_kivy',
        'garden_requirements': 'garden_requirements',
        'presplash.filename': 'presplash_filename',
        'icon.filename': 'icon_filename',
        'orientation': 'orientation',
        'services': 'services',

        # OSX Specific
        'author': 'author',
        'osx.python_version': 'osx_python_version',
        'osx.kivy_version': 'osx_kivy_version',

        # ANDROID SPECIFIC
        'android.presplash_color': 'android_presplash_color',
        'android.permissions': 'android_permissions',
        'android.api': 'android_api',
        'android.minapi': 'android_minapi',
        'android.sdk': 'android_sdk',
        'android.ndk': 'android_ndk',
        'android.private_storage': 'android_private_storage',
        'android.ndk_path': 'android_ndk_path',
        'android.sdk_path': 'android_sdk_path',
        'android.ant_path': 'android_ant_path',
        'android.skip_update': 'android_skip_update',
        'android.entrypoint': 'android_entrypoint',
        'android.whitelist': 'android_whitelist',
        'android.blacklist': 'android_blacklist',
        'android.whitelist_src': 'android_whitelist',
        'android.blacklist_src': 'android_blacklist',
        'android.add_jars': 'android_add_jars',
        'android.add_src': 'android_add_src',
        'android.add_aars': 'android_add_aars',
        'android.gradle_dependencies': 'android_gradle_dependencies',

        'p4a_branch': 'p4a_branch',
        'fullscreen': 'fullscreen',

        # OUYA
        'android.ouya_category': 'android_ouya_category',
        'android.ouya_icon_filename': 'android_ouya_icon_filename',

        'android.manifest_intent_filters': 'android_manifest_intent_filters',

        'android.add_libs_armeabi': 'android_add_libs_armeabi',
        'android.add_libs_armeabi_v7a': 'android_add_libs_armeabi_v7a',
        'android.add_libs_x86': 'android_add_libs_x86',
        'android.add_libs_mips': 'android_add_libs_mips',

        'android.manifest_launch_mode': 'android_manifest_launch_mode',
        'android.wakelock': 'android_wakelock',
        'android.meta_data': 'android_meta_data',
        'android.library_references': 'android_library_references',
        'android.logcat_filters': 'android_logcat_filters',
        'android.copy_libs': 'android_copy_libs',
        'android.add_activites': 'android_add_activites',
        'android.arch': 'android_arch',

        'p4a.source_dir': 'p4a_source_dir',
        'p4a.local_recipes': 'p4a_local_recipes',
        'p4a.hook': 'p4a_hook',
        'p4a.bootstrap': 'p4a_bootstrap',

        # iOS specific
        'ios.kivy_ios_dir': 'ios_kivy_ios_dir',
        'ios.codesign_debug': 'ios_codesign_debug',
        'ios.codesign_release': 'ios_codesign_release',
    },

    'buildozer': {
        'log_level': 'log_level',
        'warn_on_root': 'warn_on_root',
        'build_dir': 'build_dir',
        'bin_dir': 'bin_dir',
    },
}
