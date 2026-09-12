# -*- coding: utf-8 -*-

# =========================================================
# EDITE APENAS ESTE ARQUIVO PARA TROCAR O CONTEÚDO DO VÍDEO
# =========================================================

TEMA = "ELEIÇÕES 2026"
HASHTAG = "#Eleições2026"

GANCHO = "Você sabe isso sobre as Eleições 2026?"

# Cada pergunta precisa de:
# - pergunta
# - 4 opções
# - correta = 0, 1, 2 ou 3
# - explicacao curta
#
# O vídeo:
# 1) lê APENAS a pergunta
# 2) faz contagem 3, 2, 1
# 3) destaca a resposta correta
# 4) lê APENAS a resposta correta
# 5) mostra a explicação curta

PERGUNTAS = [
    {
        "pergunta": "Onde é mais seguro confirmar regras e prazos das Eleições 2026?",
        "opcoes": [
            "Site oficial do TSE ou TRE",
            "Comentários de vídeos",
            "Grupo de mensagens",
            "Perfil sem fonte",
        ],
        "correta": 0,
        "explicacao": "Para regras, datas e procedimentos, priorize sempre os canais oficiais da Justiça Eleitoral.",
    },
    {
        "pergunta": "Se você tiver dúvida sobre voto em trânsito, onde deve conferir as regras atualizadas?",
        "opcoes": [
            "Em qualquer postagem viral",
            "Nos canais oficiais da Justiça Eleitoral",
            "Somente com amigos",
            "Em comentários de vídeos",
        ],
        "correta": 1,
        "explicacao": "As regras podem depender do calendário eleitoral; por isso, confira a orientação oficial atualizada.",
    },
    {
        "pergunta": "Qual atitude ajuda a deixar um vídeo informativo mais confiável?",
        "opcoes": [
            "Omitir a fonte",
            "Usar somente opinião",
            "Citar a fonte oficial",
            "Inventar um exemplo",
        ],
        "correta": 2,
        "explicacao": "Mostrar a origem da informação ajuda quem assiste a conferir o conteúdo.",
    },
    {
        "pergunta": "Qual formato combina melhor com uma hashtag informativa?",
        "opcoes": [
            "Rumor sem data",
            "Pegadinha sem contexto",
            "Dica curta e com fonte",
            "Informação sem origem",
        ],
        "correta": 2,
        "explicacao": "Conteúdo curto, claro e verificável tende a funcionar melhor para temas informativos.",
    },
    {
        "pergunta": "Qual chamada final combina mais com esse tipo de vídeo?",
        "opcoes": [
            "Confira a informação nos canais oficiais",
            "Compartilhe antes de conferir",
            "Ignore a fonte",
            "Acredite só porque viralizou",
        ],
        "correta": 0,
        "explicacao": "O ideal é incentivar o público a verificar a informação em fonte oficial.",
    },
]

FECHAMENTO = "Quantas você acertou? Confira sempre as informações oficiais antes de compartilhar."
