# Pipedrive

IDs conferidos em 25/11/2026. Se o Pipedrive recusar algum ID, rode getAccountContext, corrija na chamada e avise o CN para atualizar este arquivo.

## Funil e etiqueta

Pipeline 6, "Vendas (CN)". Só vale card com etiqueta NTec (`label_ids` contém 34): o funil é de todos os núcleos (NDados 32, NI 286 e outros).

| Etapa | ID | Momento da skill | Próxima reunião |
|---|---|---|---|
| AT Diag. Agendada | 108 | fora (é da `criar-card`) | AT Diagnóstica |
| AT Diag. Realizada | 31 | `pos-diag` | AT Aprofundamento |
| AT Aprof. Marcada | 33 | `pos-diag` | AT Aprofundamento |
| Proposta Agendada | 34 | `pos-aprof` | Apresentação de Proposta |
| Negociação | 35 | `pos-proposta` | Próximos passos |
| Aprov. Verbal (Contrato) | 36 | `pos-proposta` | Próximos passos |

A etapa é um ponto de partida, não a prova. Card esquecido numa etapa velha é comum. Quando a última reunião realizada (Fathom, nota do card, o que o CN disse) contradiz a etapa, vale a reunião, e a divergência vai para Avisos. A skill não move o card de etapa.

Link do card: `https://polijunior.pipedrive.com/deal/{id}`

## Achar o card

1. searchDeals pelo radical do nome da empresa (sem Ltda, S.A., Grupo, Brasil), status open.
2. Fique com os de pipeline 6 e etiqueta NTec (getDeal com include_labels quando a busca não trouxer).
3. Dono: `owner_id` igual ao `pipedrive_user_id` do perfil do CN. Card de outro dono: leia para montar contexto, mas não escreva nada nele; entregue os textos no chat e diga de quem é o card.
4. Mais de um card NTec aberto do CN na mesma empresa: desempate pelo contato do card (person_id) contra quem estava na última reunião. Persistindo o empate, pergunte.
5. Títulos com prefixo (`[Internúcleos NDados]`, `[Feat. NCon]`, `[Hacka 26.2 - Lais]`, `[Fidelização]`) são normais. Quando há card do mesmo contato em outro núcleo (searchDeals pelo nome da pessoa), leia as notas e as tasks dele também: se o CN do outro núcleo ficou com uma parte da comunicação (criar o grupo, mandar as opções de horário), a cadência não repete essa parte, e a resposta avisa para alinhar com ele quem manda o quê.

## Contato

- `person_id` do card → getPerson: nome (o primeiro nome vai em `--nome`) e e-mail principal (destinatário do rascunho).
- Card sem pessoa (acontece): pergunte ao CN o nome e o e-mail do contato. Não grave pessoa nova; a task vai sem `participants`.
- Mais de um interlocutor no WhatsApp: `--nome "Ana e João"` ou, no grupo do pós-Diag, `--grupo`.

## Tipos de task

`email`, `mensagem`, `meeting`, `reuniao_remarcada` são os que a skill usa. Existem também `call`, `task`, `deadline`, `ligacao_outbound`, que a skill não cria.

O CN costuma criar tasks à mão como `call`, com assunto curto (`fup`, `fup 2`, `cobrar respostas`, `touchpoint - 10h`) e às vezes um recado no note. Essas tasks são dele: a skill não edita, não conclui, não apaga. Lista as abertas na resposta, para ele decidir.

O campo `outcome` (Resultado) fica vazio: quem envia registra o desfecho.

## Campos do addActivity

- `deal_id`, `org_id` (do card), `participants: [{person_id, primary: true}]` (se o card tem pessoa) e `owner_id` = `pipedrive_user_id` do perfil.
- `type`, `subject`, `due_date` e `note`, exatamente como o script devolve.
- Não envie `due_time` nem `duration`: as tasks valem o dia inteiro. O horário que importa já está no assunto (`WhatsApp - Sala 16h57`, `AT Aprofundamento - 17h`).
- `note` é HTML: quebra de linha é `<br>`. O script já entrega assim.

## Tasks da skill

O começo do assunto identifica cada task que a skill cria. É por ele que uma rodada nova acha a task da rodada anterior.

| Chave | Assunto | Tipo |
|---|---|---|
| M1-F01 / M2-F01 | `E-mail - Pós AT Diag.` / `E-mail - Pós AT Aprof.` | email |
| M3-F01 | `E-mail - Champions Letter` | email |
| M1-F02 / M2-F02 / M3-F02 | `WhatsApp - Pós AT Diag.` / `WhatsApp - Pós AT Aprof.` / `WhatsApp - Pós Proposta` | mensagem |
| M1-F03 (+F04) / M2-F03 | `WhatsApp - Véspera AT Aprof., horário {h}` / `WhatsApp - Véspera Proposta, horário {h}` | mensagem |
| M2-F05 | `WhatsApp - Pedido de informação` | mensagem |
| M3-F03 | `WhatsApp - Disponibilidade` | mensagem |
| M1-F05 / M2-F04 / M3-F04 | `WhatsApp - Sala {h − 3 min}` | mensagem |
| LIVRE-n | `WhatsApp - {rótulo}` / `E-mail - {rótulo}` (casos sem modelo, `sem-modelo.md`) | mensagem / email |
| REUNIAO | `AT Aprofundamento - {h}` / `Apresentação de Proposta - {h}` / `Próximos passos - {h}`, ou `{--reuniao} - {h}` (ex.: `TouchPoint - 10h`) | meeting (na remarcação, reuniao_remarcada) |

Mensagem livre se reconhece pelo assunto inteiro: numa rodada nova, task aberta com o mesmo assunto é atualizada, não duplicada.

As tasks da `criar-card` (`... - TP1`, `TP3`, `TP4`, `AT - 9h30 @hunter`) são de outra cadência: não toque.

## Antes de gravar

getActivities com `deal_id` (sem filtro de done) e compare pelo começo do assunto:

- Task da skill **aberta** com a mesma chave: updateActivity com `subject`, `due_date` e `note` novos. Não crie outra.
- Task da skill **concluída**: já foi enviada. Passe a chave em `--pular` e rode o script de novo.
- **Reunião**: se já existe activity aberta no dia da próxima reunião que nomeia o encontro (tipo meeting, ou assunto como `aprof 17h`, `proposta 11h`, `touchpoint - 10h`), não crie a task REUNIAO e diga qual activity já marca a reunião.
- O conector não apaga task. Se uma correção exigir apagar uma, diga em Avisos qual apagar à mão, com o link do card.

## Falha no meio

Guarde cada ID que voltar. Se uma escrita falhar, pare e diga o que já foi criado (IDs de tasks e de rascunhos) para a próxima tentativa não duplicar.
