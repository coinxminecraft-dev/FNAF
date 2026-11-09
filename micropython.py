import math
import os
import re
import sys
import array
import pygame

__all__ = ["run", "screen", "mouse", "keyboard", "audio", "system", "sprites", "random", "Math"]

pygame.init()

# ---------------------------------------------------------------------------
# Outils
# ---------------------------------------------------------------------------

_RGB_RE = re.compile(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\s*\)")

def _parse_color(c):
    """Accepte rgb(), #hex, noms de couleurs, tuples..."""
    if isinstance(c, (tuple, list)):
        return tuple(int(v) for v in c[:3])
    if isinstance(c, str):
        m = _RGB_RE.match(c.strip())
        if m:
            return tuple(max(0, min(255, int(float(m.group(i))))) for i in (1, 2, 3))
        try:
            col = pygame.Color(c.strip())
            return (col.r, col.g, col.b)
        except ValueError:
            pass
    return (255, 255, 255)


# ---------------------------------------------------------------------------
# Sprites
# ---------------------------------------------------------------------------

class _Sprites:
    def __init__(self):
        self.folder = "sprites"
        self._images = {}
        self._warned = set()

    def get(self, name):
        if name in self._images:
            return self._images[name]

        img = None

        for ext in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            path = os.path.join(self.folder, name + ext)
            if os.path.isfile(path):
                img = pygame.image.load(path).convert_alpha()
                break

        if img is None:
            if name not in self._warned:
                print(f"[microstudio] sprite introuvable : {name!r}")
                self._warned.add(name)

            img = pygame.Surface((16, 16), pygame.SRCALPHA)
            img.fill((255, 0, 255))

        self._images[name] = img
        return img

    def add(self, name, surface):
        self._images[name] = surface.convert_alpha()


sprites = _Sprites()


# ---------------------------------------------------------------------------
# Écran
# ---------------------------------------------------------------------------

