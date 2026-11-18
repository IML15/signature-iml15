"""
Firma de IML15 para la terminal: agujero negro ASCII animado.
Uso:  from firma_iml15 import mostrar_firma ;  mostrar_firma()
"""
import math
import os
import random
import sys
import time

ANCHO, ALTO = 64, 17
FOTOGRAMAS = 55
PAUSA = 0.06

AMARILLO = (255, 214, 40)
BLANCO = (255, 250, 225)
AMBAR = (205, 120, 30)
OSCURO = (120, 70, 20)
TURQUESA = (60, 200, 160)
TURQ_OSC = (30, 110, 95)
GRIS = (150, 150, 170)

# ── Esfera (sombra del agujero) ────────────────────────────────
# Se dibuja la mitad izquierda y se refleja para que sea simétrica.
#  ','  -> anillo de luz que gira por dentro del borde (animado)
_MITAD = [
    "          _.--~~",
    "       .-'~,,,,,",
    "     .',,,'     ",
    "    /,,'        ",
    "   /,'          ",
    "  |,,           ",
    "  |,,           ",
    "  |,,           ",
    "   \\,.          ",
    "    \\,,.        ",
    "     '.,,,.     ",
    "       '-._~,,,,",
    "          '~~--~",
]
_ESPEJO = str.maketrans("/\\()<>", "\\/)(><")
ESFERA = [m + m[::-1].translate(_ESPEJO) for m in _MITAD]

# ── Alias en letras grandes y rectas (más legibles) ────────────
GLIFOS = {
    "I": [" _____ ", "|_   _|", "  | |  ", "  | |  ", " _| |_ ", "|_____|"],
    "M": [" __  __ ", "|  \\/  |", "| \\  / |", "| |\\/| |", "| |  | |", "|_|  |_|"],
    "L": [" _      ", "| |     ", "| |     ", "| |     ", "| |____ ", "|______|"],
    "1": [" __ ", "/_ |", " | |", " | |", " | |", " |_|"],
    "5": [" _____ ", "| ____|", "| |__  ", "|___ \\ ", " ___) |", "|____/ "],
}
# Versión en cursiva: cada fila se desplaza y los '|' pasan a '/'.
# La M se dibuja a mano porque su "V" central no queda bien al inclinarla.
M_CURSIVA = ["      __  __ ", "     /  |/  /", "    / /|_/ / ",
             "   / /  / /  ", "  / /  / /   ", " /_/  /_/    "]


def _cursiva(letra):
    if letra == "M":
        return M_CURSIVA
    g = GLIFOS[letra]
    n = len(g)
    return [" " * (n - 1 - i) + f.replace("|", "/") + " " * i for i, f in enumerate(g)]


def _componer(palabra):
    """Coloca las letras inclinadas una junto a otra, solapando sus márgenes."""
    lienzo = [[" "] * 80 for _ in range(6)]
    x = 0
    for c in palabra:
        g = _cursiva(c)
        for y, fila in enumerate(g):
            for i, ch in enumerate(fila):
                if ch != " ":
                    lienzo[y][x + i] = ch
        x += len(GLIFOS[c][0]) + (4 if c == "M" else 2)
    return ["".join(f).rstrip() for f in lienzo]


LOGO = _componer("IML15")
_ANCHO = max(len(f) for f in LOGO)
LOGO = [f.ljust(_ANCHO) for f in LOGO]
ANCHO_LOGO = len(LOGO[0])


def _c(ch, rgb, negrita=True):
    return f"\033[{'1;' if negrita else ''}38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{ch}\033[0m"


