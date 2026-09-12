# -*- coding: utf-8 -*-

# =========================================================
# JUH QUIZ 1.5 — VÁRIOS VÍDEOS NA MESMA EXECUÇÃO
# =========================================================
#
# Cada bloco dentro de VIDEOS gera 1 MP4.
#
# O campo "layout" indica qual visual aquele vídeo usa:
#
# 1 = Informativo / Eleições
# 2 = Casal Flertando
# 3 = Festival / Rock in Rio
# 4 = Cinema
# 5 = Country / Peão
# 6 = Morango / Receita
#
# Você pode misturar layouts na MESMA execução.
# Exemplo:
# vídeo 1 -> layout 1
# vídeo 2 -> layout 3
# vídeo 3 -> layout 6
#
# Cada vídeo precisa ter EXATAMENTE 5 perguntas.
#
# correta:
# 0 = A
# 1 = B
# 2 = C
# 3 = D
# =========================================================


VIDEOS = [

    # =====================================================
    # VÍDEO 1 — ELEIÇÕES 2026
    # =====================================================
    {
        "id": "eleicoes_01",
        "layout": 1,
        "tema": "ELEIÇÕES 2026",
        "hashtag": "#Eleições2026",
        "gancho": "Você está por dentro das Eleições 2026?",

        "perguntas": [
            {
                "pergunta": "Em que dia acontece o primeiro turno das Eleições 2026?",
                "opcoes": [
                    "27 de setembro",
                    "4 de outubro",
                    "11 de outubro",
                    "25 de outubro",
                ],
                "correta": 1,
                "explicacao": "O primeiro turno das Eleições 2026 será realizado em 4 de outubro.",
            },
            {
                "pergunta": "Se houver segundo turno, em que dia ele será realizado?",
                "opcoes": [
                    "11 de outubro",
                    "18 de outubro",
                    "1º de novembro",
                    "25 de outubro",
                ],
                "correta": 3,
                "explicacao": "O eventual segundo turno está marcado para 25 de outubro.",
            },
            {
                "pergunta": "Qual será o horário de votação nas Eleições 2026?",
                "opcoes": [
                    "Das 8h às 17h",
                    "Das 7h às 16h",
                    "Das 9h às 18h",
                    "Das 8h às 18h",
                ],
                "correta": 0,
                "explicacao": "A votação ocorrerá das 8h às 17h, pelo horário de Brasília.",
            },
            {
                "pergunta": "Quantos senadores serão escolhidos nas Eleições 2026?",
                "opcoes": [
                    "27",
                    "81",
                    "54",
                    "108",
                ],
                "correta": 2,
                "explicacao": "Em 2026 serão escolhidos 54 senadores, correspondentes a dois terços do Senado.",
            },
            {
                "pergunta": "Qual destes cargos não será escolhido nas Eleições 2026?",
                "opcoes": [
                    "Governador",
                    "Prefeito",
                    "Senador",
                    "Presidente da República",
                ],
                "correta": 1,
                "explicacao": "Prefeitos são escolhidos nas eleições municipais, e não nas eleições gerais de 2026.",
            },
        ],

        "fechamento": "Quantas você acertou? Comenta seu resultado!",
    },


    # =====================================================
    # VÍDEO 2 — ORDEM DE VOTAÇÃO
    # =====================================================
    {
        "id": "eleicoes_02",
        "layout": 1,
        "tema": "ORDEM DE VOTAÇÃO 2026",
        "hashtag": "#Eleições2026",
        "gancho": "Você sabe a ordem correta de votação na urna?",

        "perguntas": [
            {
                "pergunta": "Qual será a primeira escolha do eleitor na urna em 2026?",
                "opcoes": [
                    "Presidente",
                    "Governador",
                    "Deputado Federal",
                    "Senador",
                ],
                "correta": 2,
                "explicacao": "A primeira escolha na urna será para deputado federal.",
            },
            {
                "pergunta": "Depois de deputado federal, qual cargo aparece na urna?",
                "opcoes": [
                    "Deputado Estadual ou Distrital",
                    "Governador",
                    "Presidente",
                    "Senador",
                ],
                "correta": 0,
                "explicacao": "A segunda escolha será para deputado estadual ou distrital.",
            },
            {
                "pergunta": "Quantas escolhas para senador o eleitor fará em 2026?",
                "opcoes": [
                    "Uma",
                    "Três",
                    "Quatro",
                    "Duas",
                ],
                "correta": 3,
                "explicacao": "Em 2026 o eleitor fará duas escolhas para o Senado.",
            },
            {
                "pergunta": "Qual cargo aparece imediatamente antes de presidente na urna?",
                "opcoes": [
                    "Senador",
                    "Governador",
                    "Deputado Federal",
                    "Deputado Estadual",
                ],
                "correta": 1,
                "explicacao": "Governador será a penúltima escolha da votação.",
            },
            {
                "pergunta": "Qual será a última escolha na urna eletrônica em 2026?",
                "opcoes": [
                    "Governador",
                    "Senador",
                    "Presidente da República",
                    "Deputado Federal",
                ],
                "correta": 2,
                "explicacao": "Presidente da República será a última escolha na sequência da urna.",
            },
        ],

        "fechamento": "Você lembraria dessa ordem na hora de votar?",
    },


    # =====================================================
    # VÍDEO 3 — REGRAS DO VOTO
    # =====================================================
    {
        "id": "eleicoes_03",
        "layout": 1,
        "tema": "REGRAS DO VOTO 2026",
        "hashtag": "#Eleições2026",
        "gancho": "Será que você conhece mesmo as regras das Eleições 2026?",

        "perguntas": [
            {
                "pergunta": "Qual é a idade mínima para concorrer ao cargo de deputado federal?",
                "opcoes": [
                    "21 anos",
                    "18 anos",
                    "30 anos",
                    "35 anos",
                ],
                "correta": 0,
                "explicacao": "A idade mínima para deputado federal é de 21 anos.",
            },
            {
                "pergunta": "Qual é a idade mínima para concorrer ao Senado?",
                "opcoes": [
                    "30 anos",
                    "35 anos",
                    "40 anos",
                    "21 anos",
                ],
                "correta": 1,
                "explicacao": "A idade mínima para senador é de 35 anos.",
            },
            {
                "pergunta": "Qual é a idade mínima para concorrer ao cargo de governador?",
                "opcoes": [
                    "18 anos",
                    "21 anos",
                    "35 anos",
                    "30 anos",
                ],
                "correta": 3,
                "explicacao": "A idade mínima para governador é de 30 anos.",
            },
            {
                "pergunta": "Quem votar em trânsito fora do seu estado poderá votar em qual cargo?",
                "opcoes": [
                    "Governador",
                    "Senador",
                    "Presidente da República",
                    "Deputado Federal",
                ],
                "correta": 2,
                "explicacao": "Fora do estado do domicílio eleitoral, o voto em trânsito é para presidente da República.",
            },
            {
                "pergunta": "No voto em trânsito dentro do próprio estado, em quais cargos é possível votar?",
                "opcoes": [
                    "Somente presidente",
                    "Presidente e governador",
                    "Somente cargos legislativos",
                    "Presidente, governador, senador e deputados",
                ],
                "correta": 3,
                "explicacao": "Dentro do próprio estado, o eleitor em trânsito pode votar nos cargos das eleições gerais.",
            },
        ],

        "fechamento": "Quantas dessas regras você já conhecia? Comenta seu placar!",
    },
]
