# Juh Quiz - Gerador com 6 Layouts

Este projeto gera um vídeo vertical 1080x1920 em MP4 pelo GitHub Actions.

## Layouts

1. Eleições / informativo — amarelo, azul e laranja
2. Casal / flerte — azul e vermelho
3. Rock / festival — preto, pink e roxo
4. Cinema — amarelo, vermelho e preto
5. Country / peão — marrom e dourado
6. Morango / receita — roxo, pink e vermelho

## Voz

O projeto usa a mesma configuração dos seus outros vídeos:

- `pt-BR-AntonioNeural`
- velocidade `+10%`
- lê somente a pergunta
- depois da contagem, lê somente a resposta correta

## Como usar no GitHub

1. Envie estes arquivos mantendo as pastas.
2. Edite `campanha.py` com o tema e as 5 perguntas.
3. Abra a aba **Actions**.
4. Escolha **Gerar Juh Quiz - 6 Layouts**.
5. Clique em **Run workflow**.
6. Escolha de **1 a 6**.
7. Execute.
8. Baixe o MP4 em **Artifacts**.

## Teste local

```bash
python gerar_video.py --layout 3
```

ou:

```bash
LAYOUT=3 python gerar_video.py
```

O resultado fica na pasta `output/`.
