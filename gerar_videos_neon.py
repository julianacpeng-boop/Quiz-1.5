import os
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# ============================================================
# JUH QUIZ NEON FLEXÍVEL — mesmo esquema de edição do Quiz-vers-o-1.3
#
# MODO_LAYOUT:
#   1 = SEM imagem do tema
#   2 = COM imagem automática na tela inicial do tema
#
# No modo 2 a imagem do tema é inserida automaticamente na abertura.
# Nas perguntas, a imagem não aparece para deixar mais espaço.
#
# Fluxo:
#   1) fala: QUANTO VOCÊ SABE SOBRE: TEMA?
#   2) lê SOMENTE a pergunta
#   3) contagem 3, 2, 1
#   4) destaca a resposta correta
#   5) lê SOMENTE a resposta correta
# ============================================================

# ============================================================
# EDITE SOMENTE ESTA ÁREA, COMO VOCÊ JÁ FAZ NA VERSÃO 1.3
#
# Você pode colocar:
# - quantos TEMAS quiser;
# - quantas PERGUNTAS quiser dentro de cada tema.
#
# Cada pergunta continua com 3 alternativas:
# correta: 0=A, 1=B, 2=C
#
# O programa calcula sozinho:
# - quantidade de vídeos = quantidade de temas;
# - quantidade de perguntas de cada vídeo;
# - 1/3, 1/5, 1/7...
# - "PERGUNTA 1 DE X";
# - placar final X/X.
# ============================================================

QUIZZES = {

    "Drácula": [
        {
            "pergunta": "Drácula é mais conhecido por ser qual tipo de criatura?",
            "alternativas": [
                "Lobisomem",
                "Vampiro",
                "Fantasma"
            ],
            "correta": 1
        },
        {
            "pergunta": "Quem escreveu o romance clássico Drácula?",
            "alternativas": [
                "Bram Stoker",
                "Edgar Allan Poe",
                "Mary Shelley"
            ],
            "correta": 0
        },
        {
            "pergunta": "Em muitas histórias, Drácula costuma dormir durante o dia em:",
            "alternativas": [
                "Uma torre encantada",
                "Um quarto de hotel",
                "Um caixão"
            ],
            "correta": 2
        },
    ],

    "Frankenstein": [
        {
            "pergunta": "Quem escreveu o romance clássico Frankenstein?",
            "alternativas": [
                "Mary Shelley",
                "Bram Stoker",
                "Robert Louis Stevenson"
            ],
            "correta": 0
        },
        {
            "pergunta": "Na história, Victor Frankenstein é principalmente:",
            "alternativas": [
                "Um caçador de vampiros",
                "Um jovem estudioso da ciência",
                "Um rei amaldiçoado"
            ],
            "correta": 1
        },
        {
            "pergunta": "O grande objetivo de Victor Frankenstein em seus experimentos era:",
            "alternativas": [
                "Encontrar um tesouro perdido",
                "Criar uma máquina do tempo",
                "Dar vida à matéria sem vida"
            ],
            "correta": 2
        },
    ],

    "O Médico e o Monstro": [
        {
            "pergunta": "Qual é o nome do médico protagonista de O Médico e o Monstro?",
            "alternativas": [
                "Dr. Jekyll",
                "Dr. Moreau",
                "Dr. Watson"
            ],
            "correta": 0
        },
        {
            "pergunta": "Qual é o nome da personalidade sombria de Dr. Jekyll?",
            "alternativas": [
                "Mr. Black",
                "Mr. Hyde",
                "Mr. Crow"
            ],
            "correta": 1
        },
        {
            "pergunta": "Qual tema é central na história de O Médico e o Monstro?",
            "alternativas": [
                "Viagens espaciais",
                "Caça a tesouros",
                "O conflito entre lados diferentes da personalidade humana"
            ],
            "correta": 2
        },
    ],

}


# ============================================================
# IMAGENS DOS TEMAS
# ============================================================
# As imagens aparecem automaticamente na abertura no MODO 2.
# Os arquivos devem estar dentro da pasta "imagens_temas".

TEMA_IMAGENS = {
    "Drácula": "imagens_temas/dracula.png",
    "Frankenstein": "imagens_temas/frankenstein.png",
    "O Médico e o Monstro": "imagens_temas/medico_monstro.png",
}


# ------------------------------------------------------------
# CONFIGURAÇÃO
# ------------------------------------------------------------
# ------------------------------------------------------------
# CONFIGURAÇÃO
# ------------------------------------------------------------

