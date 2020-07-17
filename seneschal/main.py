#!python -u
# -*- coding: utf-8 -*-
# pylint: disable=locally-disabled, too-few-public-methods
# pylint: disable=locally-disabled, no-name-in-module
# pylint: disable=locally-disabled, c-extension-no-member
# pylama: ignore: E265
"""
App master.

https://github.com/machawk1/wail/blob/osagnostic/bundledApps/MAKEFILE.bat
https://github.com/anthony-tuininga/cx_Freeze
https://github.com/cdrx/docker-pyinstaller
"""
import os
import platform
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.base import EventLoop

from cefpython3 import cefpython as cef
#%% CEF import


class CefBrowser(Widget):
    """
    Keyboard mode: "global" or "local".

    1. Global mode forwards keys to CEF all the time.
    2. Local mode forwards keys to CEF only when an editable
       control is focused (input type=text|password or textarea).
    """
    keyboard_mode = "global"

    def __init__(self, start_url='http://www.google.com/', **kwargs):
        """
        Represent a browser widget for kivy.

        which can be used like a normal widget.
        """
        super(CefBrowser, self).__init__(**kwargs)

        self.start_url = start_url

        #Workaround for flexible size:
        #start browser when the height has changed (done by layout)
        #This has to be done like this because I wasn't able to change
        #the texture size
        #until runtime without core-dump.
        self.bind(size=self.size_changed)

    starting = True

    def size_changed(self, *kwargs):
        """
        Create the browser.

        When the height of the cefbrowser widget got changed.
        """
        if self.starting:
            if self.height != 100:
                self.start_cef()
                self.starting = False
        else:
            self.texture = Texture.create(
                size=self.size,
                colorfmt='rgba',
                bufferfmt='ubyte'
            )
            self.texture.flip_vertical()
            with self.canvas:
                Color(1, 1, 1)
                # This will cause segmentation fault:
                # | self.rect = Rectangle(size=self.size, texture=self.texture)
                # Update only the size:
                self.rect.size = self.size
            self.browser.WasResized()

    def _cef_mes(self, *kwargs):
        """Get called every frame."""
        cef.MessageLoopWork()

    def _update_rect(self, *kwargs):
        """Get called whenever the texture got updated.
        => we need to reset the texture for the rectangle
        """
        self.rect.texture = self.texture

    def start_cef(self):
        """Starts CEF.
        """
        # create texture & add it to canvas
        self.texture = Texture.create(
            size=self.size,
            colorfmt='rgba',
            bufferfmt='ubyte'
        )
        self.texture.flip_vertical()
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(size=self.size, texture=self.texture,
                                  pos=self.pos)

        #configure cef
        cef.g_debug = True
        cef.g_debugFile = "debug.log"
        settings = {
            "log_severity": cef.LOGSEVERITY_INFO,
            "log_file": "debug.log",
            "release_dcheck_enabled": True,  # Enable only when debugging.
            # This directories must be set on Linux
            "locales_dir_path":
            cef.GetModuleDirectory() + os.sep + "locales",
            "resources_dir_path": cef.GetModuleDirectory()
        }

        #start idle
        Clock.schedule_interval(self._cef_mes, 0)

        #init CEF
        cef.Initialize(settings)

        #WindowInfo offscreen flag
        window_info = cef.WindowInfo()
        window_info.SetAsOffscreen(0)

        # Create Broswer and naviagte to empty page <= OnPaint won't
        # get called yet
        browser_settings = {}
        # The render handler callbacks are not yet set, thus an
        # error report will be thrown in the console (when release
        # DCHECKS are enabled), however don't worry, it is harmless.
        # This is happening because calling GetViewRect will return
        # false. That's why it is initially navigating to "about:blank".
        # Later, a real url will be loaded using the LoadUrl() method
        # and the GetViewRect will be called again. This time the render
        # handler callbacks will be available, it will work fine from
        # this point.
        # --
        # Do not use "about:blank" as navigateUrl - this will cause
        # the GoBack() and GoForward() methods to not work.
        self.browser = cef.CreateBrowserSync(
            window_info,
            browser_settings,
            navigateUrl=self.start_url
        )

        #set focus
        self.browser.SendFocusEvent(True)

        self._client_handler = ClientHandler(self)
        self.browser.SetClientHandler(self._client_handler)
        self.set_js_bindings()

        # Call WasResized() => force cef to call GetViewRect() and
        # OnPaint afterwards
        self.browser.WasResized()

        # The browserWidget instance is required in OnLoadingStateChange().
        self.browser.SetUserData("browserWidget", self)

        if self.keyboard_mode == "global":
            self.request_keyboard()

        # Clock.schedule_once(self.change_url, 5)

    _client_handler = None
    _js_bindings = None

    def set_js_bindings(self):
        if not self._js_bindings:
            self._js_bindings = cef.JavascriptBindings(
                bindToFrames=True, bindToPopups=True)
            self._js_bindings.SetFunction("__kivy__request_keyboard",
                                          self.request_keyboard)
            self._js_bindings.SetFunction("__kivy__release_keyboard",
                                          self.release_keyboard)
        self.browser.SetJavascriptBindings(self._js_bindings)

    def change_url(self, url, *kwargs):
        # Doing a javascript redirect instead of Navigate()
        # solves the js bindings error. The url here need to
        # be preceded with "http://". Calling StopLoad()
        # might be a good idea before making the js navigation.

        self.browser.StopLoad()
        self.browser.GetMainFrame().ExecuteJavascript(
            f"window.location='{url}'"
        )

        # Do not use Navigate() or GetMainFrame()->LoadURL(),
        # as it causes the js bindings to be removed. There is
        # a bug in CEF, that happens after a call to Navigate().
        # The OnBrowserDestroyed() callback is fired and causes
        # the js bindings to be removed. See this topic for more
        # details:
        # http://www.magpcss.org/ceforum/viewtopic.php?f=6&t=11009

        # OFF:
        # | self.browser.Navigate("http://www.youtube.com/")

    _keyboard = None

    def request_keyboard(self):
        print("request_keyboard()")
        self._keyboard = EventLoop.window.request_keyboard(
            self.release_keyboard, self)
        self._keyboard.bind(on_key_down=self.on_key_down)
        self._keyboard.bind(on_key_up=self.on_key_up)
        self.is_shift1 = False
        self.is_shift2 = False
        self.is_ctrl1 = False
        self.is_ctrl2 = False
        self.is_alt1 = False
        self.is_alt2 = False
        # Not sure if it is still required to send the focus
        # (some earlier bug), but it shouldn't hurt to call it.
        self.browser.SendFocusEvent(True)

    def release_keyboard(self):
        """
        When using local keyboard mode.

        Do all the request and releases of the keyboard through js bindings,
        otherwise some focus problems arise.
        """
        self.is_shift1 = False
        self.is_shift2 = False
        self.is_ctrl1 = False
        self.is_ctrl2 = False
        self.is_alt1 = False
        self.is_alt2 = False
        if not self._keyboard:
            return
        print("release_keyboard()")
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard.unbind(on_key_up=self.on_key_up)
        self._keyboard.release()

    # Kivy does not provide modifiers in on_key_up, but these
    # must be sent to CEF as well.
    is_shift1 = False
    is_shift2 = False
    is_ctrl1 = False
    is_ctrl2 = False
    is_alt1 = False
    is_alt2 = False

    def on_key_down(self, _, keycode, _text, modifiers):
        """
        Notes.

        - right alt modifier is not sent by Kivy through modifiers param.
         print("on_key_down(): keycode = %s, text = %s, modifiers = %s" % (
                 keycode, text, modifiers))
        """
        if keycode[0] == 27:
            # On escape release the keyboard, see the injected
            # javascript in OnLoadStart().
            self.browser.GetFocusedFrame().ExecuteJavascript(
                "__kivy__on_escape()")
            return

        cef_modifiers = cef.EVENTFLAG_NONE
        if "shift" in modifiers:
            cef_modifiers |= cef.EVENTFLAG_SHIFT_DOWN
        if "ctrl" in modifiers:
            cef_modifiers |= cef.EVENTFLAG_CONTROL_DOWN
        if "alt" in modifiers:
            cef_modifiers |= cef.EVENTFLAG_ALT_DOWN
        if "capslock" in modifiers:
            cef_modifiers |= cef.EVENTFLAG_CAPS_LOCK_ON
        # print("on_key_down(): cef_modifiers = %s" % cef_modifiers)
        cef_keycode = self.translate_to_cef_keycode(keycode[0])
        key_event = {"type": cef.KEYEVENT_RAWKEYDOWN,
                     "native_key_code": cef_keycode,
                     "modifiers": cef_modifiers}
        # print("keydown key_event: %s" % key_event)
        self.browser.SendKeyEvent(key_event)
        if keycode[0] == 304:
            self.is_shift1 = True
        elif keycode[0] == 303:
            self.is_shift2 = True
        elif keycode[0] == 306:
            self.is_ctrl1 = True
        elif keycode[0] == 305:
            self.is_ctrl2 = True
        elif keycode[0] == 308:
            self.is_alt1 = True
        elif keycode[0] == 313:
            self.is_alt2 = True

    def on_key_up(self, _, keycode):
        # print("on_key_up(): keycode = %s" % (keycode,))
        cef_modifiers = cef.EVENTFLAG_NONE
        if self.is_shift1 or self.is_shift2:
            cef_modifiers |= cef.EVENTFLAG_SHIFT_DOWN
        if self.is_ctrl1 or self.is_ctrl2:
            cef_modifiers |= cef.EVENTFLAG_CONTROL_DOWN
        if self.is_alt1:
            cef_modifiers |= cef.EVENTFLAG_ALT_DOWN
        # Capslock todo.
        cef_keycode = self.translate_to_cef_keycode(keycode[0])
        key_event = {"type": cef.KEYEVENT_KEYUP,
                     "native_key_code": cef_keycode,
                     "modifiers": cef_modifiers}
        # print("keyup key_event: %s" % key_event)
        self.browser.SendKeyEvent(key_event)
        key_event = {"type": cef.KEYEVENT_CHAR,
                     "native_key_code": cef_keycode,
                     "modifiers": cef_modifiers}
        # print("char key_event: %s" % key_event)
        self.browser.SendKeyEvent(key_event)
        if keycode[0] == 304:
            self.is_shift1 = False
        elif keycode[0] == 303:
            self.is_shift2 = False
        elif keycode[0] == 306:
            self.is_ctrl1 = False
        elif keycode[0] == 305:
            self.is_ctrl2 = False
        elif keycode[0] == 308:
            self.is_alt1 = False
        elif keycode[0] == 313:
            self.is_alt2 = False

    def translate_to_cef_keycode(self, keycode):
        """
        This works on Linux.

        , but on Windows the key mappings will probably be different.

        What if the Kivy keyboard layout is changed
        from qwerty to azerty? (F1 > options..)
        """
        cef_keycode = keycode
        if self.is_alt2:
            # The key mappings here for right alt were tested
            # with the utf-8 charset on a webpage. If the charset
            # is different there is a chance they won't work correctly.
            alt2_map = {
                # tilde
                "96": 172,
                # 0-9 (48..57)
                "48": 125, "49": 185, "50": 178, "51": 179, "52": 188,
                "53": 189, "54": 190, "55": 123, "56": 91, "57": 93,
                # minus
                "45": 92,
                # a-z (97..122)
                "97": 433, "98": 2771, "99": 486, "100": 240, "101": 490,
                "102": 496, "103": 959, "104": 689, "105": 2301, "106": 65121,
                "107": 930, "108": 435, "109": 181, "110": 497, "111": 243,
                "112": 254, "113": 64, "114": 182, "115": 438, "116": 956,
                "117": 2302, "118": 2770, "119": 435, "120": 444, "121": 2299,
                "122": 447,
            }
            if str(keycode) in alt2_map:
                cef_keycode = alt2_map[str(keycode)]
            else:
                print("Kivy to CEF key mapping not found (right alt), "
                      f"key code = {keycode}")
            shift_alt2_map = {
                # tilde
                "96": 172,
                # 0-9 (48..57)
                "48": 176, "49": 161, "50": 2755, "51": 163, "52": 36,
                "53": 2756, "54": 2757, "55": 2758, "56": 2761, "57": 177,
                # minus
                "45": 191,
                # A-Z (97..122)
                "97": 417, "98": 2769, "99": 454, "100": 208, "101": 458,
                "102": 170, "103": 957, "104": 673, "105": 697, "106": 65122,
                "107": 38, "108": 419, "109": 186, "110": 465, "111": 211,
                "112": 222, "113": 2009, "114": 174, "115": 422, "116": 940,
                "117": 2300, "118": 2768, "119": 419, "120": 428, "121": 165,
                "122": 431,
                # special: <>?  :"  {}
                "44": 215, "46": 247, "47": 65110,
                "59": 65113, "39": 65114,
                "91": 65112, "93": 65108,
            }
            if self.is_shift1 or self.is_shift2:
                if str(keycode) in shift_alt2_map:
                    cef_keycode = shift_alt2_map[str(keycode)]
                else:
                    print("Kivy to CEF key mapping not found "
                          f"(shift + right alt), key code = {keycode}")
        elif self.is_shift1 or self.is_shift2:
            shift_map = {
                # tilde
                "96": 126,
                # 0-9 (48..57)
                "48": 41, "49": 33, "50": 64, "51": 35, "52": 36, "53": 37,
                "54": 94, "55": 38, "56": 42, "57": 40,
                # minus, plus
                "45": 95, "61": 43,
                # a-z (97..122)
                "97": 65, "98": 66, "99": 67, "100": 68, "101": 69, "102": 70,
                "103": 71, "104": 72, "105": 73, "106": 74, "107": 75,
                "108": 76, "109": 77, "110": 78, "111": 79, "112": 80,
                "113": 81, "114": 82, "115": 83, "116": 84, "117": 85,
                "118": 86, "119": 87, "120": 88, "121": 89, "122": 90,
                # special: <>?  :"  {}
                "44": 60, "46": 62, "47": 63,
                "59": 58, "39": 34,
                "91": 123, "93": 125,
            }
            if str(keycode) in shift_map:
                cef_keycode = shift_map[str(keycode)]
        # Other keys:
        other_keys_map = {
            # Escape
            "27": 65307,
            # F1-F12
            "282": 65470, "283": 65471, "284": 65472, "285": 65473,
            "286": 65474, "287": 65475, "288": 65476, "289": 65477,
            "290": 65478, "291": 65479, "292": 65480, "293": 65481,
            # Tab
            "9": 65289,
            # Left Shift, Right Shift
            "304": 65505, "303": 65506,
            # Left Ctrl, Right Ctrl
            "306": 65507, "305": 65508,
            # Left Alt, Right Alt
            "308": 65513, "313": 65027,
            # Backspace
            "8": 65288,
            # Enter
            "13": 65293,
            # PrScr, ScrLck, Pause
            "316": 65377, "302": 65300, "19": 65299,
            # Insert, Delete,
            # Home, End,
            # Pgup, Pgdn
            "277": 65379, "127": 65535,
            "278": 65360, "279": 65367,
            "280": 65365, "281": 65366,
            # Arrows (left, up, right, down)
            "276": 65361, "273": 65362, "275": 65363, "274": 65364,
        }
        if str(keycode) in other_keys_map:
            cef_keycode = other_keys_map[str(keycode)]
        return cef_keycode

    def go_forward(self):
        """Going to forward in browser history
        """
        print("go forward")
        self.browser.GoForward()

    def go_back(self):
        """Going back in browser history
        """
        print("go back")
        self.browser.GoBack()

    def on_touch_down(self, touch, *kwargs):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)

        y = self.height - touch.pos[1] + self.pos[1]
        x = touch.x - self.pos[0]
        self.browser.SendMouseClickEvent(
            x,
            y,
            cef.MOUSEBUTTON_LEFT,
            mouseUp=False,
            clickCount=1
        )

        return True

    def on_touch_move(self, touch, *kwargs):
        if touch.grab_current is not self:
            return

        y = self.height - touch.pos[1] + self.pos[1]
        x = touch.x - self.pos[0]
        self.browser.SendMouseMoveEvent(x, y, mouseLeave=False)

        return True

    def on_touch_up(self, touch, *kwargs):
        if touch.grab_current is not self:
            return

        y = self.height - touch.pos[1] + self.pos[1]
        x = touch.x - self.pos[0]
        self.browser.SendMouseClickEvent(
            x,
            y,
            cef.MOUSEBUTTON_LEFT,
            mouseUp=True, clickCount=1
        )

        touch.ungrab(self)

        return True