class _Screen:
    def __init__(self):
        self.width = 1600
        self.height = 720
        self.surface = None
        self._window = None
        self._color = (255, 255, 255)
        self._alpha = 1.0
        self._lw = 1
        self._rot = 0.0
        self._sx = 1.0
        self._sy = 1.0
        self._ax = 0.0
        self._ay = 0.0
        self._font_name = None
        self._fonts = {}
        self._scaled_cache = {}

    def _setup(self, width, height, scale, title):
        self.width, self.height, self.scale = width, height, scale
        self._window = pygame.display.set_mode((int(width * scale), int(height * scale)))
        pygame.display.set_caption(title)
        self.surface = pygame.Surface((width, height)).convert()

    def _present(self):
        pygame.transform.scale(self.surface, self._window.get_size(), self._window)
        pygame.display.flip()

    def _px(self, x, y):
        return self.width / 2 + x, self.height / 2 - y

    def _col(self, c):
        return self._color if c is None else _parse_color(c)

    def setColor(self, color):
        self._color = _parse_color(color)

    def setAlpha(self, alpha):
        self._alpha = max(0.0, min(1.0, alpha))

    def setLineWidth(self, w):
        self._lw = max(1, int(round(w)))

    def setDrawRotation(self, deg):
        self._rot = deg

    def setDrawScale(self, sx, sy=None):
        self._sx = sx
        self._sy = sx if sy is None else sy

    def setDrawAnchor(self, ax, ay):
        self._ax, self._ay = ax, ay

    def setFont(self, name):
        self._font_name = name
        self._fonts.clear()

    def setTranslation(self, *_):
        pass

    def _shape(self, color, fn):
        col = self._col(color)

        if self._alpha >= 1:
            fn(self.surface, col)
        else:
            tmp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fn(tmp, col + (int(self._alpha * 255),))
            self.surface.blit(tmp, (0, 0))

    def clear(self, color=None):
        self.surface.fill(self._col(color) if color is not None else (0, 0, 0))

    def fillRect(self, x, y, w, h, color=None):
        cx, cy = self._px(x, y)
        r = pygame.Rect(0, 0, w, h)
        r.center = (round(cx), round(cy))
        self._shape(color, lambda s, c: pygame.draw.rect(s, c, r))

    def drawRect(self, x, y, w, h, color=None):
        cx, cy = self._px(x, y)
        r = pygame.Rect(0, 0, w, h)
        r.center = (round(cx), round(cy))
        lw = self._lw
        self._shape(color, lambda s, c: pygame.draw.rect(s, c, r, lw))

    def fillRound(self, x, y, w, h, color=None):
        cx, cy = self._px(x, y)
        r = pygame.Rect(0, 0, abs(w), abs(h))
        r.center = (round(cx), round(cy))
        self._shape(color, lambda s, c: pygame.draw.ellipse(s, c, r))

    def drawRound(self, x, y, w, h, color=None):
        cx, cy = self._px(x, y)
        r = pygame.Rect(0, 0, abs(w), abs(h))
        r.center = (round(cx), round(cy))
        lw = self._lw
        self._shape(color, lambda s, c: pygame.draw.ellipse(s, c, r))

    def drawLine(self, x1, y1, x2, y2, color=None):
        a, b = self._px(x1, y1), self._px(x2, y2)
        lw = self._lw
        self._shape(color, lambda s, c: pygame.draw.line(s, c, a, b, lw))

    def fillPolygon(self, *pts):
        color = None
        if len(pts) % 2 == 1:
            *pts, color = pts
        pts = [self._px(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
        self._shape(color, lambda s, c: pygame.draw.polygon(s, c, pts))

    def drawPolygon(self, *pts):
        color = None
        if len(pts) % 2 == 1:
            *pts, color = pts
        pts = [self._px(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
        lw = self._lw
        self._shape(color, lambda s, c: pygame.draw.polygon(s, c, pts, lw))

    def drawPolyline(self, *pts):
        color = None
        if len(pts) % 2 == 1:
            *pts, color = pts
        pts = [self._px(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
        lw = self._lw
        self._shape(color, lambda s, c: pygame.draw.lines(s, c, False, pts, lw))

    def _blit(self, surf, x, y):
        if self._sx != 1 or self._sy != 1:
            surf = pygame.transform.scale(
                surf,
                (
                    max(1, int(surf.get_width() * abs(self._sx))),
                    max(1, int(surf.get_height() * abs(self._sy)))
                )
            )

        if self._rot:
            surf = pygame.transform.rotozoom(surf, self._rot, 1)

        if self._alpha < 1:
            surf = surf.copy()
            surf.set_alpha(int(self._alpha * 255))

        w, h = surf.get_size()
        cx, cy = self._px(x - self._ax * w / 2, y - self._ay * h / 2)
        self.surface.blit(surf, surf.get_rect(center=(round(cx), round(cy))))

    def drawSprite(self, name, x, y, width, height=None):
        img = sprites.get(name)

        if height is None:
            height = width * img.get_height() / img.get_width()

        size = (max(1, int(abs(width))), max(1, int(abs(height))))
        key = (name, size)
        scaled = self._scaled_cache.get(key)

        if scaled is None:
            scaled = pygame.transform.scale(img, size)
            self._scaled_cache[key] = scaled

        if width < 0 or (height is not None and height < 0):
            scaled = pygame.transform.flip(scaled, width < 0, height < 0)

        self._blit(scaled, x, y)

    def _font(self, size):
        size = max(1, int(size))
        f = self._fonts.get(size)

        if f is None:
            if self._font_name and os.path.isfile(str(self._font_name)):
                f = pygame.font.Font(self._font_name, size)
            elif self._font_name:
                f = pygame.font.SysFont(self._font_name, size)
            else:
                f = pygame.font.Font(None, int(size * 1.3))

            self._fonts[size] = f

        return f

    def drawText(self, text, x, y, size=20, color=None):
        surf = self._font(size).render(str(text), True, self._col(color))
        self._blit(surf, x, y)

    def textWidth(self, text, size=20):
        return self._font(size).size(str(text))[0]


screen = _Screen()


# ---------------------------------------------------------------------------
# Souris
# ---------------------------------------------------------------------------

class _Mouse:
    def __init__(self):
        self.x = 0
        self.y = 0

        self.left = 0
        self.middle = 0
        self.right = 0
        self.pressed = 0

        # Clics détectés sur une seule frame
        self.click = False
        self.left_click = False
        self.middle_click = False
        self.right_click = False

        self._previous_left = 0
        self._previous_middle = 0
        self._previous_right = 0

        self.wheel = 0
        self.visible = True

    def _update(self):
        px, py = pygame.mouse.get_pos()
        self.x = px / screen.scale - screen.width / 2
        self.y = screen.height / 2 - py / screen.scale

        l, m, r = pygame.mouse.get_pressed(3)

        self.left = int(l)
        self.middle = int(m)
        self.right = int(r)
        self.pressed = int(l or m or r)

        # True uniquement lors du début du clic
        self.left_click = bool(l and not self._previous_left)
        self.middle_click = bool(m and not self._previous_middle)
        self.right_click = bool(r and not self._previous_right)

        self.click = (
            self.left_click
            or self.middle_click
            or self.right_click
        )

        self._previous_left = int(l)
        self._previous_middle = int(m)
        self._previous_right = int(r)


mouse = _Mouse()

# ---------------------------------------------------------------------------
# Clavier
# ---------------------------------------------------------------------------

_ALIASES = {
    "ENTER": "RETURN",
    "ESCAPE": "ESCAPE",
    "SHIFT": "LSHIFT",
    "CTRL": "LCTRL",
    "ALT": "LALT",
    "BACKSPACE": "BACKSPACE",
    "DELETE": "DELETE"
}

def _keycode(name):
    name = _ALIASES.get(name, name)

    if name.startswith("DIGIT_"):
        name = name[6:]

    attr = "K_" + name.lower()
    code = getattr(pygame, attr, None)

    if code is None:
        raise AttributeError(f"touche inconnue : {name}")

    return code


class _KeyView:
    def __init__(self, getter):
        self._get = getter

    def __getattr__(self, name):
        return 1 if self._get(_keycode(name.upper())) else 0


class _Keyboard:
    def __init__(self):
        self._pressed_now = set()
        self._released_now = set()

        self.press = _KeyView(lambda k: k in self._pressed_now)
        self.release = _KeyView(lambda k: k in self._released_now)

        self.typed = ""

    def __getattr__(self, name):
        if name.startswith("_") or name in ("press", "release", "typed"):
            raise AttributeError(name)

        return 1 if pygame.key.get_pressed()[_keycode(name.upper())] else 0

    def _clear(self):
        self._pressed_now.clear()
        self._released_now.clear()
        self.typed = ""


keyboard = _Keyboard()


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

class _Audio:
    def __init__(self):
        self.folder_sounds = "sounds"
        self.folder_music = "music"
        self._cache = {}
        self._ok = False

    def _init(self):
        if not self._ok:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
                self._ok = True
            except pygame.error:
                print("[microstudio] audio indisponible")

        return self._ok

    def beep(self, freq=440, duration=0.15, volume=0.5):
        if not self._init():
            return

        rate = 22050
        n = int(rate * duration)

        buf = array.array(
            "h",
            (
                int(
                    32767 * volume
                    * math.sin(2 * math.pi * freq * i / rate)
                    * (1 - i / n)
                )
                for i in range(n)
            )
        )

        pygame.mixer.Sound(buffer=buf.tobytes()).play()

    def playSound(self, name, volume=1.0):
        if not self._init():
            return

        snd = self._cache.get(name)

        if snd is None:
            for ext in (".wav", ".ogg", ".mp3"):
                p = os.path.join(self.folder_sounds, name + ext)

                if os.path.isfile(p):
                    snd = pygame.mixer.Sound(p)
                    break

            if snd is None:
                print(f"[microstudio] son introuvable : {name!r}")
                return

            self._cache[name] = snd

        snd.set_volume(volume)
        snd.play()

    def playMusic(self, name, volume=1.0, loop=True):
        if not self._init():
            return

        for ext in (".ogg", ".mp3", ".wav"):
            p = os.path.join(self.folder_music, name + ext)

            if os.path.isfile(p):
                pygame.mixer.music.load(p)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1 if loop else 0)
                return

        print(f"[microstudio] musique introuvable : {name!r}")

    def stopMusic(self):
        if self._ok:
            pygame.mixer.music.stop()


audio = _Audio()


# ---------------------------------------------------------------------------
# System, random, Math
# ---------------------------------------------------------------------------

class _System:
    def __init__(self):
        self.fps = 60
        self.time = 0

    def _update(self, clock):
        self.time = pygame.time.get_ticks()
        self.fps = clock.get_fps()

    def exit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))


system = _System()


class _Random:
    def __init__(self):
        import random as _r
        self._r = _r.Random()

    def seed(self, s):
        self._r.seed(s)

    def next(self):
        return self._r.random()

    def nextInt(self, n):
        return self._r.randrange(int(n))


random = _Random()


class _Math:
    PI = math.pi

    sin = staticmethod(math.sin)
    cos = staticmethod(math.cos)
    tan = staticmethod(math.tan)
    atan2 = staticmethod(math.atan2)
    sqrt = staticmethod(math.sqrt)
    abs = staticmethod(abs)
    min = staticmethod(min)
    max = staticmethod(max)
    floor = staticmethod(math.floor)
    ceil = staticmethod(math.ceil)
    round = staticmethod(round)

    @staticmethod
    def clamp(v, lo, hi):
        return max(lo, min(hi, v))


Math = _Math()


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------

def run(
    init=None,
    update=None,
    draw=None,
    width=320,
    height=180,
    scale=3,
    title="microstudio.py",
    fps=60
):
    main = sys.modules.get("__main__")

    init = init or getattr(main, "init", None)
    update = update or getattr(main, "update", None)
    draw = draw or getattr(main, "draw", None)

    screen._setup(width, height, scale, title)
    clock = pygame.time.Clock()

    if init:
        init()

    running = True

    while running:
        keyboard._clear()
        mouse.wheel = 0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN:
                keyboard._pressed_now.add(e.key)
                keyboard.typed += e.unicode

            elif e.type == pygame.KEYUP:
                keyboard._released_now.add(e.key)

            elif e.type == pygame.MOUSEWHEEL:
                mouse.wheel += e.y

        mouse._update()
        system._update(clock)

        pygame.mouse.set_visible(mouse.visible)

        if update:
            update()

        if draw:
            draw()

        screen._present()
        clock.tick(fps)

    pygame.quit()