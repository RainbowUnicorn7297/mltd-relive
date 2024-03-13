import os
import shutil
import struct
import subprocess
import sys
import traceback
from tkinter.filedialog import askopenfilename
from xml.etree import ElementTree as ET

import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer

apktool_path = ''
zipalign_path = ''
apksigner_path = ''

apk_path = ''
apk_name = ''
ascii_apk_name = ''
original_apk_path = ''

resolution = 720
frame_rate = 60


def fonts_path():
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('..'))
    return os.path.join(base_path, 'fonts')


def current_path():
    return getattr(sys, '_MEIPASS', os.path.abspath('.'))


def validate_input():
    if not apktool_path.endswith('apktool.bat'):
        return 'Invalid apktool.bat Path'
    if not zipalign_path.endswith('zipalign.exe'):
        return 'Invalid zipalign.exe Path'
    if not apksigner_path.endswith('apksigner.bat'):
        return 'Invalid apksigner.bat Path'
    if not apk_path.endswith('.apk'):
        return 'Invalid Game APK Path'
    return ''


def initialize():
    global apk_path, apk_name, ascii_apk_name, original_apk_path

    apk_name = os.path.basename(apk_path).removesuffix('.apk')
    ascii_apk_name = apk_name.replace('劇場時光', '~~MLTD_CH~~')
    ascii_apk_name = ascii_apk_name.replace('밀리언 라이브!', '~~MLTD_KR~~')
    if apk_name != ascii_apk_name:
        shutil.copyfile(os.path.join(apk_path), os.path.abspath(f'{ascii_apk_name}.apk'))
        original_apk_path = apk_path
        apk_path = os.path.abspath(f'{ascii_apk_name}.apk')


def apktool_decode():
    subprocess.run([apktool_path, 'd', apk_path], stdin=subprocess.DEVNULL)


def apply_patch():
    lang = ''
    tree = ET.parse(os.path.join(ascii_apk_name, 'AndroidManifest.xml'))
    package = tree.getroot().get('package')
    if package.startswith('com.bandainamcoent.imas_millionlive_theaterdays_ch.'):
        lang = 'ch'
    elif package.startswith('com.bandainamcoent.imas_millionlive_theaterdays_kr.'):
        lang = 'kr'
    else:
        raise RuntimeError('Unrecognized game APK')

    with open(os.path.join(ascii_apk_name, 'lib', 'arm64-v8a', 'libil2cpp.so'), 'rb') as f:
        il2cpp = bytearray(f.read())

    resolution_addr = 0x01950494 if lang == 'ch' else 0x01947404
    resolution_inst = 0x52800009 | (resolution << 5)
    il2cpp[resolution_addr:resolution_addr+4] = struct.pack('<i', resolution_inst)

    frame_rate_addrs = [
        0x01e35c94,     # OnBeginScene
        0x01e3676c,     # SetupLiveMVSpecialLevel
        0x01e3617c,     # SetupLiveSpecialLevel
        0x01e359ac,     # SetupTheaterSpecialLevel
        0x01e35de4,     # SetupCommuSpecialPlusLevel
        0x01e35f8c      # SetupGashaSpecialPlusLevel
    ]
    if lang == 'kr':
        frame_rate_addrs = [
            0x01e2bbfc,     # OnBeginScene
            0x01e2c6d4,     # SetupLiveMVSpecialLevel
            0x01e2c0e4,     # SetupLiveSpecialLevel
            0x01e2b914,     # SetupTheaterSpecialLevel
            0x01e2bd4c,     # SetupCommuSpecialPlusLevel
            0x01e2bef4      # SetupGashaSpecialPlusLevel
        ]
    frame_rate_inst = 0x52800000 | (frame_rate << 5)
    for frame_rate_addr in frame_rate_addrs:
        il2cpp[frame_rate_addr:frame_rate_addr+4] = struct.pack('<i', frame_rate_inst)

    with open(os.path.join(ascii_apk_name, 'lib', 'arm64-v8a', 'libil2cpp.so'), 'wb') as f:
        f.write(il2cpp)

    shutil.copyfile(
        os.path.join(current_path(), 'OverrideActivity_device_max_refresh_rate.smali'),
        os.path.join(ascii_apk_name, 'smali', 'com', 'bandainamcoent', 'imas_millionlive_theaterdays', 'player', 'OverrideActivity.smali')
    )


def apktool_build():
    subprocess.run([apktool_path, 'b', ascii_apk_name], stdin=subprocess.DEVNULL)


def zipalign():
    subprocess.run([
        zipalign_path, '-f', '-v', '4',
        os.path.join(ascii_apk_name, 'dist', f'{ascii_apk_name}.apk'),
        os.path.join(ascii_apk_name, 'dist', f'{ascii_apk_name}_{resolution}p_{frame_rate}fps.apk')
    ])


