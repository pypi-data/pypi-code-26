spec = {
    # PROJECT SETTINGS
    'targetname': 'android',
    'build_dir': './.buildozer',
    'bin_dir': './bin',

    # APPLICATION
    'title': 'My Application',
    'package_name': 'myapp',
    'version': '0.1',
    'version_regex': '__version__ = [\'"](.*)[\'"]',
    'version_filename': '%(source.dir)s/main.py',
    'package_domain': 'org.test',

    # SOURCE
    'source_dir': '.',
    'source_exclude_dirs': 'tests, bin',
    'source_include_exts': 'py,png,jpg,kv,atlas',
    'source_exclude_exts': 'spec',
    'source_include_patterns': 'assets/*,images/*.png',
    'source_exclude_patterns': 'license,images/*/*.jpg',

    'requirements': 'kivy',
    'requirements_source_kivy': '../../kivy',
    'garden_requirements': '',
    'presplash_filename': '%(source_dir)s/data/presplash.png',
    'icon_filename': '%(source_dir)s/data/icon.png',
    'orientation': 'portrait',   # landscape, portrait or all
    'services': 'NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY',    # (list) List of service to declare

    # ANDROID SPECIFIC
    'android_arch': 'armeabi-v7a',
    'android_api': 19,
    'android_minapi': 9,
    'android_sdk': 20,
    'android_sdk_path': '',
    'android_skip_update': False,
    'android_ndk': '9c',
    'android_ndk_path': '',
    'android_ant_path': '',

    'fullscreen': 'False',
    'android_permissions': 'INTERNET',
    'android_presplash_color': '#FFFFFF',
    'android_private_storage': True,
    'android_wakelock': False,

    # ANDROID SPECIFIC (Advanced)
    'android_entrypoint': 'org.renpy.android_PythonActivity',
    'android_add_jars': 'foo.jar,bar.jar,path/to/more/*.jar',
    'android_add_java_src': '',
    'android_add_aars': '',
    'android_gradle_dependencies': '',
    'android_add_activites': 'com.example.ExampleActivity',

    # MANIFEST
    'android_manifest_intent_filters': '',
    'android_manifest_launch_mode': 'standard',
    'android_meta_data': '',
    'android_library_references': '',
    'android_logcat_filters': '*:S python:D',
    'android_copy_libs': '1',

    'android_whitelist': '',
    'android_blacklist': '',

    # ADDITIONAL LIBRARIES
    'android_add_libs_armeabi': 'libs/android/*.so',
    'android_add_libs_armeabi_v7a': 'libs/android-v7/*.so',
    'android_add_libs_x86': 'libs/android-x86/*.so',
    'android_add_libs_mips': 'libs/android-mips/*.so',

    # OUYA
    'android_ouya_category': 'GAME',
    'android_ouya_icon_filename': '%(source_dir)s/data/ouya_icon.png',

    # Python for android (p4a) specific
    'p4a_branch': 'stable',
    'p4a_source_dir': '',
    'p4a_local_recipes': '',
    'p4a_hook': '',
    'p4a_bootstrap': 'sdl2',
    'p4a_port': '',

    # iOS specific
    'ios_kivy_ios_dir': '../kivy-ios',
    'ios_codesign_debug': 'iPhone Developer: <lastname> <firstname> (<hexstring>)',
    'ios_codesign_release': '%(ios_codesign.debug)s',

    # OSX Specific
    'author': '© Copyright Info',
    'osx_python_version': 3,
    'osx_kivy_version': '1.9.1',
}