TEMPO_ESCOLHA = 3

# MESMA VOZ DO Quiz-vers-o-1.3
VOZ = "pt-BR-AntonioNeural"
VELOCIDADE_VOZ = "+10%"

W = 1080
H = 1920
FPS = 30

AUDIO_HZ = 48000
AUDIO_CHANNELS = 2

PAUSA_DEPOIS_TEMA = 0.35
PAUSA_DEPOIS_PERGUNTA = 0.15
PAUSA_DEPOIS_RESPOSTA = 0.55

FUSO = ZoneInfo("America/Fortaleza")
DATA_DO_DIA = datetime.now(FUSO).strftime("%Y-%m-%d")

# Pode ser definido no GitHub Actions.
MODO_LAYOUT = int(os.getenv("MODO_LAYOUT", "2").strip())
if MODO_LAYOUT not in (1, 2):
    raise ValueError("MODO_LAYOUT deve ser 1 (sem imagem) ou 2 (com imagem).")


PASTA_RAIZ = Path("output_neon")
PASTA_TMP = Path("_tmp_juhquiz_neon")
NOME_MODO = "modo_1_sem_imagem" if MODO_LAYOUT == 1 else "modo_2_com_imagem"
PASTA_SAIDA = PASTA_RAIZ / DATA_DO_DIA / NOME_MODO

# ------------------------------------------------------------
# PALETA
# ------------------------------------------------------------

NAVY = (5, 20, 77)
NAVY_2 = (2, 8, 34)
BLUE = (19, 119, 255)
CYAN = (24, 231, 255)
WHITE = (247, 249, 255)
YELLOW = (255, 197, 27)
ORANGE = (255, 155, 0)
PINK = (245, 27, 203)
PURPLE = (122, 44, 255)
GREEN = (24, 215, 123)
GREEN_DARK = (7, 92, 53)
GRAY = (88, 112, 170)
LIGHT_BLUE = (237, 243, 255)

# ============================================================
# UTILIDADES
# ============================================================

def slug(texto):
    txt = unicodedata.normalize("NFKD", str(texto))
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = re.sub(r"[^a-zA-Z0-9]+", "-", txt).strip("-").lower()
    return txt or "quiz"


def executar(cmd):
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr)
        raise RuntimeError("Falha ao executar comando.")
    return p


def fonte(tamanho, bold=False):
    candidatos = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",

        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]

    for arq in candidatos:
        try:
            return ImageFont.truetype(arq, tamanho)
        except Exception:
            pass

    return ImageFont.load_default()


def gradient_vertical(size, top_color, bottom_color):
    w, h = size
    faixa = Image.new("RGB", (1, h))
    dados = []

    for y in range(h):
        t = y / max(1, h - 1)
        dados.append(tuple(
            int(top_color[i] * (1 - t) + bottom_color[i] * t)
            for i in range(3)
        ))

    faixa.putdata(dados)
    return faixa.resize((w, h))


def wrap_text(draw, texto, fnt, max_width):
    palavras = str(texto).split()
    linhas = []
    atual = ""

    for palavra in palavras:
        teste = (atual + " " + palavra).strip()
        bb = draw.textbbox((0, 0), teste, font=fnt)
        if bb[2] - bb[0] <= max_width:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra

    if atual:
        linhas.append(atual)

    return linhas


def draw_centered_text(draw, texto, y, fnt, fill, x0=60, x1=None):
    if x1 is None:
        x1 = W - 60
    bb = draw.textbbox((0, 0), str(texto), font=fnt)
    tw = bb[2] - bb[0]
    x = x0 + ((x1 - x0) - tw) / 2
    draw.text((x, y), str(texto), font=fnt, fill=fill)


def draw_multiline_centered(
    draw,
    texto,
    fnt,
    y,
    max_width,
    fill,
    line_gap=10,
    center_x=W / 2
):
    linhas = wrap_text(draw, texto, fnt, max_width)

    bb = draw.textbbox((0, 0), "Ag", font=fnt)
    line_h = bb[3] - bb[1]

    yy = y
    for linha in linhas:
        bb2 = draw.textbbox((0, 0), linha, font=fnt)
        tw = bb2[2] - bb2[0]
        draw.text((center_x - tw / 2, yy), linha, font=fnt, fill=fill)
        yy += line_h + line_gap

    return yy


