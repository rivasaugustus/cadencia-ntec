# Cadência

O script `scripts/montar_cadencia.py` aplica tudo o que está aqui. Este arquivo serve para entender o que ele devolve e explicar ao CN. Não refaça datas nem textos à mão.

## Os três momentos

Os textos são os do documento "Cadências, mensagens e follow-up | CNs", com as chaves dele: M1 é o momento pós AT Diagnóstica, M2 o pós AT Aprofundamento, M3 o pós Apresentação de Proposta; F01, F02... são as mensagens de cada momento.

| `--momento` | Hoje, se a reunião foi hoje | Até a próxima reunião (D) |
|---|---|---|
| `pos-diag` | E-mail M1-F01 + WhatsApp M1-F02 | Véspera M1-F03 (+ M1-F04 na mesma task, se D − Diag > 4 dias) · Sala M1-F05 · `AT Aprofundamento - {h}` |
| `pos-aprof` | E-mail M2-F01 + WhatsApp M2-F02 | Pedido M2-F05 (só com `--pedido`) · Véspera M2-F03 · Sala M2-F04 · `Apresentação de Proposta - {h}` |
| `pos-proposta` | Champions Letter M3-F01 + WhatsApp M3-F02 | Disponibilidade M3-F03 (só se D − hoje ≥ 5 dias) · Sala M3-F04 · `Próximos passos - {h}` |

## Datas

- **Pós-reunião** (F01 + F02): sempre sai, hoje (ou no próximo dia útil, se hoje é fim de semana). O documento pede o envio até 1 ou 2 horas depois da reunião, então o ideal é rodar no mesmo dia. Se a reunião foi antes, o script ajusta o "hoje" dos textos para o dia dela e avisa:
  - 1 dia antes: "conversa de ontem", "reunião de ontem", "apresentado ontem";
  - 2 a 6 dias: "conversa de sexta-feira", "apresentado na sexta-feira";
  - 7 dias ou mais: "conversa do dia 13/11", "apresentado no dia 13/11".

  O CN já mandou o pós por conta própria: passe as chaves em `--pular` (veja o passo 4 do fluxo).
- **Véspera** (M1-F03, M2-F03): dia útil anterior a D. Se esse dia não é a véspera de calendário (reunião de segunda, véspera na sexta), o script troca "amanhã" pelo dia da semana nas frases da véspera e do complemento, e avisa. É a única mudança de texto além dos marcadores.
- **Complemento** (M1-F04): vai na mesma task da véspera, como "Mensagem 2, logo em seguida", quando o Aprof é mais de 4 dias depois do Diag. Com `--spoiler`, entra a linha do spoiler e a pendência de mandar o print; sem, as duas linhas opcionais saem.
- **Pedido** (M2-F05): o primeiro dia útil, de hoje até a véspera de D, sem nenhum toque; sem dia livre, o primeiro com um toque só. Se todos já têm dois, fica de fora.
- **Disponibilidade** (M3-F03): 2 dias úteis antes de D, só quando D está a 5 dias ou mais (o documento diz "principalmente quando o prazo for grande").
- **Sala**: no dia D, assunto com o horário da reunião menos 3 minutos (o documento pede 3 a 5).
- **Reunião**: task do tipo meeting no dia D.
- **No máximo dois toques por dia.** O CN abre dois canais com o cliente (e-mail e WhatsApp), então dois toques no mesmo dia podem acontecer; mais que isso é demais. Cada mensagem enviada conta um: o pós-reunião (e-mail + WhatsApp) já ocupa os dois do dia. A véspera com o complemento (M1-F04) conta um, porque é uma conversa só. A sala e a task da reunião não contam. Prioridade quando não cabe: pós-reunião, véspera, disponibilidade, pedido.
- **Pedido** procura primeiro um dia sem nenhum toque antes da reunião; só divide dia com outro toque (a véspera, por exemplo) quando não sobra dia livre, e avisa.
- Nada cai no passado, nem em sábado ou domingo. Próxima reunião em fim de semana ou já passada é `erro`.

## Marcadores

| Marcador | Vira |
|---|---|
| `[Nome]` | `--nome` (primeiro nome, ou "Ana e João") |
| `[Empresa]` | `--empresa` |
| `[Nome e Sobrenome]` | `apresentacao_whats` do perfil |
| `[horário]`, `[Horário]` | horário de D (17h, 16h30) |
| `[Dia da semana]` | dia de D (quinta-feira) |
| `[data]`, `[dia]` | D por extenso (quinta-feira, 03/12, às 15h) |
| `[Link]` | `--link-sala`; sem ele, `LINK DA SALA DA REUNIÃO` e pendência |
| `[Link do protótipo]` | `--link-prototipo`; sem ele, `LINK DO PROTÓTIPO` e pendência |
| `[Parágrafo autoral]` | `--paragrafo` (veja `contexto.md`) |
| `[Pedido]` e "da solução/proposta/protótipo" | `--pedido` e `--pedido-objeto` |

Nunca invente um link para não deixar o marcador: marcador visível é pendência que o CN resolve; link errado vai para o cliente.

## Escolha entre as sugestões

- **Pós-Diag (M1-F01):** com `--paragrafo`, sugestão 2; sem, sugestão 1. O perfil pode fixar uma das duas (`sugestao_pos_diag`); fixada a 2 sem parágrafo, é `erro`.
- **Pós-Aprof (M2-F01):** igual, com `sugestao_pos_aprof`. A sugestão 1 pede ajustes "até 3 dias antes da reunião": se D está a menos de 4 dias, o script avisa em `pendencias` para o CN revisar essa linha no rascunho.
- **WhatsApp pós-Diag (M1-F02):** `--grupo` usa a versão de grupo ("Olá, pessoal!").

## Saída do script

JSON com:

- `tasks`: `chave`, `canal`, `tipo`, `assunto`, `data`, `data_curta`, `note` (HTML) e, nas de e-mail, `email` (`assunto` e `corpo` para o rascunho) e `rascunho` (a URL passada em `--rascunho`, ou null).
- `nao_criadas`: chave e motivo.
- `pendencias`: o que o CN precisa completar (link, anexo, rascunho).
- `avisos`: decisões que o script tomou (sugestão escolhida, complemento, troca do "amanhã").
- `proxima`: reunião, data, hora e por extenso; null sem `--proxima`.
- Em erro: `{"erro": ...}` (dado de entrada, código 2) ou `{"erro_interno": ...}` (texto ou perfil, código 3).

## Mudar um texto

O script confere o hash de `MENSAGENS` e para com `erro_interno` se algum texto mudou. Isso garante que nenhum texto do documento é alterado sem querer. Quando o documento oficial mudar e o CN pedir a atualização: troque o texto em `MENSAGENS` (mantendo os marcadores entre colchetes) e atualize `HASH_MENSAGENS` com o sha256 do conteúdo em UTF-8. Nunca corrija o texto direto na task nem ajuste o hash sem pedido.

## Fora do documento

Retomada, contrato, cobrança, TouchPoint, lead que ficou de falar com TI e outros casos sem modelo: a skill escreve as mensagens com base no repertório do documento e no contexto, e passa ao script em `--livre`. Regras, cadências sugeridas e formato em `sem-modelo.md`. Essas mensagens não passam pelo hash; o script só aplica o perfil, confere marcadores e travessão, e encaixa as datas no limite de toques.