class ClientHandler:
    """ClientHandler."""

    def __init__(self, browser_widget):
        self.browserWidget = browser_widget

    def _fix_select_boxes(self, frame):
        # This is just a temporary fix, until proper Popup widgets
        # painting is implemented (PET_POPUP in OnPaint). Currently
        # there is no way to obtain a native window handle (GtkWindow
        # pointer) in Kivy, and this may cause things like context menus,
        # select boxes and plugins not to display correctly. Although,
        # this needs to be tested. The popup widget buffers are
        # available in a separate paint buffer, so they could positioned
        # freely so that it doesn't go out of the window. So the native
        # window handle might not necessarily be required to make it work
        # in most cases (99.9%). Though, this still needs testing to confirm.
        # --
        # See this topic on the CEF Forum regarding the NULL window handle:
        # http://www.magpcss.org/ceforum/viewtopic.php?f=6&t=10851
        # --
        # See also a related topic on the Kivy-users group:
        # https://groups.google.com/d/topic/kivy-users/WdEQyHI5vTs/discussion
        # --
        # The javascript select boxes library used:
        # http://marcj.github.io/jquery-selectBox/
        # --
        # Cannot use "file://" urls to load local resources, error:
        # | Not allowed to load local resource
        print("_fix_select_boxes()")
        resources_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "kivy-select-boxes")
        if not os.path.exists(resources_dir):
            print("The kivy-select-boxes directory does not exist, "
                  "select boxes fix won't be applied.")
            return
        js_file = os.path.join(resources_dir, "kivy-selectBox.js")

        with open(js_file, "r") as myfile:
            js_content = myfile.read()
        css_file = os.path.join(resources_dir, "kivy-selectBox.css")
        css_content = ""
        with open(css_file, "r") as myfile:
            css_content = myfile.read()
        css_content = css_content.replace("\r", "")
        css_content = css_content.replace("\n", "")
        js_code = """
            %(js_content)s
            var head = document.getElementsByTagName('head')[0];
            var style = document.createElement('style');
            style.type = 'text/css';
            style.appendChild(document.createTextNode("%(css_content)s"));
            head.appendChild(style);
        """ % locals()
        frame.ExecuteJavascript(js_code,
                                "kivy_.py > ClientHandler > OnLoadStart > "
                                "_fix_select_boxes()")

    def OnLoadStart(self, browser, frame):
        self._fix_select_boxes(frame)
        browserWidget = browser.GetUserData("browserWidget")
        if browserWidget and browserWidget.keyboard_mode == "local":
            print("OnLoadStart(): injecting focus listeners for text controls")
            # The logic is similar to the one found in kivy-berkelium:
            # https://github.com/kivy/kivy-berkelium/blob/master/berkelium/__init__.py
            js_code = """
                var __kivy__keyboard_requested = false;
                function __kivy__keyboard_interval() {
                    var element = document.activeElement;
                    if (!element) {
                        return;
                    }
                    var tag = element.tagName;
                    var type = element.type;
                    if (tag == "INPUT" && (type == "" || type == "text"
                            || type == "password") || tag == "TEXTAREA") {
                        if (!__kivy__keyboard_requested) {
                            __kivy__request_keyboard();
                            __kivy__keyboard_requested = true;
                        }
                        return;
                    }
                    if (__kivy__keyboard_requested) {
                        __kivy__release_keyboard();
                        __kivy__keyboard_requested = false;
                    }
                }
                function __kivy__on_escape() {
                    if (document.activeElement) {
                        document.activeElement.blur();
                    }
                    if (__kivy__keyboard_requested) {
                        __kivy__release_keyboard();
                        __kivy__keyboard_requested = false;
                    }
                }
                setInterval(__kivy__keyboard_interval, 100);
            """
            frame.ExecuteJavascript(js_code,
                                    "kivy_.py > ClientHandler > OnLoadStart")

    def OnLoadEnd(self, browser, frame, httpStatusCode):
        """
        End Load event.

        Browser lost its focus after the LoadURL() and the
        OnBrowserDestroyed() callback bug. When keyboard mode
        is local the fix is in the request_keyboard() method.
        Call it from OnLoadEnd only when keyboard mode is global.
        """
        browserWidget = browser.GetUserData("browserWidget")
        if browserWidget and browserWidget.keyboard_mode == "global":
            browser.SendFocusEvent(True)

    def OnLoadingStateChange(self, browser, isLoading, canGoBack,
                             canGoForward):
        """Change State."""
        print("OnLoadingStateChange(): isLoading = {isLoading}")
        browserWidget = browser.GetUserData("browserWidget")

    def OnPaint(self, browser, paintElementType, _, buffer, _width,
                _height):
        """Paint."""
        # print "OnPaint()"
        if paintElementType != cef.PET_VIEW:
            print("Popups aren't implemented yet")
            return

        #update buffer
        buffer = buffer.GetString(mode="bgra", origin="top-left")

        #update texture of canvas rectangle
        self.browserWidget.texture.blit_buffer(
            buffer,
            colorfmt='bgra',
            bufferfmt='ubyte'
        )

        self.browserWidget._update_rect()

        return True

    def GetViewRect(self, rect):
        """Get view rect."""
        width, height = self.browserWidget.texture.size
        rect.append(0)
        rect.append(0)
        rect.append(width)
        rect.append(height)
        #print("GetViewRect(): %s x %s" % (width, height))
        return True


#%% Configuration
WIDTH = 900
HEIGHT = 640

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")


class MainFrame():
    """MainFrame."""

    def __init__(self):
        """Initialize."""
        self.browser = None

    def clear_browser_references(self):
        """
        Clear browser references that you keep anywhere in your code.

        All references must be cleared for CEF to shutdown cleanly.
        """
        self.browser = None


class FirstKivy(App):
    """First kivy class."""

    def build(self):
        """Build."""
        return Label(text="Hello Kivy!")

#%%


if __name__ == '__main__':

    Builder.load_string("""
<BrowserLayout>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: '18dp'
        Button:
            text: "Back"
            on_press: browser.go_back()
        Button:
            text: "Forward"
            on_press: browser.go_forward()
    CefBrowser:
        id: browser
""")

    class BrowserLayout(BoxLayout):
        """BrowserLayout."""
        pass

    class CefBrowserApp(App):
        """CefBrowserApp."""

        def build(self):
            """Build."""
            return BrowserLayout()

    CefBrowserApp().run()

    cef.Shutdown()