def fonte_pergunta(draw, texto, max_width=790, max_lines=4):
    tamanhos = [54, 50, 46, 42, 38, 34]

    for tam in tamanhos:
        f = fonte(tam, True)
        linhas = wrap_text(draw, texto, f, max_width)
        if len(linhas) <= max_lines:
            return f

    return fonte(32, True)


def desenhar_logo_texto(draw, modo=1):
    if modo == 1:
        box = [280, 70, 800, 190]
        shadow = [box[0] + 13, box[1] + 14, box[2] + 13, box[3] + 14]
        draw.rounded_rectangle(shadow, radius=34, fill=(9, 52, 130))
        draw.rounded_rectangle(
            box,
            radius=34,
            fill=NAVY,
            outline=CYAN,
            width=7
        )
        draw_centered_text(draw, "JUH QUIZ", 93, fonte(52, True), WHITE, box[0], box[2])
    else:
        box = [55, 70, 300, 150]
        draw.rounded_rectangle(
            box,
            radius=25,
            fill=NAVY,
            outline=CYAN,
            width=5
        )
        draw_centered_text(draw, "JUH QUIZ", 88, fonte(30, True), WHITE, box[0], box[2])


def resolver_caminho_imagem_tema(tema):
    caminho = TEMA_IMAGENS.get(tema)
    if not caminho:
        return None

    candidatos = [Path(caminho), Path("imagens_temas") / Path(caminho).name]
    for cand in candidatos:
        if cand.exists():
            return cand
    return None


def desenhar_painel_imagem_tema(img, tema):
    """
    No modo 2, a imagem do tema é inserida automaticamente
    apenas na tela inicial do tema.
    """
    x1, y1, x2, y2 = 55, 500, 1025, 1470
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [x1-10, y1-10, x2+10, y2+10],
        radius=42,
        fill=(10, 22, 86),
        outline=PURPLE,
        width=6
    )
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=38,
        fill=(230, 239, 255),
        outline=CYAN,
        width=8
    )

    caminho = resolver_caminho_imagem_tema(tema)
    if caminho is not None:
        try:
            foto = Image.open(caminho).convert("RGBA")
            resample_src = getattr(Image, 'Resampling', Image)
            foto = ImageOps.fit(foto, (x2-x1-24, y2-y1-24), method=resample_src.LANCZOS)

            mask = Image.new("L", foto.size, 0)
            md = ImageDraw.Draw(mask)
            md.rounded_rectangle([0, 0, foto.size[0]-1, foto.size[1]-1], radius=28, fill=255)
            foto.putalpha(mask)
            img.paste(foto, (x1+12, y1+12), foto)
            return
        except Exception:
            pass

    draw.rounded_rectangle(
        [x1+36, y1+36, x2-36, y2-36],
        radius=28,
        fill=(220, 232, 252),
        outline=(170, 190, 225),
        width=4
    )
    centro_y = (y1 + y2) // 2
    draw_centered_text(draw, "IMAGEM", centro_y - 35, fonte(34, True), GRAY, x1, x2)
    draw_centered_text(draw, "DO TEMA", centro_y + 15, fonte(29, True), GRAY, x1, x2)


def desenhar_fundo():
    img = gradient_vertical((W, H), NAVY_2, (4, 18, 70))
    draw = ImageDraw.Draw(img)

    for y in range(0, H, 110):
        draw.line([(0, y), (W, y + 180)], fill=(8, 52, 120), width=2)

    draw.ellipse([-180, -150, 430, 440], fill=(4, 45, 110))
    draw.ellipse([760, 60, 1290, 600], fill=(35, 22, 110))

    return img


def desenhar_tema(draw, tema, y):
    for tam in [34, 31, 28, 25, 22]:
        f = fonte(tam, True)
        linhas = wrap_text(draw, tema.upper(), f, 790)
        if len(linhas) <= 2:
            break

    box_h = 68 if len(linhas) == 1 else 105

    draw.rounded_rectangle(
        [120, y, W - 120, y + box_h],
        radius=34,
        fill=NAVY,
        outline=CYAN,
        width=4
    )

    yy = y + 16
    for linha in linhas:
        draw_centered_text(draw, linha, yy, f, CYAN, 135, W - 135)
        bb = draw.textbbox((0, 0), "Ag", font=f)
        yy += (bb[3] - bb[1]) + 6

    return y + box_h


# ============================================================
# RENDER — INTRO
# ============================================================

