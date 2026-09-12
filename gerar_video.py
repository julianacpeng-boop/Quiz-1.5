# -*- coding: utf-8 -*-

import argparse
import asyncio
import os
import re
import shutil
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

from campanha import TEMA, HASHTAG, GANCHO, PERGUNTAS, FECHAMENTO


# =========================================================
# CONFIGURAÇÃO
# =========================================================
W, H = 1080, 1920
FPS = 30
AUDIO_HZ = 48000

# MESMA VOZ DOS OUTROS PROJETOS
VOZ = "pt-BR-AntonioNeural"
VELOCIDADE_VOZ = "+10%"

TEMPO_CONTAGEM = 3
PAUSA_POS_PERGUNTA = 0.25
PAUSA_POS_RESPOSTA = 0.60
TEMPO_FINAL_MINIMO = 3.0

OUTPUT = Path("output")
TEMP_ROOT = Path("_temp")

LETTERS = ["A", "B", "C", "D"]


# =========================================================
# 6 TEMAS VISUAIS
# =========================================================
THEMES = {
    1: {
        "nome": "INFORMATIVO",
        "bg": (247, 197, 68),
        "panel": (255, 255, 255),
        "text": (17, 55, 78),
        "muted": (102, 119, 130),
        "accent": (8, 126, 174),
        "accent2": (232, 103, 0),
        "option": (248, 251, 252),
        "correct": (225, 248, 235),
        "correct_border": (28, 150, 86),
    },
    2: {
        "nome": "CASAL FLERTANDO",
        "bg": (16, 61, 214),
        "panel": (255, 255, 255),
        "text": (32, 24, 36),
        "muted": (110, 100, 112),
        "accent": (255, 48, 38),
        "accent2": (10, 68, 255),
        "option": (255, 249, 250),
        "correct": (255, 234, 232),
        "correct_border": (255, 48, 38),
    },
    3: {
        "nome": "FESTIVAL",
        "bg": (8, 8, 20),
        "panel": (248, 248, 252),
        "text": (20, 18, 30),
        "muted": (106, 103, 120),
        "accent": (255, 45, 155),
        "accent2": (91, 52, 255),
        "option": (250, 250, 255),
        "correct": (255, 236, 247),
        "correct_border": (255, 45, 155),
    },
    4: {
        "nome": "CINEMA",
        "bg": (17, 17, 22),
        "panel": (255, 255, 255),
        "text": (24, 21, 18),
        "muted": (112, 104, 98),
        "accent": (230, 45, 45),
        "accent2": (255, 181, 0),
        "option": (255, 253, 247),
        "correct": (255, 247, 213),
        "correct_border": (255, 181, 0),
    },
    5: {
        "nome": "COUNTRY",
        "bg": (132, 66, 31),
        "panel": (255, 248, 232),
        "text": (61, 36, 24),
        "muted": (132, 103, 82),
        "accent": (107, 51, 25),
        "accent2": (240, 185, 91),
        "option": (255, 255, 255),
        "correct": (255, 239, 205),
        "correct_border": (215, 131, 50),
    },
    6: {
        "nome": "MORANGO",
        "bg": (139, 66, 255),
        "panel": (255, 255, 255),
        "text": (67, 21, 45),
        "muted": (139, 96, 119),
        "accent": (233, 39, 88),
        "accent2": (139, 66, 255),
        "option": (255, 248, 251),
        "correct": (244, 237, 255),
        "correct_border": (139, 66, 255),
    },
}


# =========================================================
# FONTES
# =========================================================
def achar_fonte(*candidatos):
    for p in candidatos:
        if p and Path(p).exists():
            return p
    return None


FONT_BOLD = achar_fonte(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
)

FONT_REG = achar_fonte(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
)


def fonte(tamanho, bold=True):
    p = FONT_BOLD if bold else FONT_REG
    if p:
        return ImageFont.truetype(p, int(tamanho))
    return ImageFont.load_default()


