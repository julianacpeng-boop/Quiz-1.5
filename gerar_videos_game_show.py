"""
Arquivo de compatibilidade para o Quiz-1.5.

Ele carrega o dicionário QUIZZES diretamente do gerador oficial
do repositório Quiz-vers-o-1.3, evitando duplicar as 225 perguntas.
"""

from urllib.request import Request, urlopen

URL_ORIGINAL = (
    "https://raw.githubusercontent.com/"
    "julianacpeng-boop/Quiz-vers-o-1.3/main/gerar_videos_game_show.py"
)

def _carregar_quizzes():
    req = Request(
        URL_ORIGINAL,
        headers={"User-Agent": "JuhQuiz-1.5"}
    )

    with urlopen(req, timeout=60) as resp:
        codigo = resp.read().decode("utf-8")

    namespace = {
        "__name__": "quiz_v13_fonte",
        "__file__": URL_ORIGINAL,
    }

    exec(compile(codigo, URL_ORIGINAL, "exec"), namespace)

    if "QUIZZES" not in namespace:
        raise RuntimeError(
            "O arquivo da versão 1.3 foi carregado, mas QUIZZES não foi encontrado."
        )

    return namespace["QUIZZES"]


QUIZZES = _carregar_quizzes()