def apksigner():
    subprocess.run([
        apksigner_path, 'sign',
        '--ks', os.path.join(current_path(), 'mltd.jks'),
        '--ks-key-alias', 'bndltool',
        '--ks-pass', 'pass:changeit',
        os.path.join(ascii_apk_name, 'dist', f'{ascii_apk_name}_{resolution}p_{frame_rate}fps.apk')
    ])


def collect_and_cleanup():
    global apk_path

    if os.path.isfile(os.path.join(ascii_apk_name, 'dist', f'{ascii_apk_name}_{resolution}p_{frame_rate}fps.apk')):
        os.replace(
            os.path.join(ascii_apk_name, 'dist', f'{ascii_apk_name}_{resolution}p_{frame_rate}fps.apk'),
            f'{apk_name}_{resolution}p_{frame_rate}fps.apk'
        )
    if os.path.isdir(os.path.abspath(ascii_apk_name)):
        shutil.rmtree(os.path.abspath(ascii_apk_name))
    if apk_name != ascii_apk_name:
        if os.path.isfile(os.path.abspath(f'{ascii_apk_name}.apk')):
            os.remove(os.path.abspath(f'{ascii_apk_name}.apk'))
        apk_path = original_apk_path


def main():
    global apktool_path, zipalign_path, apksigner_path
    global apk_path
    global resolution, frame_rate

    resolutions = [720, 1080, 1440, 2160]
    selected_resolution = 0
    custom_resolution_flag = False
    custom_resolution_text = '720'
    frame_rates = [60, 90, 120, 144, 165, 240]
    selected_frame_rate = 0
    custom_frame_rate_flag = False
    custom_frame_rate_text = '60'

    is_patching = False
    skip_frames = 0
    error_message = ''

    apktool_search_paths = ['C:\\Windows', '/usr/local/bin']
    for p in apktool_search_paths:
        if os.path.isfile(os.path.join(p, 'apktool.bat')):
            apktool_path = os.path.abspath(os.path.join(p, 'apktool.bat'))

    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    io = impl.io
    io.fonts.clear()
    io.fonts.add_font_from_file_ttf(
        os.path.join(fonts_path(), 'Roboto-Medium.ttf'), 24,
        io.fonts.get_glyph_ranges_latin()
    )
    tc_font = io.fonts.add_font_from_file_ttf(
        os.path.join(fonts_path(), 'NotoSansTC-Medium.otf'), 24,
        io.fonts.get_glyph_ranges_chinese_full()
    )
    kr_font = io.fonts.add_font_from_file_ttf(
        os.path.join(fonts_path(), 'NotoSansKR-Medium.ttf'), 24,
        io.fonts.get_glyph_ranges_korean()
    )
    impl.refresh_font_texture()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(io.display_size.x, io.display_size.y)
        imgui.begin('', flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE)

        imgui.text('apktool.bat Path:')
        if not apktool_path.endswith('apktool.bat'):
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.5, 0.0, 0.0)
        _, apktool_path = imgui.input_text('##apktool', apktool_path, 1024, flags=imgui.INPUT_TEXT_READ_ONLY)
        if not apktool_path.endswith('apktool.bat'):
            imgui.pop_style_color(1)
        imgui.same_line()
        if imgui.button('Browse apktool.bat...'):
            new_path = askopenfilename(filetypes=[('Batch', '*.bat')])
            if new_path:
                apktool_path = os.path.abspath(new_path)

        imgui.text('zipalign.exe Path:')
        if not zipalign_path.endswith('zipalign.exe'):
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.5, 0.0, 0.0)
        _, zipalign_path = imgui.input_text('##zipalign', zipalign_path, 1024, flags=imgui.INPUT_TEXT_READ_ONLY)
        if not zipalign_path.endswith('zipalign.exe'):
            imgui.pop_style_color(1)
        imgui.same_line()
        if imgui.button('Browse zipalign.exe...'):
            new_path = askopenfilename(filetypes=[('Executable', '*.exe')])
            if new_path:
                zipalign_path = os.path.abspath(new_path)
                if not apksigner_path.endswith('apksigner.bat'):
                    zipalign_dir = os.path.dirname(zipalign_path)
                    if os.path.isfile(os.path.join(zipalign_dir, 'apksigner.bat')):
                        apksigner_path = os.path.abspath(os.path.join(zipalign_dir, 'apksigner.bat'))

        imgui.text('apksigner.bat Path:')
        if not apksigner_path.endswith('apksigner.bat'):
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.5, 0.0, 0.0)
        _, apksigner_path = imgui.input_text('##apksigner', apksigner_path, 1024, flags=imgui.INPUT_TEXT_READ_ONLY)
        if not apksigner_path.endswith('apksigner.bat'):
            imgui.pop_style_color(1)
        imgui.same_line()
        if imgui.button('Browse apksigner.bat...'):
            new_path = askopenfilename(filetypes=[('Batch', '*.bat')])
            if new_path:
                apksigner_path = os.path.abspath(new_path)
                if not zipalign_path.endswith('zipalign.exe'):
                    apksigner_dir = os.path.dirname(apksigner_path)
                    if os.path.isfile(os.path.join(apksigner_dir, 'zipalign.exe')):
                        zipalign_path = os.path.abspath(os.path.join(apksigner_dir, 'zipalign.exe'))

        imgui.text('Game APK Path:')
        if not apk_path.endswith('.apk'):
            imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.5, 0.0, 0.0)
        if '劇場時光' in apk_path:
            imgui.push_font(tc_font)
        elif '밀리언 라이브!' in apk_path:
            imgui.push_font(kr_font)
        _, apk_path = imgui.input_text('##apk', apk_path, 1024, flags=imgui.INPUT_TEXT_READ_ONLY)
        if '劇場時光' in apk_path or '밀리언 라이브!' in apk_path:
            imgui.pop_font()
        if not apk_path.endswith('.apk'):
            imgui.pop_style_color(1)
        imgui.same_line()
        if imgui.button('Browse .apk...'):
            new_path = askopenfilename(filetypes=[('Android Package', '*.apk')])
            if new_path:
                apk_path = os.path.abspath(new_path)

        imgui.text('Resolution:')
        imgui.columns(2, border=False)
        if not custom_resolution_flag:
            _, selected_resolution = imgui.slider_int('##resolution', selected_resolution, min_value=0, max_value=len(resolutions)-1, format='')
            resolution = resolutions[selected_resolution]
        else:
            _, custom_resolution_text = imgui.input_text('##custom_res', custom_resolution_text, 5, flags=imgui.INPUT_TEXT_CHARS_DECIMAL)
            try:
                resolution = int(custom_resolution_text)
            except ValueError:
                resolution = 720
            if resolution < 240:
                resolution = 240
        imgui.same_line()
        imgui.text(f'{resolution}p')
        imgui.next_column()
        _, custom_resolution_flag = imgui.checkbox('Custom Resolution', custom_resolution_flag)
        imgui.columns(1)

        imgui.text('Frame Rate:')
        imgui.columns(2, border=False)
        if not custom_frame_rate_flag:
            _, selected_frame_rate = imgui.slider_int('##frame_rate', selected_frame_rate, min_value=0, max_value=len(frame_rates)-1, format='')
            frame_rate = frame_rates[selected_frame_rate]
        else:
            _, custom_frame_rate_text = imgui.input_text('##custom_fps', custom_frame_rate_text, 4, flags=imgui.INPUT_TEXT_CHARS_DECIMAL)
            try:
                frame_rate = int(custom_frame_rate_text)
            except ValueError:
                frame_rate = 60
            if frame_rate < 24:
                frame_rate = 24
        imgui.same_line()
        imgui.text(f'{frame_rate}fps')
        imgui.next_column()
        _, custom_frame_rate_flag = imgui.checkbox('Custom Frame Rate', custom_frame_rate_flag)
        imgui.columns(1)

        imgui.text('')

        if imgui.button('Patch', width=imgui.get_window_size()[0]):
            error_message = validate_input()
            if not error_message:
                is_patching = True
                skip_frames = 2

        if is_patching:
            imgui.open_popup('Patching')
        if imgui.begin_popup_modal('Patching', flags=imgui.WINDOW_NO_RESIZE)[0]:
            imgui.text('Please wait...')
            if not is_patching:
                imgui.close_current_popup()
            imgui.end_popup()

        if error_message:
            imgui.open_popup('Error')
            imgui.set_next_window_size(io.display_size.x-10, io.display_size.y*2/3)
        if imgui.begin_popup_modal('Error', flags=imgui.WINDOW_NO_RESIZE)[0]:
            imgui.text(error_message)
            if imgui.button('Close'):
                error_message = ''
                imgui.close_current_popup()
            imgui.end_popup()

        imgui.end()

        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

        if is_patching:
            if skip_frames > 0:
                # Skip some frames to show popup first before patching
                skip_frames -= 1
            else:
                try:
                    initialize()
                    apktool_decode()
                    apply_patch()
                    apktool_build()
                    zipalign()
                    apksigner()
                except Exception:
                    error_message = traceback.format_exc()
                finally:
                    collect_and_cleanup()
                    is_patching = False

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 800, 450
    window_name = "APK Patcher for MLTD"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


if __name__ == "__main__":
    main()