def render_intro(tema, total_perguntas):
    img = desenhar_fundo()
    draw = ImageDraw.Draw(img)

    if MODO_LAYOUT == 2:
        desenhar_logo_texto(draw, 2)

        draw_centered_text(
            draw,
            "QUANTO VOCÊ SABE SOBRE:",
            210,
            fonte(34, True),
            YELLOW
        )

        f_tema = fonte(60, True)
        linhas = wrap_text(draw, tema.upper(), f_tema, 860)
        if len(linhas) > 2:
            f_tema = fonte(50, True)
            linhas = wrap_text(draw, tema.upper(), f_tema, 860)

        y = 275
        for linha in linhas:
            draw_centered_text(draw, linha, y+4, f_tema, PINK)
            draw_centered_text(draw, linha, y, f_tema, WHITE)
            bb = draw.textbbox((0, 0), "Ag", font=f_tema)
            y += (bb[3] - bb[1]) + 8

        desenhar_painel_imagem_tema(img, tema)
        draw = ImageDraw.Draw(img)

        draw_centered_text(
            draw,
            f"{total_perguntas} PERGUNTAS",
            1525,
            fonte(36, True),
            CYAN
        )
        draw_centered_text(
            draw,
            "RESPONDA E DESCUBRA SE VOCÊ ACERTA TUDO",
            1585,
            fonte(26, True),
            WHITE
        )
        draw_centered_text(
            draw,
            "@juhquiz",
            H - 105,
            fonte(30, True),
            (175, 205, 255)
        )
        return img

    img = desenhar_fundo()
    draw = ImageDraw.Draw(img)

    desenhar_logo_texto(draw, MODO_LAYOUT)

    tema_y = 310
    card_y = 500

    draw_centered_text(
        draw,
        "QUANTO VOCÊ SABE SOBRE:",
        tema_y - 60,
        fonte(28, True),
        YELLOW
    )

    fim_tema = desenhar_tema(draw, tema, tema_y)

    card_top = max(card_y, fim_tema + 60)
    card = [90, card_top, W - 90, card_top + 470]

    draw.rounded_rectangle(
        [card[0] + 15, card[1] + 18, card[2] + 15, card[3] + 18],
        radius=50,
        fill=(0, 5, 30)
    )

    draw.rounded_rectangle(
        card,
        radius=50,
        fill=(7, 31, 110),
        outline=CYAN,
        width=6
    )

    draw_centered_text(
        draw,
        f"{total_perguntas} PERGUNTAS",
        card_top + 72,
        fonte(45, True),
        YELLOW
    )

    draw_centered_text(
        draw,
        "VOCÊ TEM 3 SEGUNDOS",
        card_top + 160,
        fonte(38, True),
        WHITE
    )

    draw_centered_text(
        draw,
        "PARA RESPONDER CADA UMA",
        card_top + 215,
        fonte(34, True),
        WHITE
    )

    chips = [
        ("PERGUNTA", BLUE),
        ("3 • 2 • 1", PURPLE),
        ("RESPOSTA", PINK),
    ]

    x = 155
    widths = [235, 220, 235]
    for (txt, cor), ww in zip(chips, widths):
        draw.rounded_rectangle(
            [x, card_top + 315, x + ww, card_top + 380],
            radius=30,
            fill=cor
        )
        draw_centered_text(
            draw,
            txt,
            card_top + 333,
            fonte(23, True),
            WHITE,
            x,
            x + ww
        )
        x += ww + 25

    draw_centered_text(
        draw,
        "@juhquiz",
        H - 105,
        fonte(30, True),
        (175, 205, 255)
    )

    return img


# ============================================================
# RENDER — PERGUNTA
# ============================================================