F_LOGO = fonte(42, True)
F_BADGE = fonte(25, True)
F_TITLE = fonte(58, True)
F_SUB = fonte(28, True)
F_QUESTION = fonte(45, True)
F_OPTION = fonte(31, True)
F_LETTER = fonte(25, True)
F_SMALL = fonte(24, True)
F_TIMER = fonte(100, True)
F_ANSWER = fonte(36, True)
F_FINAL = fonte(48, True)


# =========================================================
# TEXTO / DESENHO
# =========================================================
def text_width(draw, text, font):
    b = draw.textbbox((0, 0), str(text), font=font)
    return b[2] - b[0]


def wrap_text(draw, text, font, max_width, max_lines=None):
    words = str(text).split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word
        if text_width(draw, test, font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while text_width(draw, lines[-1] + "...", font) > max_width and len(lines[-1]) > 2:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."

    return lines


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def centered(draw, text, y, font, fill):
    x = (W - text_width(draw, text, font)) // 2
    draw.text((x, y), text, font=font, fill=fill)


def mix(c1, c2, ratio):
    return tuple(int(c1[i] * (1 - ratio) + c2[i] * ratio) for i in range(3))


def decorative_background(theme, layout):
    img = Image.new("RGB", (W, H), theme["bg"])
    d = ImageDraw.Draw(img)

    # Cada número tem detalhes visuais próprios.
    if layout == 1:
        d.rectangle((0, 0, W, 250), fill=theme["bg"])
        d.polygon([(0, 0), (W, 0), (W, 170), (0, 260)], fill=(235, 106, 0))
        d.polygon([(0, 145), (W, 70), (W, 270), (0, 345)], fill=(7, 126, 174))
        for x in range(40, W, 160):
            d.ellipse((x, 1550, x + 60, 1610), outline=mix(theme["accent"], (255,255,255), .45), width=4)

    elif layout == 2:
        d.ellipse((-260, -220, 470, 510), fill=(32, 81, 232))
        d.ellipse((730, 80, 1320, 650), fill=(220, 47, 41))
        # "lábios" estilizados
        d.ellipse((390, 105, 690, 250), fill=(255, 60, 70))
        d.ellipse((405, 155, 675, 260), fill=theme["bg"])
        d.rectangle((0, 1600, W, H), fill=(204, 48, 54))

    elif layout == 3:
        d.ellipse((-250, -250, 480, 480), fill=(68, 21, 91))
        d.ellipse((700, 70, 1360, 720), fill=(27, 44, 89))
        horizon = 1450
        for y in range(horizon, H, 80):
            d.line((0, y, W, y), fill=(55, 40, 96), width=2)
        for x in range(-400, 1500, 90):
            d.line((W//2, horizon, x, H), fill=(45, 53, 110), width=2)

    elif layout == 4:
        d.rectangle((0, 0, W, 360), fill=(255, 202, 67))
        d.rectangle((0, 1540, W, H), fill=(34, 30, 30))
        for x in range(30, W, 90):
            d.ellipse((x, 1640, x + 55, 1710), fill=(248, 228, 184))
            d.polygon([(x+10,1645),(x+25,1615),(x+40,1648)], fill=(248,228,184))

    elif layout == 5:
        d.rectangle((0, 0, W, H), fill=(131, 67, 31))
        d.ellipse((-200, -140, 520, 580), fill=(163, 87, 39))
        d.ellipse((720, 100, 1320, 680), fill=(107, 51, 25))
        d.rectangle((0, 1580, W, H), fill=(93, 48, 26))
        for y in range(1600, H, 70):
            d.line((0, y, W, y), fill=(137, 80, 48), width=3)

    elif layout == 6:
        d.ellipse((-200, -230, 520, 520), fill=(184, 65, 218))
        d.ellipse((720, 60, 1320, 680), fill=(235, 46, 105))
        # sementes estilizadas
        for x, y in [(90,150),(180,300),(890,180),(960,360),(120,1500),(910,1500)]:
            d.ellipse((x, y, x+18, y+34), fill=(255, 228, 136))

    # scanlines leves em todos
    for y in range(0, H, 10):
        d.line((0, y, W, y), fill=mix(theme["bg"], (0,0,0), .08), width=1)

    return img


def draw_header(img, theme, layout, step=None):
    d = ImageDraw.Draw(img)

    d.text((55, 45), "JUH", font=F_LOGO, fill=(255,255,255))
    x = 55 + text_width(d, "JUH ", F_LOGO)
    d.text((x, 45), "QUIZ", font=F_LOGO, fill=theme["accent2"] if layout != 1 else (255,255,255))

    badge = HASHTAG
    bw = text_width(d, badge, F_BADGE)
    rounded(
        d,
        (W - bw - 105, 43, W - 45, 102),
        28,
        theme["accent"],
    )
    d.text((W - bw - 75, 59), badge, font=F_BADGE, fill=(255,255,255))

    if step:
        d.text((55, 115), step.upper(), font=F_SMALL, fill=(245,245,245))


def render_intro(theme, layout):
    img = decorative_background(theme, layout)
    d = ImageDraw.Draw(img)
    draw_header(img, theme, layout, theme["nome"])

    rounded(
        d,
        (55, 250, W - 55, 1500),
        42,
        theme["panel"],
    )

    centered(d, theme["nome"], 320, F_BADGE, theme["accent"])

    y = 400
    for line in wrap_text(d, TEMA.upper(), F_TITLE, 860, 3):
        centered(d, line, y, F_TITLE, theme["text"])
        y += 72

    d.rectangle((190, y + 20, W - 190, y + 27), fill=theme["accent"])

    y += 85
    for line in wrap_text(d, GANCHO, F_QUESTION, 820, 4):
        centered(d, line, y, F_QUESTION, theme["text"])
        y += 58

    # seis pequenos indicadores de layout
    y += 95
    start_x = 168
    for i in range(1, 7):
        fill = theme["accent"] if i == layout else mix(theme["muted"], theme["panel"], .55)
        rounded(d, (start_x + (i-1)*125, y, start_x + 80 + (i-1)*125, y + 80), 20, fill)
        num = str(i)
        nx = start_x + 40 + (i-1)*125 - text_width(d, num, F_BADGE)//2
        d.text((nx, y + 23), num, font=F_BADGE, fill=(255,255,255))

    centered(d, "5 PERGUNTAS • 3 SEGUNDOS • RESPOSTA", 1340, F_SMALL, theme["muted"])
    return img


def render_question(theme, layout, q_index, fase="pergunta", contador=None):
    item = PERGUNTAS[q_index]
    img = decorative_background(theme, layout)
    d = ImageDraw.Draw(img)

    draw_header(
        img,
        theme,
        layout,
        f"Pergunta {q_index + 1} de {len(PERGUNTAS)}",
    )

    # progresso
    px = 55
    total = W - 110
    gap = 12
    seg = (total - gap * 4) / 5
    for i in range(5):
        fill = theme["accent"] if i <= q_index else mix(theme["muted"], theme["panel"], .55)
        rounded(
            d,
            (px + i*(seg+gap), 175, px + i*(seg+gap) + seg, 188),
            7,
            fill,
        )

    rounded(
        d,
        (55, 230, W - 55, 1660),
        42,
        theme["panel"],
    )

    # título visual diferente por layout
    top_label = {
        1: "VOCE SABE ISSO?",
        2: "QUAL VOCE ESCOLHE?",
        3: "SO QUEM TA POR DENTRO ACERTA",
        4: "CINEMA QUIZ",
        5: "ESCOLHA O ESTILO",
        6: "VALE A FAMA?",
    }[layout]

    d.text((100, 285), top_label, font=F_BADGE, fill=theme["accent"])

    qy = 355
    for line in wrap_text(d, item["pergunta"], F_QUESTION, 820, 4):
        d.text((100, qy), line, font=F_QUESTION, fill=theme["text"])
        qy += 58

    opt_y = max(650, qy + 60)
    correta = int(item["correta"])

    for i, op in enumerate(item["opcoes"]):
        y1 = opt_y + i * 175
        y2 = y1 + 130

        revelar = fase == "resposta" and i == correta
        fill = theme["correct"] if revelar else theme["option"]
        outline = theme["correct_border"] if revelar else mix(theme["muted"], theme["panel"], .20)
        w = 5 if revelar else 2

        rounded(
            d,
            (95, y1, W - 95, y2),
            28,
            fill,
            outline=outline,
            width=w,
        )

        bubble = theme["correct_border"] if revelar else theme["accent"]
        rounded(d, (120, y1 + 33, 186, y1 + 99), 18, bubble)

        letter = LETTERS[i]
        lx = 153 - text_width(d, letter, F_LETTER)//2
        d.text((lx, y1 + 50), letter, font=F_LETTER, fill=(255,255,255))

        lines = wrap_text(d, op, F_OPTION, 700, 2)
        ty = y1 + (30 if len(lines) == 2 else 48)
        for line in lines:
            d.text((220, ty), line, font=F_OPTION, fill=theme["text"])
            ty += 42

    if fase == "contagem":
        rounded(
            d,
            (W - 270, 1260, W - 105, 1425),
            82,
            theme["panel"],
            outline=theme["accent"],
            width=7,
        )
        n = str(contador)
        nx = W - 187 - text_width(d, n, F_TIMER)//2
        d.text((nx, 1278), n, font=F_TIMER, fill=theme["accent"])

    if fase == "resposta":
        resposta = item["opcoes"][correta]
        rounded(
            d,
            (95, 1465, W - 95, 1585),
            30,
            theme["correct"],
            outline=theme["correct_border"],
            width=4,
        )
        label = "RESPOSTA: " + resposta
        lines = wrap_text(d, label, F_ANSWER, 790, 2)
        ty = 1492
        for line in lines:
            centered(d, line, ty, F_ANSWER, theme["correct_border"])
            ty += 46

    centered(d, "A contagem comeca depois da leitura da pergunta.", 1760, F_SMALL, (245,245,245))
    return img


def render_explanation(theme, layout, q_index):
    item = PERGUNTAS[q_index]
    img = decorative_background(theme, layout)
    d = ImageDraw.Draw(img)

    draw_header(img, theme, layout, "Explicacao rapida")

    rounded(
        d,
        (70, 300, W - 70, 1510),
        46,
        theme["panel"],
    )

    centered(d, "POR QUE?", 370, F_TITLE, theme["accent"])

    resposta = item["opcoes"][item["correta"]]
    rounded(
        d,
        (130, 510, W - 130, 650),
        30,
        theme["correct"],
        outline=theme["correct_border"],
        width=4,
    )

    for j, line in enumerate(wrap_text(d, resposta, F_ANSWER, 700, 2)):
        centered(d, line, 545 + j*48, F_ANSWER, theme["correct_border"])

    y = 760
    for line in wrap_text(d, item["explicacao"], F_QUESTION, 780, 7):
        centered(d, line, y, F_QUESTION, theme["text"])
        y += 60

    return img


def render_final(theme, layout):
    img = decorative_background(theme, layout)
    d = ImageDraw.Draw(img)
    draw_header(img, theme, layout, "Resultado")

    rounded(
        d,
        (70, 300, W - 70, 1510),
        46,
        theme["panel"],
    )

    centered(d, "FIM DO QUIZ", 390, F_TITLE, theme["accent"])
    centered(d, TEMA.upper(), 510, F_FINAL, theme["text"])

    y = 660
    for line in wrap_text(d, FECHAMENTO, F_QUESTION, 800, 6):
        centered(d, line, y, F_QUESTION, theme["text"])
        y += 62

    rounded(
        d,
        (170, 1120, W - 170, 1225),
        34,
        theme["accent"],
    )
    centered(d, HASHTAG, 1150, F_BADGE, (255,255,255))

    centered(d, "JUH QUIZ", 1355, F_LOGO, theme["muted"])
    return img


# =========================================================
# TTS / FFmpeg
# =========================================================
def limpar_tts(texto):
    texto = str(texto)
    texto = re.sub(r"#", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


async def tts_mp3(texto, caminho):
    texto = limpar_tts(texto)
    comunicador = edge_tts.Communicate(
        texto,
        VOZ,
        rate=VELOCIDADE_VOZ,
    )
    await comunicador.save(str(caminho))


def run(cmd):
    print("$", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def duracao(path):
    p = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(p.stdout.strip())


def mp3_para_wav(mp3, wav, target):
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(mp3),
        "-af", f"apad=pad_dur={target:.3f}",
        "-t", f"{target:.3f}",
        "-ar", str(AUDIO_HZ),
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(wav),
    ])


def silencio_wav(path, tempo):
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "lavfi",
        "-i", f"anullsrc=r={AUDIO_HZ}:cl=mono",
        "-t", f"{tempo:.3f}",
        "-c:a", "pcm_s16le",
        str(path),
    ])


def beep_wav(path, tempo=1.0):
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "lavfi",
        "-i", f"sine=frequency=960:sample_rate={AUDIO_HZ}:duration=0.14",
        "-af", f"apad=pad_dur={tempo:.3f}",
        "-t", f"{tempo:.3f}",
        "-ar", str(AUDIO_HZ),
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(path),
    ])


