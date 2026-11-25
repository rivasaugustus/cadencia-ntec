# Casos sem modelo no documento

O documento de cadências cobre o caminho feliz: reunião feita, próxima marcada. O funil real tem situações que ele não cobre, e várias estão na própria lista "[Criar para uma V2 aprimorada]" dele. Nesses casos a skill escreve as mensagens, usando como base o repertório do documento e o contexto do card.

## Quando é caso sem modelo

- Lead que parou de responder, em qualquer etapa.
- Lead que ficou de falar com o TI ou com superiores antes de marcar o Aprof (a sugestão da Bia no documento).
- Cobrança de documento ou de ponto combinado que não chegou.
- Reunião depois da proposta que não é a de próximos passos: TouchPoint, negociação, alinhamento.
- Envio do contrato para assinatura e follow-up da assinatura.
- Follow-up pós-proposta com case ou conteúdo para manter o lead aquecido.
- Retomada de lead perdido.
- Qualquer outro toque que o CN peça e que nenhum F do documento resolva.

Se um F do documento resolve, use o F: a mensagem livre não substitui o modelo.

## Como escrever

**O repertório é o documento.** Os textos estão em `MENSAGENS`, no script. Escreva como se a mensagem fosse mais um F dele:

- Abertura no padrão "Olá, {Nome}! Tudo bem?" (o perfil do CN pode trocar por "Oi" ou tirar o "Tudo bem?"; o script aplica).
- "Vocês" para a empresa. Primeira pessoa do singular no WhatsApp ("me chamar por aqui"); "nós" e "nossa equipe" no e-mail, quando fala do trabalho do NTec.
- Frases curtas, parágrafos de uma ou duas linhas, uma ideia por parágrafo.
- Fecho de disponibilidade, como o documento faz ("Fico à disposição!", "Seguimos à disposição", "é só me chamar por aqui").
- Emoji só onde o documento usa: 🔗 antes de link e, no máximo, um 😊 no fim de WhatsApp.
- Quando uma frase do documento serve, reaproveite-a em vez de inventar outra. Ex.: "Se eu puder ajudar de alguma forma nesse processo, é só me chamar por aqui." serve para quase toda retomada.

**O conteúdo é o contexto.** Pelas fontes de `contexto.md`:

- Retome pelo concreto: o protótipo que ficou com eles, a proposta, a conversa com o TI, o organograma que ficou de vir, a data combinada.
- Um objetivo e no máximo um pedido por mensagem, fácil de responder (um sim, um não ou uma data).
- Nada de fato que não está nas fontes: nenhuma decisão atribuída ao cliente, nenhum prazo, preço, desconto ou case que não saiu da proposta ou do CN.

**O tom é o do CN.** `voz_autoral` e `exemplos_autorais` do perfil.

**O que não entra:** cobrança emocional ou culpa ("conforme meu último e-mail", "ainda não tive retorno"), urgência inventada, recapitulação longa da proposta, travessão (o script recusa) e marcador entre colchetes (o script recusa).

**Tamanho:** WhatsApp em até 6 linhas. E-mail só quando há documento, link ou formalidade (contrato, resumo de pendências da reunião); de resto, WhatsApp.

## Cadências sugeridas

Pontos de partida, ajustados ao que o CN pedir e ao calendário do card. Os dias são úteis, contados a partir de hoje, e vão em `apos_dias_uteis`. O limite de dois toques por dia vale para tudo.

| Caso | Toques |
|---|---|
| Parou de responder | 1. WhatsApp hoje, retomando pelo concreto. 2. E-mail em 3 dias, com o mesmo assunto da última conversa. 3. WhatsApp em 8 dias, com saída sem culpa ("se o momento não for agora, me avisa que retomo mais pra frente"). Depois do 3º, para: o próximo passo é decisão do CN. |
| Ficou de falar com TI ou superiores | O e-mail pós-Diag do documento (M1-F01) promete que o protótipo começa agora e que o próximo passo é o Aprofundamento. Se isso depende do aval de {área}, ele não serve: passe `--pular M1-F01` e escreva um e-mail livre de pós-Diag no mesmo esqueleto (agradecimento, o que entendemos, próximo passo real, disponibilidade). O WhatsApp do documento (M1-F02) sai normalmente. Mais um toque no meio do prazo que o cliente deu para responder (ele disse "2 semanas": em 5 dias úteis), oferecendo o que foi oferecido na reunião para ajudar na conversa com {área}. Se o CN já tem task para cobrar o retorno no fim do prazo, não crie outra. |
| Documento ou ponto combinado que não veio | WhatsApp no dia útil seguinte ao prazo combinado. E-mail 3 dias depois, se ainda não veio. |
| Pós-TouchPoint ou negociação | E-mail hoje com o que ficou combinado (pendência, quem leva, prazo) e WhatsApp avisando que o e-mail chegou. Se a próxima reunião já está marcada, a sala e a task dela, com `--reuniao "TouchPoint"` (ou o nome que o CN usa). |
| Envio do contrato | E-mail hoje com o contrato ou o link de assinatura (pendência de anexo) e WhatsApp avisando. |
| Assinatura pendente | WhatsApp em 2 dias. E-mail em 5. |
| Aquecimento pós-proposta com case | Um e-mail no meio do prazo até a reunião de próximos passos, com um case que o CN indicar. Nunca escolha o case sozinho. |
| Lead perdido | Só quando o CN pedir: um e-mail curto, com um motivo concreto para retomar (uma novidade, a mudança de momento que o próprio lead citou). |

## Como rodar

Escreva as mensagens num JSON e passe em `--livre`:

```json
[
  {"rotulo": "Retomada 1", "canal": "whatsapp", "texto": "Olá, Erich! Tudo bem?\n\n..."},
  {"rotulo": "Retomada 2", "canal": "email", "assunto": "Próximos passos | Projeto Montreal + Poli Júnior", "apos_dias_uteis": 3, "texto": "Olá, Erich!\n\n..."}
]
```

- `rotulo` vira o assunto da task (`WhatsApp - Retomada 1`, `E-mail - Retomada 2`), até 40 caracteres.
- `data` (AAAA-MM-DD) fixa o dia; `apos_dias_uteis` conta a partir de hoje; sem os dois, o primeiro dia útil com vaga. Se o dia já tem dois toques, o script empurra para o próximo com vaga ou, com `data` fixa, deixa de fora e diz por quê.
- Com próxima reunião marcada, nenhuma mensagem livre fica no dia dela ou depois.
- `--so-livre` quando as mensagens do documento do momento não se aplicam (pós-TouchPoint, contrato, retomada). Sem ele, as livres entram junto da cadência do documento (o caso do TI: pós-Diag do documento + retomada livre).

As mensagens livres seguem o mesmo caminho das outras: rascunho no Gmail para e-mail, segunda rodada com `--rascunho LIVRE-n=URL`, gravação no Pipedrive. Na resposta, mostre o texto inteiro de cada uma, marcada como escrita pela skill, porque não vem do documento e o CN precisa ler antes de enviar.