def render_frame(tema, pergunta, numero, total_perguntas, estado, timer=None):
    img = desenhar_fundo()
    draw = ImageDraw.Draw(img)

    if MODO_LAYOUT == 2:
        desenhar_logo_texto(draw, 2)

        draw.rounded_rectangle(
            [835, 77, 1015, 145],
            radius=24,
            fill=YELLOW
        )
        draw_centered_text(
            draw,
            f"{numero}/{total_perguntas}",
            94,
            fonte(31, True),
            NAVY,
            835,
            1015
        )

        tema_fim = desenhar_tema(draw, tema, 230)
        card_top = max(345, tema_fim + 28)

    else:
        desenhar_logo_texto(draw, 1)

        draw.rounded_rectangle(
            [835, 80, 1015, 148],
            radius=24,
            fill=YELLOW
        )
        draw_centered_text(
            draw,
            f"{numero}/{total_perguntas}",
            97,
            fonte(31, True),
            NAVY,
            835,
            1015
        )

        tema_fim = desenhar_tema(draw, tema, 230)
        card_top = max(345, tema_fim + 28)

    card = [55, card_top, W - 55, H - 105]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [card[0] + 18, card[1] + 22, card[2] + 18, card[3] + 22],
        radius=48,
        fill=(0, 0, 0, 95)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        card,
        radius=48,
        fill=WHITE,
        outline=CYAN,
        width=8
    )

    chamada = [310, card_top + 28, 770, card_top + 91]
    draw.rounded_rectangle(
        chamada,
        radius=31,
        fill=PURPLE
    )
    draw_centered_text(
        draw,
        "DESAFIO RÁPIDO",
        card_top + 45,
        fonte(27, True),
        WHITE,
        chamada[0],
        chamada[2]
    )

    draw_centered_text(
        draw,
        f"PERGUNTA {numero} DE {total_perguntas}",
        card_top + 115,
        fonte(25, True),
        BLUE
    )

    f_q = fonte_pergunta(draw, pergunta["pergunta"], max_width=790, max_lines=4)
    linhas = wrap_text(draw, pergunta["pergunta"], f_q, 790)

    bb_ag = draw.textbbox((0, 0), "Ag", font=f_q)
    line_h = bb_ag[3] - bb_ag[1]
    bloco_h = len(linhas) * (line_h + 8)

    question_y = card_top + 175
    question_bottom = question_y + bloco_h

    draw.rounded_rectangle(
        [125, question_y - 15, W - 125, question_bottom + 16],
        radius=20,
        fill=(255, 241, 132)
    )

    yy = question_y
    for linha in linhas:
        draw_centered_text(
            draw,
            linha,
            yy,
            f_q,
            NAVY,
            125,
            W - 125
        )
        yy += line_h + 8

    timer_y = max(card_top + 410, question_bottom + 58)
    timer_size = 118
    tx0 = W / 2 - timer_size / 2
    ty0 = timer_y
    tx1 = W / 2 + timer_size / 2
    ty1 = timer_y + timer_size

    draw.ellipse(
        [tx0 - 7, ty0 - 7, tx1 + 7, ty1 + 7],
        fill=CYAN
    )
    draw.ellipse(
        [tx0, ty0, tx1, ty1],
        fill=NAVY
    )

    if estado == "reading":
        timer_txt = "..."
        feedback = "OUÇA A PERGUNTA"
    elif estado == "countdown":
        timer_txt = str(timer)
        feedback = "RESPONDA AGORA"
    else:
        timer_txt = "✓"
        feedback = "RESPOSTA CORRETA"

    draw_centered_text(
        draw,
        timer_txt,
        timer_y + 24,
        fonte(50, True),
        WHITE,
        int(tx0),
        int(tx1)
    )

    draw_centered_text(
        draw,
        feedback,
        timer_y + 135,
        fonte(24, True),
        PURPLE
    )

    alt_top = timer_y + 195
    disponivel = (H - 225) - alt_top
    alt_gap = 22
    alt_h = min(116, max(82, int((disponivel - 2 * alt_gap) / 3)))

    letras = ["A", "B", "C"]
    cores = [CYAN, PURPLE, YELLOW]

    for j, alt in enumerate(pergunta["alternativas"]):
        yy = alt_top + j * (alt_h + alt_gap)
        correta = j == int(pergunta["correta"])

        if estado == "answer" and correta:
            bg = (220, 255, 236)
            outline = GREEN
            label_bg = GREEN
            text_color = GREEN_DARK
        elif estado == "answer" and not correta:
            bg = (238, 241, 248)
            outline = (190, 198, 218)
            label_bg = (150, 160, 185)
            text_color = (120, 126, 145)
        else:
            bg = (255, 255, 255)
            outline = cores[j]
            label_bg = cores[j]
            text_color = NAVY

        box = [120, yy, W - 120, yy + alt_h]

        draw.rounded_rectangle(
            [box[0] + 7, box[1] + 8, box[2] + 7, box[3] + 8],
            radius=24,
            fill=(214, 222, 240)
        )
        draw.rounded_rectangle(
            box,
            radius=24,
            fill=bg,
            outline=outline,
            width=5
        )

        label_w = 78
        label = [
            box[0] + 18,
            yy + 14,
            box[0] + 18 + label_w,
            yy + alt_h - 14
        ]

        draw.rounded_rectangle(
            label,
            radius=18,
            fill=label_bg
        )

        letra = "✓" if estado == "answer" and correta else letras[j]

        draw_centered_text(
            draw,
            letra,
            yy + max(18, (alt_h - 46) // 2),
            fonte(35, True),
            NAVY if (j == 2 and not (estado == "answer" and correta)) else WHITE,
            int(label[0]),
            int(label[2])
        )

        tam_alt = 35
        if len(alt) > 45:
            tam_alt = 28
        elif len(alt) > 32:
            tam_alt = 31

        f_alt = fonte(tam_alt, True)
        alt_lines = wrap_text(draw, alt, f_alt, box[2] - (label[2] + 65))

        bb_alt = draw.textbbox((0, 0), "Ag", font=f_alt)
        lh_alt = bb_alt[3] - bb_alt[1]

        total_alt_h = len(alt_lines) * (lh_alt + 3)
        alt_text_y = yy + (alt_h - total_alt_h) / 2

        for linha in alt_lines[:2]:
            draw.text(
                (label[2] + 28, alt_text_y),
                linha,
                font=f_alt,
                fill=text_color
            )
            alt_text_y += lh_alt + 3

    dot_y = H - 150
    if total_perguntas <= 12:
        espacamento = min(42, 720 / max(1, total_perguntas - 1)) if total_perguntas > 1 else 0
        largura_total = espacamento * max(0, total_perguntas - 1)
        start_x = W / 2 - largura_total / 2
        raio = 8 if total_perguntas <= 8 else 6

        for i in range(total_perguntas):
            cx = start_x + i * espacamento
            if i < numero - 1:
                cor = GREEN
            elif i == numero - 1:
                cor = BLUE
            else:
                cor = (196, 209, 236)
            draw.ellipse(
                [cx-raio, dot_y-raio, cx+raio, dot_y+raio],
                fill=cor
            )
    else:
        barra = [180, dot_y - 8, W - 180, dot_y + 8]
        draw.rounded_rectangle(barra, radius=8, fill=(196, 209, 236))
        progresso = numero / total_perguntas
        draw.rounded_rectangle(
            [barra[0], barra[1], barra[0] + (barra[2]-barra[0]) * progresso, barra[3]],
            radius=8,
            fill=BLUE
        )

    draw_centered_text(
        draw,
        "@juhquiz • QUANTAS VOCÊ CONSEGUE ACERTAR?",
        H - 105,
        fonte(22, True),
        (176, 196, 230)
    )

    return img


# ============================================================
# RENDER — FINAL
# ============================================================

def render_final(tema, total_perguntas):
    img = desenhar_fundo()
    draw = ImageDraw.Draw(img)

    desenhar_logo_texto(draw, 1)

    draw_centered_text(
        draw,
        "FIM DO DESAFIO!",
        500,
        fonte(65, True),
        YELLOW
    )

    desenhar_tema(draw, tema, 630)

    draw_centered_text(
        draw,
        "QUANTAS VOCÊ ACERTOU?",
        830,
        fonte(48, True),
        WHITE
    )

    draw_centered_text(
        draw,
        f"{total_perguntas}/{total_perguntas}?",
        960,
        fonte(100, True),
        CYAN
    )

    draw.rounded_rectangle(
        [180, 1120, W - 180, 1255],
        radius=38,
        fill=PURPLE,
        outline=CYAN,
        width=5
    )
    draw_centered_text(
        draw,
        "COMENTA SUA PONTUAÇÃO",
        1160,
        fonte(34, True),
        WHITE,
        180,
        W - 180
    )

    draw_centered_text(
        draw,
        "@juhquiz",
        H - 120,
        fonte(34, True),
        (180, 210, 255)
    )

    return img


# ============================================================
# ÁUDIO / FFMPEG
# ============================================================

def limpar_tts(texto):
    texto = str(texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tts_salvar(texto, caminho):
    caminho = Path(caminho)
    if caminho.exists():
        caminho.unlink()

    cmd = [
        "edge-tts",
        "--voice", VOZ,
        "--rate", VELOCIDADE_VOZ,
        "--text", limpar_tts(texto),
        "--write-media", str(caminho)
    ]

    executar(cmd)

    if not caminho.exists() or caminho.stat().st_size < 500:
        raise RuntimeError(f"Áudio não foi criado: {caminho}")


def duracao_audio(caminho):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(caminho)
    ]
    return float(subprocess.check_output(cmd, text=True).strip())


def criar_beep(caminho, frequencia=950):
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency={frequencia}:duration=0.14",
        "-af", "volume=0.55,apad=pad_dur=1",
        "-t", "1.0",
        "-c:a", "aac",
        "-b:a", "160k",
        "-ar", str(AUDIO_HZ),
        "-ac", str(AUDIO_CHANNELS),
        str(caminho)
    ]
    executar(cmd)