async def segmento_tts(texto, imagem, temp, nome, pausa=0.25, minimo=0):
    mp3 = temp / f"{nome}.mp3"
    wav = temp / f"{nome}.wav"

    await tts_mp3(texto, mp3)
    total = max(minimo, duracao(mp3) + pausa)
    mp3_para_wav(mp3, wav, total)

    return {
        "image": imagem,
        "audio": wav,
        "duration": total,
    }


def segmento_silencio(imagem, temp, nome, tempo, beep=False):
    wav = temp / f"{nome}.wav"
    if beep:
        beep_wav(wav, tempo)
    else:
        silencio_wav(wav, tempo)

    return {
        "image": imagem,
        "audio": wav,
        "duration": tempo,
    }


def concatenar_audio(segmentos, temp):
    lista = temp / "audio.txt"

    with lista.open("w", encoding="utf-8") as f:
        for s in segmentos:
            f.write(f"file '{s['audio'].resolve().as_posix()}'\n")

    out = temp / "audio_final.wav"

    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat",
        "-safe", "0",
        "-i", str(lista),
        "-ar", str(AUDIO_HZ),
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(out),
    ])

    return out


def montar_video(segmentos, audio, saida, temp):
    lista = temp / "frames.txt"

    with lista.open("w", encoding="utf-8") as f:
        for s in segmentos:
            f.write(f"file '{s['image'].resolve().as_posix()}'\n")
            f.write(f"duration {s['duration']:.4f}\n")
        f.write(f"file '{segmentos[-1]['image'].resolve().as_posix()}'\n")

    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat",
        "-safe", "0",
        "-i", str(lista),
        "-i", str(audio),
        "-r", str(FPS),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(saida),
    ])


