# Contexto: de onde vem cada dado

Todo dado que entra numa mensagem vem de uma fonte desta lista. O cliente vai ler o texto e reconhecer, ou não, a própria reunião.

## Fontes, da mais forte para a mais fraca

1. **O que o CN escreveu no chat** ("a aprof ficou pra quinta 17h", "ela pediu o organograma").
2. **Nota de resumo no card** (getNotes com deal_id, mais recentes primeiro). O CN costuma colar ali o resumo da reunião, com data, participantes, link do Fathom, contexto, decisões e próximos passos. É a fonte mais rápida para o parágrafo autoral. Confira a data no topo: nota antiga descreve a reunião anterior.
3. **Fathom**: a gravação da última reunião (veja abaixo).
4. **Google Calendar**: data, horário e link do Meet da próxima reunião.
5. **Activities do card**: data da próxima reunião quando a agenda não traz.

**Ficha de AT em branco.** A nota "Ficha de AT" do card vem muitas vezes só com o enunciado do template, com respostas como `R: (ex. Gestora de obras...)`. Trecho que começa com `(ex.` é o exemplo do formulário, não informação do cliente. Nunca use.

## Última reunião (`--ultima-reuniao`)

A data da reunião que define o momento: a AT Diagnóstica no `pos-diag`, o Aprof no `pos-aprof`, a Apresentação de Proposta no `pos-proposta`. Vem do CN, da nota de resumo ou da gravação no Fathom. Na remarcação, é a mesma de antes.

## Fathom

1. get_identity, uma vez: dá o nome e o e-mail do CN (também serve para achar o perfil).
   - O CN colou um link do Fathom: get_recording_by_url. Link de compartilhamento (`/share/...`) de gravação de outra pessoa costuma voltar "not found or access denied"; nesse caso siga pelo passo 2, com a data da reunião.
2. list_meetings sem filtro de quem gravou (o colega que estava na call pode ter gravado), com `created_after` e `created_before` em volta da data da reunião. Fique com a reunião que tem convidado de domínio externo e cita a empresa ou o contato, no título ou nos convidados, sem acento e sem caixa, em qualquer posição ("Poli Júnior & Empresa" ou "Empresa & Poli Junior").
3. get_meeting_summary para o que foi decidido. get_meeting_transcript só quando o parágrafo autoral precisar das palavras exatas do cliente.

O título da gravação não decide o momento: decida pelo conteúdo. Mapeou processo e dores sem mostrar tela: Diagnóstica. Apresentou e validou protótipo: Aprofundamento. Apresentou escopo, prazo e preço: Proposta.

## Próxima reunião (`--proxima`, `--link-sala`)

list_events na agenda principal do CN, de hoje até 45 dias à frente, `timeZone: America/Sao_Paulo`. Vale o evento com horário marcado (`start.dateTime`, não dia inteiro), com convidado externo e que cita a empresa ou o contato. O link da sala é o Meet do evento (get_event se a listagem não trouxer).

- Nenhum evento: procure activity aberta do card que nomeia a reunião. Se ainda nada, pergunte ao CN a data e a hora. Sem resposta, rode sem `--proxima`: só os toques de hoje saem.
- Evento de dia inteiro sem convidados ("aprof 15h30") é lembrete do CN, não reunião: serve de pista para perguntar, não de data.
- Mais de um candidato: pergunte qual.
- A skill só lê a agenda. Nunca cria nem altera convite.

## Link do protótipo (`--link-prototipo`)

Do CN, da nota do card ou de uma task anterior da skill (o note do `WhatsApp - Pós AT Aprof.` traz o link). Sem ele, o texto sai com o marcador e uma pendência.

## Parágrafo autoral (`--paragrafo`)

É o único trecho escrito pelo Claude, e só existe na sugestão 2 dos e-mails pós-Diag e pós-Aprof. Também o texto do pedido no M2-F05 (`--pedido`).

- **Pós-Diag:** completa a frase "nosso principal foco será ajudar vocês a resolver:". Um parágrafo de 1 a 3 frases, começando como sintagma nominal, como no exemplo do documento ("A falta de integração entre os processos, gerando retrabalho, pouca visibilidade das informações e dificuldade para acompanhar os indicadores da operação.").
- **Pós-Aprof:** completa "Nosso principal alinhamento durante a reunião foi:". Ajustes, validações e decisões da reunião, de 1 a 3 frases.
- **Pedido (M2-F05):** uma ou duas frases objetivas com o que falta, para substituir "[Descrever objetivamente a informação necessária.]". Escreva como afirmação, não como pergunta, porque a pergunta já vem na frase seguinte do modelo ("Assim que tiverem essa informação, conseguem me encaminhar..."). Ex.: "Precisamos do organograma da equipe de manutenção para fechar os perfis de acesso do sistema."

Regras:

- Só fatos que estão numa das fontes acima. Dor que o cliente não disse, decisão que ninguém tomou e hipótese de briefing não entram.
- Use os nomes de sistema, área e processo como o cliente falou.
- Sem adjetivo de venda e sem travessão.
- Escreva na voz do perfil do CN (`voz_autoral` e `exemplos_autorais`). O perfil decide o tom; as fontes decidem o conteúdo.
- Se as fontes não dão substância, não passe `--paragrafo`: o script usa a sugestão 1, que não precisa dele.
- Mostre o parágrafo ao CN na resposta, na seção do e-mail, para ele conferir.
