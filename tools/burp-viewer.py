import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

from tkinter.filedialog import askopenfilename

from xml.etree import ElementTree as ET
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import gzip, json

key = b'do8PxbqYKV7cexTrt4J3fmgBtXXzu+dP'
iv = b'\x00' * 16

ids = []
methods = []
requests = []
responses = []
selected_id = -1

request_data = ''
request_raw = ''
request_json = ''
response_data = ''
response_raw = ''
response_json = ''
request_json_min = False
response_json_min = False

def decrypt_request(data):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    data = unpad(cipher.decrypt(b64decode(data, b'-_')), 16)
    data = bytearray(data)[16:]
    return json.loads(data)

def decrypt_response(data):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    data = unpad(cipher.decrypt(b64decode(data, b'-_')), 16)
    data = gzip.decompress(bytearray(data)[16:])
    return json.loads(data)

def load_file():
    global ids, methods, requests, responses, selected_id
    filename = askopenfilename()
    if not filename:
        return
    ids = []
    methods = []
    requests = []
    responses = []
    selected_id = -1
    update_data()
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        for item in root:
            host = item.find('host').text
            if 'appspot.com' in host:
                methods.append(item.find('path').text)
                request = b64decode(item.find('request').text).decode('utf-8')
                requests.append(request)
                response = b64decode(item.find('response').text).decode('utf-8')
                responses.append(response)
        ids = [n for n in range(len(methods))]
    except:
        pass

def update_data():
    global ids, requests, responses, selected_id
    global request_header, request_raw, request_json
    global response_header, response_raw, response_json
    global request_json_min, response_json_min
    
    if selected_id in ids:
        request = requests[selected_id].splitlines()
        request_header = '\n'.join(request[:-1])
        request_raw = request[-1]
        if request_json_min:
            request_json = json.dumps(
                decrypt_request(request_raw), ensure_ascii=False,
                separators=(',', ':')
            )
        else:
            request_json = json.dumps(
                decrypt_request(request_raw), ensure_ascii=False, indent=4
            )
        response = responses[selected_id].splitlines()
        response_header = '\n'.join(response[:-1])
        response_raw = response[-1]
        if response_json_min:
            response_json = json.dumps(
                decrypt_response(response_raw), ensure_ascii=False,
                separators=(',', ':')
            )
        else:
            response_json = json.dumps(
                decrypt_response(response_raw), ensure_ascii=False, indent=4
            )
    else:
        request_header = request_raw = request_json = ''
        response_header = response_raw = response_json = ''

def main():
    global ids, methods, requests, responses, selected_id
    global request_header, request_raw, request_json
    global response_header, response_raw, response_json
    global request_json_min, response_json_min

    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    io = impl.io
    io.fonts.clear()
    io.fonts.add_font_from_file_ttf(
        'fonts/Roboto-Medium.ttf', 24,
        io.fonts.get_glyph_ranges_latin()
    )
    tc_font = io.fonts.add_font_from_file_ttf(
        'fonts/NotoSansTC-Medium.otf', 24,
        io.fonts.get_glyph_ranges_chinese_full()
    )
    impl.refresh_font_texture()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(io.display_size.x, io.display_size.y)
        imgui.begin('', flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_MENU_BAR)

        if imgui.begin_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_open, _ = imgui.menu_item('Open')
                if clicked_open:
                    load_file()
                clicked_quit, _ = imgui.menu_item('Quit')
                if clicked_quit:
                    exit(1)
                imgui.end_menu()
            imgui.end_menu_bar()

        imgui.columns(3, border=False)

        imgui.begin_child('methods')
        imgui.columns(2, border=False)
        imgui.set_column_offset(1, 40)
        for i in ids:
            clicked, _ = imgui.selectable(
                str(i), selected_id == i, imgui.SELECTABLE_SPAN_ALL_COLUMNS
            )
            if clicked:
                selected_id = i
                update_data()
            imgui.next_column()
            imgui.text(methods[i])
            imgui.next_column()
        imgui.columns(1)
        imgui.end_child()
        imgui.next_column()

        show_request_header, _ = imgui.collapsing_header('Request Header')
        if show_request_header:
            if imgui.button('Copy Request Header'):
                glfw.set_clipboard_string(None, request_header)
            imgui.input_text_multiline(
                '##request header', request_header, len(request_header) + 2,
                -1, flags=imgui.INPUT_TEXT_READ_ONLY
            )
        show_request_raw, _ = imgui.collapsing_header(
            'Request Data (Raw, Encrypted)',
            flags=imgui.TREE_NODE_DEFAULT_OPEN
        )
        if show_request_raw:
            imgui.input_text(
                '##request raw', request_raw, len(request_raw) + 2,
                flags=imgui.INPUT_TEXT_READ_ONLY
            )
            imgui.same_line()
            if imgui.button('Copy Request Data (Raw)'):
                glfw.set_clipboard_string(None, request_raw)
        show_request_json, _ = imgui.collapsing_header(
            'Request Data (JSON, Decrypted)',
            flags=imgui.TREE_NODE_DEFAULT_OPEN
        )
        if show_request_json:         
            if imgui.radio_button('Minify Request JSON', request_json_min):
                request_json_min = not request_json_min
                update_data()
            imgui.same_line()
            if imgui.button('Copy Request Data (JSON)'):
                glfw.set_clipboard_string(None, request_json)
            with imgui.font(tc_font):
                imgui.input_text_multiline(
                    '##request json', request_json,
                    len(request_json.encode('utf-8')) + 2, -1, height=-1,
                    flags=imgui.INPUT_TEXT_READ_ONLY
                )
        imgui.next_column()

        show_response_header, _ = imgui.collapsing_header('Response Header')
        if show_response_header:
            if imgui.button('Copy Response Header'):
                glfw.set_clipboard_string(None, response_header)
            imgui.input_text_multiline(
                '##response header', response_header, len(response_header) + 2,
                -1, flags=imgui.INPUT_TEXT_READ_ONLY
            )
        show_response_raw, _ = imgui.collapsing_header(
            'Response Data (Raw, Encrypted)',
            flags=imgui.TREE_NODE_DEFAULT_OPEN
        )
        if show_response_raw:
            imgui.input_text(
                '##response raw', response_raw, len(response_raw) + 2,
                flags=imgui.INPUT_TEXT_READ_ONLY
            )
            imgui.same_line()
            if imgui.button('Copy Response Data (Raw)'):
                glfw.set_clipboard_string(None, response_raw)
        show_response_json, _ = imgui.collapsing_header(
            'Response Data (JSON, Decrypted)',
            flags=imgui.TREE_NODE_DEFAULT_OPEN
        )
        if show_response_json:     
            if imgui.radio_button('Minify Response JSON', response_json_min):
                response_json_min = not response_json_min
                update_data()
            imgui.same_line()
            if imgui.button('Copy Response Data (JSON)'):
                glfw.set_clipboard_string(None, response_json)
            with imgui.font(tc_font):
                imgui.input_text_multiline(
                    '##response json', response_json,
                    len(response_json.encode('utf-8')) + 2, -1, height=-1,
                    flags=imgui.INPUT_TEXT_READ_ONLY
                )
        imgui.columns(1)
        imgui.end()

        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1920, 1000
    window_name = "Burp Suite HTTP History Viewer for MLTD"

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