# =========================================================
# VALIDAÇÃO
# =========================================================
def validar():
    if len(PERGUNTAS) != 5:
        raise ValueError("Use exatamente 5 perguntas em campanha.py.")

    for i, q in enumerate(PERGUNTAS, start=1):
        if len(q.get("opcoes", [])) != 4:
            raise ValueError(f"Pergunta {i}: use exatamente 4 opcoes.")
        if q.get("correta") not in (0, 1, 2, 3):
            raise ValueError(f"Pergunta {i}: 'correta' deve ser 0, 1, 2 ou 3.")
        if not q.get("pergunta"):
            raise ValueError(f"Pergunta {i}: texto vazio.")
        if not q.get("explicacao"):
            raise ValueError(f"Pergunta {i}: explicacao vazia.")


def escolher_layout():
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", type=int, choices=range(1, 7))
    args = parser.parse_args()

    valor = args.layout or int(os.environ.get("LAYOUT", "1"))

    if valor not in THEMES:
        raise ValueError("LAYOUT deve ser um numero de 1 a 6.")

    return valor


# =========================================================
# GERAÇÃO
# =========================================================
async def main():
    validar()
    layout = escolher_layout()
    theme = THEMES[layout]

    OUTPUT.mkdir(parents=True, exist_ok=True)

    temp = TEMP_ROOT / f"layout_{layout}"
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True, exist_ok=True)

    segmentos = []

    # INTRO
    intro = temp / "intro.png"
    render_intro(theme, layout).save(intro)

    segmentos.append(
        await segmento_tts(
            GANCHO,
            intro,
            temp,
            "intro",
            pausa=0.6,
            minimo=3.0,
        )
    )

    # PERGUNTAS
    for qi, q in enumerate(PERGUNTAS):
        pergunta_img = temp / f"q{qi+1}_pergunta.png"
        render_question(theme, layout, qi, "pergunta").save(pergunta_img)

        # LÊ SOMENTE A PERGUNTA
        segmentos.append(
            await segmento_tts(
                q["pergunta"],
                pergunta_img,
                temp,
                f"q{qi+1}_pergunta_audio",
                pausa=PAUSA_POS_PERGUNTA,
            )
        )

        # CONTAGEM 3,2,1 + BIP
        for numero in range(TEMPO_CONTAGEM, 0, -1):
            contagem_img = temp / f"q{qi+1}_contagem_{numero}.png"
            render_question(
                theme,
                layout,
                qi,
                "contagem",
                numero,
            ).save(contagem_img)

            segmentos.append(
                segmento_silencio(
                    contagem_img,
                    temp,
                    f"q{qi+1}_bip_{numero}",
                    1.0,
                    beep=True,
                )
            )

        # RESPOSTA
        resposta_img = temp / f"q{qi+1}_resposta.png"
        render_question(theme, layout, qi, "resposta").save(resposta_img)

        resposta_correta = q["opcoes"][q["correta"]]

        # LÊ SOMENTE A RESPOSTA CORRETA
        segmentos.append(
            await segmento_tts(
                resposta_correta,
                resposta_img,
                temp,
                f"q{qi+1}_resposta_audio",
                pausa=PAUSA_POS_RESPOSTA,
                minimo=1.6,
            )
        )

        # EXPLICAÇÃO VISUAL CURTA, SEM NARRAÇÃO
        exp_img = temp / f"q{qi+1}_explicacao.png"
        render_explanation(theme, layout, qi).save(exp_img)

        segmentos.append(
            segmento_silencio(
                exp_img,
                temp,
                f"q{qi+1}_explicacao_audio",
                1.25,
                beep=False,
            )
        )

    # FINAL
    final_img = temp / "final.png"
    render_final(theme, layout).save(final_img)

    segmentos.append(
        await segmento_tts(
            FECHAMENTO,
            final_img,
            temp,
            "final_audio",
            pausa=0.7,
            minimo=TEMPO_FINAL_MINIMO,
        )
    )

    audio = concatenar_audio(segmentos, temp)

    nome = re.sub(r"[^A-Za-z0-9_-]+", "_", TEMA).strip("_")
    saida = OUTPUT / f"JUH_QUIZ_{nome}_LAYOUT_{layout}.mp4"

    montar_video(
        segmentos,
        audio,
        saida,
        temp,
    )

    print()
    print("========================================")
    print("VIDEO GERADO COM SUCESSO")
    print("Layout:", layout, "-", theme["nome"])
    print("Voz:", VOZ)
    print("Arquivo:", saida)
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