def criar_clipe_imagem(img_path, duracao, saida, audio=None):
    duracao = float(duracao)

    if audio:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-i", str(audio),
            "-t", f"{duracao:.3f}",
            "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
            "-af", f"aresample={AUDIO_HZ}:async=1:first_pts=0,apad",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", str(AUDIO_HZ),
            "-ac", str(AUDIO_CHANNELS),
            "-video_track_timescale", "90000",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            str(saida)
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-f", "lavfi",
            "-i", f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_HZ}",
            "-t", f"{duracao:.3f}",
            "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", str(AUDIO_HZ),
            "-ac", str(AUDIO_CHANNELS),
            "-shortest",
            "-video_track_timescale", "90000",
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            str(saida)
        ]

    executar(cmd)


def juntar_clipes(lista, saida, concat_path):
    concat_path = Path(concat_path).resolve()
    saida = Path(saida).resolve()

    concat_path.parent.mkdir(parents=True, exist_ok=True)
    saida.parent.mkdir(parents=True, exist_ok=True)

    with open(concat_path, "w", encoding="utf-8") as f:
        for p in lista:
            p_abs = Path(p).resolve()

            if not p_abs.exists():
                raise FileNotFoundError(f"Segmento não encontrado: {p_abs}")

            caminho_ffmpeg = str(p_abs).replace("'", "'\\''")
            f.write("file '" + caminho_ffmpeg + "'\n")

    cmd = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_path),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "160k",
        "-ar", str(AUDIO_HZ),
        "-ac", str(AUDIO_CHANNELS),
        "-af", f"aresample={AUDIO_HZ}:async=1:first_pts=0",
        "-avoid_negative_ts", "make_zero",
        "-movflags", "+faststart",
        str(saida)
    ]

    executar(cmd)


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar():
    if not isinstance(QUIZZES, dict) or not QUIZZES:
        raise ValueError("QUIZZES está vazio.")

    for tema, perguntas in QUIZZES.items():
        if not str(tema).strip():
            raise ValueError("Existe um tema sem nome.")

        if not isinstance(perguntas, list) or len(perguntas) < 1:
            raise ValueError(
                f"Tema '{tema}' precisa ter pelo menos 1 pergunta."
            )

        for posicao, q in enumerate(perguntas, start=1):
            if not str(q.get("pergunta", "")).strip():
                raise ValueError(
                    f"Tema '{tema}', pergunta {posicao}: falta o texto da pergunta."
                )

            alternativas = q.get("alternativas", [])
            if len(alternativas) != 3:
                raise ValueError(
                    f"Tema '{tema}', pergunta {posicao}: "
                    "precisa ter exatamente 3 alternativas."
                )

            if any(not str(a).strip() for a in alternativas):
                raise ValueError(
                    f"Tema '{tema}', pergunta {posicao}: "
                    "há alternativa vazia."
                )

            if int(q.get("correta", -1)) not in (0, 1, 2):
                raise ValueError(
                    f"Tema '{tema}', pergunta {posicao}: "
                    "'correta' deve ser 0, 1 ou 2."
                )