def _mezcla(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ── Nubes de estrellas turquesa ────────────────────────────────
random.seed(15)
ESTRELLAS = {}
for (nx, ny, rad, dens) in [(5, 1, 8, 0.55), (59, 2, 7, 0.45), (5, 14, 7, 0.5), (59, 14, 6, 0.6)]:
    for y in range(ALTO):
        for x in range(ANCHO):
            d = math.hypot((x - nx) / 2, y - ny) / (rad / 2)
            if d < 1 and random.random() < dens * (1 - d):
                ESTRELLAS[(x, y)] = (random.choice("+*.:x"), random.random())
for _ in range(10):
    ESTRELLAS[(random.randrange(ANCHO), random.randrange(ALTO))] = (".", random.random())


def _escena(t, aparicion):
    cx, cy = ANCHO / 2, ALTO // 2
    a = math.radians(9)
    ca, sa = math.cos(a), math.sin(a)
    A, B = 11.0 * aparicion, 2.7 * aparicion
    filas, delante = [], []
    for y in range(ALTO):
        fila, fila_d = [], []
        for x in range(ANCHO):
            X, Y = (x - cx) / 2.0, (y - cy)
            u = X * ca - Y * sa * 2.0
            v = X * sa * 0.5 + Y * ca
            celda, es_delante = None, False
            e = 99.0

            if aparicion > 0.05:
                e = math.hypot(u / A, v / B)
                ang = math.atan2(v / B, u / A)
                grosor = 0.42 + 0.3 * abs(math.sin(ang))
                if 1.0 <= e < 1.0 + grosor:
                    es_delante = v > 0
                    if e < 1.1 or e > 1.0 + grosor - 0.13:
                        celda = ("#", AMARILLO)
                    elif math.sin(ang * 9 - t * 3.0) > 0.93:
                        celda = ("o", (40, 25, 10))
                    elif math.sin(ang * 20 + e * 15) > 0:
                        celda = ("%", AMBAR)
                    else:
                        celda = (":", OSCURO)

            if celda is None and (x, y) in ESTRELLAS and e > 1.8:
                ch, f = ESTRELLAS[(x, y)]
                if math.sin(t * 4 + f * 40) > 0.75:
                    celda = ("*", (180, 255, 230))
                else:
                    celda = (ch, TURQUESA if f > 0.4 else TURQ_OSC)
            fila.append(celda)
            fila_d.append(es_delante)
        filas.append(fila)
        delante.append(fila_d)

    # Esfera completa: tapa la parte de atrás del disco; la de delante pasa por encima
    if aparicion >= 1:
        pulso = 0.5 + 0.5 * math.sin(t * 4)
        alto, ancho = len(ESFERA), len(ESFERA[0])
        y0, x0 = int(cy) - alto // 2, int(cx - ancho / 2)
        ccx, ccy = (ancho - 1) / 2, (alto - 1) / 2
        for dy, linea in enumerate(ESFERA):
            yy = y0 + dy
            nucleo = linea.strip()
            ini, fin = linea.index(nucleo[0]), linea.rindex(nucleo[-1])
            for i, ch in enumerate(linea):
                xx = x0 + i
                if not (0 <= yy < ALTO and 0 <= xx < ANCHO) or delante[yy][xx]:
                    continue
                ang = math.atan2((dy - ccy) * 2, i - ccx)
                if ch == ",":                     # anillo de luz que gira
                    s = math.sin(ang * 5 - t * 5)
                    if s > 0.55:
                        filas[yy][xx] = ("*", BLANCO)
                    elif s > -0.1:
                        filas[yy][xx] = (":", _mezcla(AMARILLO, BLANCO, (s + 0.1) / 0.65))
                    else:
                        filas[yy][xx] = (".", AMBAR)
                elif ch != " ":                   # contorno con reflejo que recorre
                    brillo = 0.5 + 0.5 * math.sin(ang * 2 - t * 3)
                    filas[yy][xx] = (ch, _mezcla(AMARILLO, BLANCO, brillo * pulso + 0.2))
                elif ini < i < fin:               # interior: degradado hacia dentro
                    nx = (i - ccx) / (ancho / 2 - 3)
                    ny = (dy - ccy) / (alto / 2 - 0.5)
                    d = math.hypot(nx, ny)               # 0 centro, ~1 borde
                    giro = 0.08 * math.sin(ang * 3 + d * 6 - t * 2.5)
                    de = d + giro                        # para el degradado del borde
                    # núcleo: masa brillante que respira y se difumina hacia fuera
                    nucleo_r = 0.62 + 0.04 * math.sin(t * 3)
                    dc = d / nucleo_r + 0.12 * math.sin(ang * 4 - t * 4) * d
                    if dc < 0.30:
                        filas[yy][xx] = ("@", BLANCO)
                    elif dc < 0.50:
                        filas[yy][xx] = ("#", (255, 235, 140))
                    elif dc < 0.68:
                        filas[yy][xx] = ("%", AMARILLO)
                    elif dc < 0.82:
                        filas[yy][xx] = ("*", (245, 150, 30))
                    elif dc < 0.95:
                        filas[yy][xx] = (":", (190, 90, 20))
                    elif dc < 1.08:
                        filas[yy][xx] = (".", (120, 50, 15))
                    # degradado del borde hacia dentro
                    elif de > 0.9:
                        filas[yy][xx] = (":", (190, 95, 25))
                    elif de > 0.83:
                        filas[yy][xx] = ("-", (140, 60, 20))
                    elif de > 0.77:
                        filas[yy][xx] = (".", (95, 40, 15))
                    elif de > 0.72:
                        filas[yy][xx] = ("'", (60, 25, 12))
                    else:
                        filas[yy][xx] = None          # franja negra entre núcleo y borde
    return filas


NARANJA = (255, 120, 20)
CURSOR = (255, 255, 255)


def _logo(t):
    """Celdas del alias: degradado vertical blanco -> amarillo -> naranja + destello."""
    filas = []
    for y, fila in enumerate(LOGO):
        k = y / (len(LOGO) - 1)
        base = _mezcla(BLANCO, AMARILLO, k * 2) if k < 0.5 else _mezcla(AMARILLO, NARANJA, (k - 0.5) * 2)
        celdas = []
        for x, ch in enumerate(fila):
            if ch == " ":
                celdas.append(None)
            else:
                d = abs((x + y) - ((t * 28) % (ANCHO_LOGO + 40) - 20))
                celdas.append((ch, _mezcla(base, (255, 255, 255), 1 - d / 4)))
        filas.append(celdas)
    return filas


def _rejilla(t, version):
    """Todo el fotograma como una rejilla de celdas (carácter, color) o None."""
    izquierda = _escena(t, 1.0)
    derecha = [[] for _ in range(ALTO)]
    inicio = 3
    for i, celdas in enumerate(_logo(t)):
        derecha[inicio + i] = celdas
    textos = [("~ code from the event horizon ~", (235, 150, 30)),
              (f"github.com/IML15  ·  {version}", GRIS)]
    for j, (txt, col) in enumerate(textos):
        derecha[inicio + len(LOGO) + 1 + j] = [None] + [(ch, col) if ch != " " else None for ch in txt]
    return [[None] + izq + [None, None] + der for izq, der in zip(izquierda, derecha)]


def _pintar(rejilla, escritos=None):
    """Convierte la rejilla en texto. Si 'escritos' tiene valor, solo muestra
    los primeros caracteres (en orden de lectura) y un cursor detrás."""
    lineas, cuenta = [], 0
    for fila in rejilla:
        linea, cursor_puesto = "", False
        for celda in fila:
            if celda is None:
                linea += " "
                continue
            cuenta += 1
            if escritos is None or cuenta <= escritos:
                linea += _c(*celda)
            elif cuenta == escritos + 1 and not cursor_puesto:
                linea += _c("_", CURSOR)
                cursor_puesto = True
            else:
                linea += " "
        lineas.append(linea)
    return lineas


def _escribir_lineal(rejilla, duracion=2.0):
    """Efecto máquina de escribir sin mover el cursor: funciona en cualquier consola."""
    total = sum(c is not None for fila in rejilla for c in fila)
    pausa = duracion / max(total, 1)
    for fila in rejilla:
        ultimo = max((i for i, c in enumerate(fila) if c is not None), default=-1)
        for celda in fila[:ultimo + 1]:
            if celda is None:
                sys.stdout.write(" ")
            else:
                sys.stdout.write(_c(*celda))
                sys.stdout.flush()
                time.sleep(pausa)
        sys.stdout.write("\n")
        sys.stdout.flush()


def mostrar_firma(version="v1.0", animar=True):
    if os.name == "nt":
        os.system("")  # activa colores ANSI en Windows

    if not animar:
        print("\n".join(_pintar(_rejilla(0.3, version))))
        return

    if not sys.stdout.isatty():
        # Consolas que no son terminal real (p. ej. "Run" de PyCharm):
        # no se puede redibujar, pero sí escribir carácter a carácter.
        _escribir_lineal(_rejilla(0.3, version))
        return

    total = sum(c is not None for fila in _rejilla(0, version) for c in fila)
    pasos_escritura = 60                                   # ~1,8 s escribiendo
    por_paso = math.ceil(total / pasos_escritura)
    try:
        sys.stdout.write("\033[?25l")                      # ocultar cursor real
        f = 0
        # 1) se va escribiendo, línea a línea, con un cursor delante
        for paso in range(pasos_escritura + 1):
            t = f * 0.1
            if f:
                sys.stdout.write(f"\033[{ALTO}F")
            sys.stdout.write("\n".join(_pintar(_rejilla(t, version), paso * por_paso)) + "\n")
            sys.stdout.flush()
            time.sleep(0.03)
            f += 1
        # 2) ya escrito, sigue animándose un momento
        for _ in range(FOTOGRAMAS - 15):
            t = f * 0.1
            sys.stdout.write(f"\033[{ALTO}F")
            sys.stdout.write("\n".join(_pintar(_rejilla(t, version))) + "\n")
            sys.stdout.flush()
            time.sleep(PAUSA)
            f += 1
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


if __name__ == "__main__":
    mostrar_firma()