# ============================================================
# GERAÇÃO
# ============================================================

def main():
    validar()

    if PASTA_TMP.exists():
        shutil.rmtree(PASTA_TMP)

    PASTA_TMP.mkdir(parents=True, exist_ok=True)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    print("=" * 72, flush=True)
    print("JUH QUIZ NEON", flush=True)
    print(f"Modo: {MODO_LAYOUT} — {NOME_MODO}", flush=True)
    print(f"Voz: {VOZ}", flush=True)
    print(f"Velocidade: {VELOCIDADE_VOZ}", flush=True)
    print(f"Vídeos: {len(QUIZZES)}", flush=True)
    print("=" * 72, flush=True)

    beep_normal = PASTA_TMP / "beep_950.m4a"
    beep_final = PASTA_TMP / "beep_1250.m4a"

    criar_beep(beep_normal, 950)
    criar_beep(beep_final, 1250)

    videos_gerados = []

    temas = list(QUIZZES.items())

    for video_num, (tema, perguntas) in enumerate(temas, start=1):
        perguntas_tema = perguntas
        total_perguntas = len(perguntas_tema)

        print("\n" + "=" * 72, flush=True)
        print(
            f"🎬 {video_num:02d}/{len(temas):02d} — {tema}",
            flush=True
        )
        print("=" * 72, flush=True)

        pasta_video = PASTA_TMP / f"video_{video_num:02d}_{slug(tema)}"
        pasta_video.mkdir(parents=True, exist_ok=True)

        segmentos = []

        frame_tema = pasta_video / "00_tema.png"
        render_intro(tema, total_perguntas).save(frame_tema)

        audio_tema = pasta_video / "00_tema.mp3"
        fala_tema = f"Quanto você sabe sobre: {tema}?"
        tts_salvar(fala_tema, audio_tema)

        dur_tema = duracao_audio(audio_tema) + PAUSA_DEPOIS_TEMA

        clip_tema = pasta_video / "00_tema.mp4"
        criar_clipe_imagem(
            frame_tema,
            dur_tema,
            clip_tema,
            audio=audio_tema
        )
        segmentos.append(clip_tema)

        for idx, pergunta in enumerate(perguntas_tema):
            numero = idx + 1

            print(
                f" • {numero}/{total_perguntas} — {pergunta['pergunta']}",
                flush=True
            )

            pasta_q = pasta_video / f"q{numero:02d}"
            pasta_q.mkdir(parents=True, exist_ok=True)

            audio_q = pasta_q / "pergunta.mp3"
            tts_salvar(pergunta["pergunta"], audio_q)

            dur_q = duracao_audio(audio_q) + PAUSA_DEPOIS_PERGUNTA

            frame_q = pasta_q / "01_pergunta.png"
            render_frame(
                tema=tema,
                pergunta=pergunta,
                numero=numero,
                total_perguntas=total_perguntas,
                estado="reading"
            ).save(frame_q)

            clip_q = pasta_q / "01_pergunta.mp4"
            criar_clipe_imagem(
                frame_q,
                dur_q,
                clip_q,
                audio=audio_q
            )
            segmentos.append(clip_q)

            for segundos in range(TEMPO_ESCOLHA, 0, -1):
                frame_timer = pasta_q / f"timer_{segundos}.png"

                render_frame(
                    tema=tema,
                    pergunta=pergunta,
                    numero=numero,
                    total_perguntas=total_perguntas,
                    estado="countdown",
                    timer=segundos
                ).save(frame_timer)

                clip_timer = pasta_q / f"timer_{segundos}.mp4"

                som = beep_final if segundos == 1 else beep_normal

                criar_clipe_imagem(
                    frame_timer,
                    1.0,
                    clip_timer,
                    audio=som
                )
                segmentos.append(clip_timer)

            correta = int(pergunta["correta"])
            texto_resposta = pergunta["alternativas"][correta]

            audio_resp = pasta_q / "resposta.mp3"
            tts_salvar(texto_resposta, audio_resp)

            dur_resp = (
                duracao_audio(audio_resp)
                + PAUSA_DEPOIS_RESPOSTA
            )

            frame_resp = pasta_q / "03_resposta.png"
            render_frame(
                tema=tema,
                pergunta=pergunta,
                numero=numero,
                total_perguntas=total_perguntas,
                estado="answer"
            ).save(frame_resp)

            clip_resp = pasta_q / "03_resposta.mp4"
            criar_clipe_imagem(
                frame_resp,
                dur_resp,
                clip_resp,
                audio=audio_resp
            )
            segmentos.append(clip_resp)

        frame_final = pasta_video / "final.png"
        render_final(tema, total_perguntas).save(frame_final)

        clip_final = pasta_video / "final.mp4"
        criar_clipe_imagem(
            frame_final,
            2.0,
            clip_final
        )
        segmentos.append(clip_final)

        nome_saida = (
            f"{video_num:02d}_{slug(tema)}_"
            f"modo{MODO_LAYOUT}_{DATA_DO_DIA}.mp4"
        )
        saida_video = PASTA_SAIDA / nome_saida

        juntar_clipes(
            segmentos,
            saida_video,
            pasta_video / "concat.txt"
        )

        videos_gerados.append(saida_video)

        print("✅ Gerado:", saida_video, flush=True)

    print("\n✅ FINALIZADO", flush=True)
    print(f"📁 {PASTA_SAIDA}", flush=True)

    for p in videos_gerados:
        print(" -", p, flush=True)


if __name__ == "__main__":
    main()
