# cadencia-ntec

Skill do Claude que monta a cadência de follow-up dos cards do funil **Vendas (CN)** do NTec, o Núcleo de Tecnologia da Poli Júnior.

Depois de cada reunião com um lead, o Coordenador de Negócios (CN) precisa mandar a sequência de mensagens do documento **"Cadências, mensagens e follow-up | CNs"**: o pós-reunião, os aquecimentos e o "já estou na sala" antes da próxima reunião. A skill monta essa sequência para um card e grava cada toque como task no Pipedrive, no dia certo, com o texto pronto dentro.

O CN abre a task no dia e só envia:

- **WhatsApp:** o texto está no note da task.
- **E-mail:** o note traz o link do rascunho já montado no Gmail dele, com assinatura.
- **Próxima reunião:** vira uma task própria, como `AT Aprofundamento - 17h`.

Nada é enviado ao cliente pela skill. Quem revisa e envia é sempre o CN.

---

## Sumário

1. [O que a skill faz](#o-que-a-skill-faz)
2. [Instalação](#instalação)
3. [Como usar](#como-usar)
4. [O funil e os momentos](#o-funil-e-os-momentos)
5. [A cadência de cada momento](#a-cadência-de-cada-momento)
6. [Regras de datas](#regras-de-datas)
7. [Como as mensagens são montadas](#como-as-mensagens-são-montadas)
8. [Casos sem modelo no documento](#casos-sem-modelo-no-documento)
9. [Perfis dos CNs](#perfis-dos-cns)
10. [O que a skill grava no Pipedrive](#o-que-a-skill-grava-no-pipedrive)
11. [Formato da resposta](#formato-da-resposta)
12. [Garantias de segurança](#garantias-de-segurança)
13. [Estrutura do repositório](#estrutura-do-repositório)
14. [O script](#o-script)
15. [Manutenção](#manutenção)
16. [Problemas comuns](#problemas-comuns)

---

## O que a skill faz

1. **Identifica o CN** pelo Fathom e carrega o perfil de estilo dele.
2. **Acha o card** no Pipedrive (pipeline 6, etiqueta NTec) e confere que o dono é o CN.
3. **Define o momento** pela etapa do card, conferida contra a última reunião realizada.
4. **Junta o contexto:** contato, data da última reunião, data, hora e link da próxima (Google Calendar), link do protótipo, nota de resumo do card e gravação do Fathom.
5. **Escreve só o que o documento deixa em aberto:** o parágrafo de cenário ou alinhamento e o texto de pedido de informação. Nos casos sem modelo, escreve as mensagens inteiras.
6. **Roda o script**, que escolhe as mensagens do documento, troca os marcadores, aplica o perfil do CN e calcula as datas.
7. **Cria os rascunhos** no Gmail do CN para cada e-mail.
8. **Grava as tasks** no Pipedrive, atualizando as que já existem em vez de duplicar.
9. **Responde** com uma tabela do que foi criado, pendências e avisos.

---

## Instalação

### Pré-requisitos

- Claude.ai (ou Claude Code) com execução de código habilitada.
- Conectores ligados na conta do próprio CN:
  - **Pipedrive** (leitura e escrita de tasks);
  - **Fathom** (leitura de gravações);
  - **Google Calendar** (leitura da próxima reunião);
  - **Gmail** (criação de rascunhos).
- Um perfil do CN em `cadencia-ntec/references/perfis/` (veja [Perfis dos CNs](#perfis-dos-cns)). Sem perfil, a skill faz o cadastro no chat.

### Passo a passo

1. Baixe este repositório (Code > Download ZIP) ou clone.
2. Compacte **só a pasta `cadencia-ntec/`** em um .zip.
3. No Claude: **Configurações > Capacidades > Skills > Upload skill** e escolha o .zip.
4. Ative a skill.
5. Desative a antiga `follow-up-lead-ntec`, se ainda estiver instalada: as duas disputam os mesmos pedidos.

### Testar

Peça: *"simula a cadência da {empresa}"*. No modo simulação a skill lê tudo e mostra o que faria, sem gravar nada.

---

## Como usar

A skill é acionada por linguagem natural, sem comando. Exemplos:

| Você diz | O que acontece |
|---|---|
| "acabei a AT da ICL, a aprof ficou pra segunda 17h" | Cadência pós-Diag até o Aprofundamento |
| "apresentei a proto pra Mangels hoje, proposta dia 03/12 às 15h" | Cadência pós-Aprof até a Apresentação de Proposta |
| "apresentei a proposta da Motiva, próximos passos dia 09/12" | Champions Letter e cadência até a reunião de próximos passos |
| "monta a cadência da {empresa}" | A skill descobre o momento sozinha |
| "falta ela mandar o organograma" | Inclui o WhatsApp de pedido de informação |
| "a aprof da Mangels foi para quinta 10h" | Remarcação: move véspera, sala e reunião |
| "o lead da CPFL sumiu" | Retomada (caso sem modelo) |
| "ele vai falar com o TI antes de marcar a aprof" | Pós-Diag adaptado + toque de apoio (caso sem modelo) |
| "simula a cadência da {empresa}" | Mostra tudo, não grava nada |

Ela **não** é usada para:

- card em **AT Diag. Agendada** ou **Ficha de AT** → skill `criar-card`;
- visão do funil inteiro → `varredura-funil-ntec`;
- preparar uma reunião → `briefing-lead-spin`.

---

## O funil e os momentos

Pipeline 6, "Vendas (CN)". Só vale card com a etiqueta **NTec** (id 34).

| Etapa | ID | Momento | Próxima reunião |
|---|---|---|---|
| AT Diag. Agendada | 108 | fora (é da `criar-card`) | AT Diagnóstica |
| AT Diag. Realizada | 31 | `pos-diag` | AT Aprofundamento |
| AT Aprof. Marcada | 33 | `pos-diag` | AT Aprofundamento |
| Proposta Agendada | 34 | `pos-aprof` | Apresentação de Proposta |
| Negociação | 35 | `pos-proposta` | Próximos passos |
| Aprov. Verbal (Contrato) | 36 | `pos-proposta` | Próximos passos |

A etapa é só o ponto de partida. Card esquecido numa etapa antiga é comum, então vale a última reunião realizada (Fathom, nota do card, o que o CN disse). Quando as duas divergem, a skill avisa. Ela não move o card de etapa.

---

## A cadência de cada momento

As chaves seguem o documento: **M1** é o momento pós AT Diagnóstica, **M2** o pós Aprofundamento, **M3** o pós Proposta; **F01, F02...** são as mensagens de cada momento.

### Pós AT Diagnóstica (`pos-diag`)

| Toque | Canal | Quando |
|---|---|---|
| M1-F01 E-mail pós-Diag (sugestão 1 ou 2) | E-mail | hoje |
| M1-F02 WhatsApp de abertura de canal (individual ou grupo) | WhatsApp | hoje |
| M1-F03 Véspera do Aprofundamento | WhatsApp | dia útil anterior à reunião |
| M1-F04 Aquecimento 2 (na mesma task da véspera) | WhatsApp | só se o Aprof for mais de 4 dias depois do Diag |
| M1-F05 "Já estou na sala" | WhatsApp | dia da reunião |
| `AT Aprofundamento - {h}` | reunião | dia da reunião |

### Pós Aprofundamento (`pos-aprof`)

| Toque | Canal | Quando |
|---|---|---|
| M2-F01 E-mail pós-Aprof com link do protótipo (sugestão 1 ou 2) | E-mail | hoje |
| M2-F02 WhatsApp espelho com o link | WhatsApp | hoje |
| M2-F05 Pedido de informação complementar | WhatsApp | só se faltar algo; primeiro dia livre |
| M2-F03 Véspera da Proposta | WhatsApp | dia útil anterior à reunião |
| M2-F04 "Já estou na sala" | WhatsApp | dia da reunião |
| `Apresentação de Proposta - {h}` | reunião | dia da reunião |

### Pós Apresentação de Proposta (`pos-proposta`)

| Toque | Canal | Quando |
|---|---|---|
| M3-F01 Champions Letter (com a proposta em anexo) | E-mail | hoje |
| M3-F02 WhatsApp espelho | WhatsApp | hoje |
| M3-F03 Disponibilidade | WhatsApp | 2 dias úteis antes, só se a reunião estiver a 5+ dias |
| M3-F04 "Já estou na sala" | WhatsApp | dia da reunião |
| `Próximos passos - {h}` | reunião | dia da reunião |

Sem próxima reunião marcada, só os toques de hoje saem. Aquecimentos, sala e a task da reunião entram quando a data existir.

---

## Regras de datas

- **Pós-reunião sai sempre.** O documento pede o envio até 1 ou 2 horas depois da reunião, então o ideal é rodar no mesmo dia. Se a reunião foi antes, o pós sai hoje com o "hoje" do texto ajustado:
  - 1 dia antes: "conversa de ontem", "apresentado ontem";
  - 2 a 6 dias: "conversa de sexta-feira", "apresentado na sexta-feira";
  - 7 dias ou mais: "conversa do dia 13/11".

  Antes, a skill procura no Gmail se o CN já mandou e-mail ao contato desde a reunião. Se já mandou, aquele toque fica de fora.
- **Véspera** no dia útil anterior à reunião. Reunião de segunda tem véspera na sexta, e o "amanhã" do texto vira "segunda-feira".
- **Sala** no dia da reunião, com o horário menos 3 minutos no assunto (`WhatsApp - Sala 16h57`).
- **Até dois toques por dia.** O CN abre dois canais com o cliente (e-mail e WhatsApp), então dois toques no mesmo dia podem acontecer; mais que isso é demais.
  - Cada mensagem enviada conta um toque.
  - O pós-reunião (e-mail + WhatsApp) ocupa os dois do dia.
  - Véspera com aquecimento 2 conta um só (é uma conversa).
  - Sala e task da reunião não contam.
  - Prioridade quando não cabe: pós-reunião, véspera, disponibilidade, pedido.
- **Nada no passado nem no fim de semana.** Próxima reunião em sábado, domingo ou já passada é erro de entrada.
- Todas as tasks valem o **dia inteiro** (sem horário no Pipedrive). O horário que importa está no assunto.

---

## Como as mensagens são montadas

### Os textos do documento são fixos

Os textos do documento ficam dentro do script, conferidos por uma impressão digital (hash). Se alguém alterar um texto sem atualizar o hash, o script para. Isso garante que o core das mensagens nunca muda por acidente.

O Claude **nunca redigita** uma mensagem do documento: o script troca os marcadores e devolve o texto pronto.

### Marcadores

| Marcador | Vira |
|---|---|
| `[Nome]` | primeiro nome do contato (ou "Ana e João") |
| `[Empresa]` | nome da empresa |
| `[Nome e Sobrenome]` | como o CN se apresenta no WhatsApp (perfil) |
| `[horário]` | horário da próxima reunião (17h, 16h30) |
| `[Dia da semana]` | dia da próxima reunião (quinta-feira) |
| `[data]`, `[dia]` | próxima reunião por extenso (quinta-feira, 03/12, às 15h) |
| `[Link]` | link do Meet da próxima reunião |
| `[LINK DO PROTÓTIPO]` | link do protótipo |
| parágrafo autoral | escrito pelo Claude a partir da reunião |
| pedido de informação | escrito pelo Claude a partir do que falta |

Link que não foi encontrado **fica visível no texto** (`LINK DA SALA DA REUNIÃO`, `LINK DO PROTÓTIPO`) e vira pendência. Um link inventado iria para o cliente; um marcador visível, o CN resolve.

### Sugestão 1 ou sugestão 2

Os e-mails pós-Diag e pós-Aprof têm duas versões no documento. A sugestão 2 tem um parágrafo que muda de lead para lead (cenário no pós-Diag, alinhamento no pós-Aprof).

- Com substância na reunião para esse parágrafo: sugestão 2.
- Sem: sugestão 1.
- O perfil do CN pode fixar uma das duas.

### Parágrafo autoral

É o único trecho dos e-mails do documento escrito pelo Claude. Regras:

- só fatos que estão na nota do card, no Fathom ou no que o CN disse;
- nomes de sistema e área como o cliente falou;
- sem adjetivo de venda, sem travessão;
- na voz do perfil do CN;
- sempre mostrado na resposta, para o CN conferir.

Fontes, da mais forte para a mais fraca: o que o CN escreveu no chat, a nota de resumo no card, o Fathom, o Google Calendar e as activities do card. A **Ficha de AT** costuma vir em branco, só com os exemplos do template ("(ex. Gestora de obras...)"); trecho que começa com `(ex.` é ignorado.

---

## Casos sem modelo no documento

O documento cobre o caminho feliz. Para o resto, a skill escreve as mensagens com base no repertório dele (mesma abertura, "vocês", frases curtas, fecho de disponibilidade, frases reaproveitadas quando servem) e no contexto do card, sempre retomando por algo concreto.

| Caso | Cadência sugerida |
|---|---|
| Lead parou de responder | WhatsApp hoje · e-mail em 3 dias úteis · WhatsApp em 8 com saída sem culpa. Depois do 3º, para. |
| Ficou de falar com o TI ou superiores | E-mail pós-Diag adaptado (o do documento promete protótipo e Aprof) · WhatsApp do documento · um toque de apoio no meio do prazo que o cliente deu |
| Documento ou ponto combinado que não veio | WhatsApp no dia seguinte ao prazo · e-mail 3 dias depois |
| Pós-TouchPoint ou negociação | E-mail com o que ficou combinado + WhatsApp avisando · sala e reunião com nome livre (`TouchPoint - 10h`) |
| Envio do contrato | E-mail com o contrato + WhatsApp avisando |
| Assinatura pendente | WhatsApp em 2 dias · e-mail em 5 |
| Aquecimento pós-proposta com case | Um e-mail no meio do prazo, com o case que o CN indicar |
| Lead perdido | Só a pedido do CN: um e-mail curto com motivo concreto |

Essas mensagens passam pelo mesmo script: recebem o perfil, as datas e o limite de toques. O script recusa travessão e marcador esquecido. Na resposta, aparecem **inteiras**, marcadas como "Escrita pela skill", porque o CN precisa ler antes de enviar.

Se um F do documento resolve, a skill usa o F.

---

## Perfis dos CNs

Cada CN tem um arquivo `cadencia-ntec/references/perfis/{nome.sobrenome}.json`:

```json
{
  "nome": "Augustus Rivas",
  "usuario": "augustus.rivas",
  "email": "augustus.rivas@polijunior.com.br",
  "pipedrive_user_id": 26429856,
  "apresentacao_whats": "Augustus Rivas",
  "estilo": {
    "saudacao": "manter",
    "tudo_bem": true,
    "emoji": true,
    "fecho_email": null,
    "sugestao_pos_diag": "auto",
    "sugestao_pos_aprof": "auto"
  },
  "voz_autoral": "Frases curtas, sujeito na frente, verbo simples.",
  "exemplos_autorais": []
}
```

### Ajustes de estilo

A personalização é **controlada**: muda o jeito de abrir e fechar, nunca o core do texto.

| Ajuste | Valores | Efeito |
|---|---|---|
| `saudacao` | `manter`, `Olá`, `Oi` | Primeira palavra da abertura |
| `tudo_bem` | `true`, `false` | Tira o "Tudo bem?" da abertura |
| `emoji` | `true`, `false` | Tira 🔗, 😊 e 😄 |
| `fecho_email` | `null` ou uma linha curta | Troca a despedida dos e-mails que terminam só em despedida |
| `sugestao_pos_diag` | `auto`, `1`, `2` | Fixa a sugestão do e-mail pós-Diag |
| `sugestao_pos_aprof` | `auto`, `1`, `2` | Fixa a sugestão do e-mail pós-Aprof |
| `voz_autoral` | texto | Tom dos parágrafos e das mensagens escritas pela skill |
| `exemplos_autorais` | até 3 parágrafos | Referência de tom (nunca de conteúdo) |

Qualquer outra chave em `estilo` faz o script parar com erro, para ninguém mudar o texto do documento por um perfil.

### Cadastrar um CN novo

Na primeira vez que um CN sem perfil usa a skill, ela:

1. pega nome e e-mail do Fathom;
2. pede o nome de uma empresa com card dele e lê o ID de usuário no Pipedrive;
3. pergunta o estilo (Oi ou Olá, "Tudo bem?", emoji, despedida própria);
4. pede um ou dois parágrafos de e-mails que ele já mandou, para a voz autoral;
5. usa o perfil na sessão e devolve o arquivo JSON.

Para o perfil ficar permanente: abra um PR adicionando o arquivo em `cadencia-ntec/references/perfis/` e reinstale a skill.

---

## O que a skill grava no Pipedrive

### Assuntos das tasks

O começo do assunto identifica cada task da skill. É por ele que uma rodada nova acha a task anterior e atualiza em vez de duplicar.

| Task | Assunto | Tipo |
|---|---|---|
| E-mail pós-reunião | `E-mail - Pós AT Diag.` · `E-mail - Pós AT Aprof.` · `E-mail - Champions Letter` | email |
| WhatsApp pós-reunião | `WhatsApp - Pós AT Diag.` · `WhatsApp - Pós AT Aprof.` · `WhatsApp - Pós Proposta` | mensagem |
| Véspera | `WhatsApp - Véspera AT Aprof., horário 17h` · `WhatsApp - Véspera Proposta, horário 15h` | mensagem |
| Pedido | `WhatsApp - Pedido de informação` | mensagem |
| Disponibilidade | `WhatsApp - Disponibilidade` | mensagem |
| Sala | `WhatsApp - Sala 16h57` | mensagem |
| Mensagem escrita pela skill | `WhatsApp - {rótulo}` · `E-mail - {rótulo}` | mensagem / email |
| Próxima reunião | `AT Aprofundamento - 17h` · `Apresentação de Proposta - 15h` · `Próximos passos - 10h` | meeting (remarcação: reuniao_remarcada) |

### Campos

- `deal_id`, `org_id`, contato como participante principal, `owner_id` = CN.
- `note` em HTML: o texto do WhatsApp, ou o link "Abrir rascunho no Gmail" seguido do texto do e-mail.
- Sem `due_time` nem `duration`.
- `outcome` (Resultado) fica vazio: quem envia registra o desfecho.

### O que a skill não toca

- Tasks criadas à mão pelo CN (`fup`, `cobrar material`, `touchpoint - 10h`): só lê e lista na resposta.
- Tasks da `criar-card` (`TP1`, `TP3`, `TP4`, `AT - 9h30 @hunter`).
- Card de outro dono: lê para contexto, entrega os textos no chat, não grava.
- Etapa do card, Resultado das tasks, done.
- Nada é apagado (o conector nem permite).

### Card com outro núcleo

Quando o mesmo contato tem card em outro núcleo (`[Feat. NCon]`, `[Internúcleos ...]`), a skill lê o outro card também. Se o CN do outro núcleo ficou com uma parte da comunicação (criar o grupo, mandar horários), a cadência não repete essa parte e avisa para alinhar.

---

## Formato da resposta

```
**{Empresa} - {Contato}** · [abrir card](https://polijunior.pipedrive.com/deal/{id})

| Momento         | Pós AT Diag. → AT Aprofundamento         |
| Próxima reunião | AT Aprofundamento - 17h · segunda, 30/11 |
| Sala            | {link do Meet, ou "não encontrada"}      |
| Perfil          | {nome do CN}                             |

| Canal    | Task                                       | Data        | No card                    |
| E-mail   | E-mail - Pós AT Diag.                      | qua, 25/11  | criada · [rascunho](...)   |
| WhatsApp | WhatsApp - Pós AT Diag.                    | qua, 25/11  | criada                     |
| WhatsApp | WhatsApp - Véspera AT Aprof., horário 17h  | sex, 27/11  | atualizada                 |
| WhatsApp | WhatsApp - Sala 16h57                      | seg, 30/11  | criada                     |
| —        | AT Aprofundamento - 17h                    | seg, 30/11  | já existia (`aprof 17h`)   |

Parágrafo do e-mail: "..."
Pendências: ...
Avisos: ...
```

No modo simulação, a resposta abre com "SIMULAÇÃO: nada foi gravado" e mostra o texto completo de cada task e de cada e-mail.

---

## Garantias de segurança

1. **Nada é enviado ao cliente.** Só tasks e rascunhos.
2. **Texto do documento intocável**, conferido por hash.
3. **Zero invenção:** nome, data, link e fato da reunião vêm de fonte verificável.
4. **Só no card do CN.**
5. **Cria e atualiza; nunca apaga.**
6. **Modo simulação** com "simula" ou "testa".
7. **Falha no meio:** a skill para e lista o que já criou (IDs), para a próxima tentativa não duplicar.

---

## Estrutura do repositório

```
README.md                      este arquivo (para humanos)
cadencia-ntec/                 a skill (é esta pasta que vai no .zip)
├── SKILL.md                   instruções da skill: fluxo, regras, formato, exemplos
├── scripts/
│   └── montar_cadencia.py     textos do documento, datas, perfil e tasks
└── references/
    ├── pipedrive.md           funil, etapas, assuntos das tasks, regras de gravação
    ├── contexto.md            fontes, Fathom, agenda, parágrafo autoral
    ├── cadencia.md            regras de datas, marcadores e sugestões
    ├── sem-modelo.md          casos sem modelo: como escrever e cadências sugeridas
    ├── perfis.md              campos do perfil e cadastro de CN novo
    └── perfis/
        ├── _modelo.json       modelo vazio
        └── augustus.rivas.json
```

A skill segue o guia oficial da Anthropic ("The Complete Guide to Building Skills for Claude"): `SKILL.md` com frontmatter, detalhes em `references/` (carregados só quando preciso) e a parte determinística num script.

---

## O script

`cadencia-ntec/scripts/montar_cadencia.py` não tem dependências além do Python 3. A skill roda o script sozinha, mas ele também funciona direto no terminal:

```bash
python3 cadencia-ntec/scripts/montar_cadencia.py \
  --momento pos-diag \
  --perfil cadencia-ntec/references/perfis/augustus.rivas.json \
  --nome Júlio --empresa ICL \
  --ultima-reuniao 2026-11-25 \
  --proxima "2026-11-30 17:00" \
  --link-sala https://meet.google.com/abc-defg-hij
```

### Argumentos

| Argumento | Para quê |
|---|---|
| `--momento` | `pos-diag`, `pos-aprof` ou `pos-proposta` |
| `--perfil` | arquivo JSON do CN |
| `--nome`, `--empresa` | contato e empresa |
| `--ultima-reuniao` | data da reunião que define o momento (AAAA-MM-DD) |
| `--proxima` | próxima reunião (AAAA-MM-DD HH:MM, horário de Brasília) |
| `--link-sala`, `--link-prototipo` | links |
| `--paragrafo` | parágrafo autoral (sugestão 2) |
| `--pedido`, `--pedido-objeto` | pedido de informação (M2-F05): texto e `solucao`, `proposta` ou `prototipo` |
| `--grupo` | WhatsApp pós-Diag na versão de grupo |
| `--spoiler` | aquecimento 2 com spoiler do protótipo |
| `--pular` | chaves já enviadas (ex.: `M1-F01,M1-F02`) |
| `--pular-hoje` | chaves que o CN já mandou hoje (pulam e contam no limite do dia) |
| `--remarcacao` | só véspera, sala e reunião, com a reunião como Reunião Remarcada |
| `--livre` | JSON com mensagens escritas para casos sem modelo |
| `--so-livre` | não gera mensagens do documento, só as livres, a sala e a reunião |
| `--reuniao` | nome da próxima reunião fora do padrão (ex.: `TouchPoint`) |
| `--rascunho CHAVE=URL` | link do rascunho criado no Gmail (pode repetir) |
| `--agora` | data e hora de referência, para testes |

### Formato do `--livre`

```json
[
  {
    "rotulo": "Retomada 1",
    "canal": "whatsapp",
    "texto": "Olá, Erich! Tudo bem?\n\n..."
  },
  {
    "rotulo": "Retomada 2",
    "canal": "email",
    "assunto": "Próximos passos | Projeto Montreal + Poli Júnior",
    "apos_dias_uteis": 3,
    "texto": "Olá, Erich!\n\n..."
  }
]
```

`data` (AAAA-MM-DD) fixa o dia; `apos_dias_uteis` conta a partir de hoje; sem os dois, o primeiro dia útil com vaga.

### Saída

JSON com `tasks` (chave, canal, tipo, assunto, data, note em HTML e, nos e-mails, assunto e corpo do rascunho), `nao_criadas` (com motivo), `pendencias`, `avisos` e `proxima`. Erro de entrada devolve `{"erro": ...}` com código 2; erro de texto ou perfil, `{"erro_interno": ...}` com código 3.

---

## Manutenção

### Mudou o documento de cadências

1. Edite o texto em `MENSAGENS`, no script, mantendo os marcadores entre colchetes.
2. Recalcule o hash e atualize `HASH_MENSAGENS`:
   ```bash
   python3 -c "import importlib.util,hashlib;s=importlib.util.spec_from_file_location('m','cadencia-ntec/scripts/montar_cadencia.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(hashlib.sha256(m.MENSAGENS.encode()).hexdigest())"
   ```
3. Suba a versão em `metadata.version` no `SKILL.md`.
4. Reinstale a skill.

### Mudou um ID no Pipedrive

Etapas, etiqueta e tipos de task estão em `references/pipedrive.md`. Se o Pipedrive recusar um ID, a skill avisa; corrija o arquivo e reinstale.

### Mudou o limite de toques

Constante `LIMITE_TOQUES_DIA` no script (hoje, 2).

### Novo perfil ou ajuste de perfil

PR em `cadencia-ntec/references/perfis/`. Os valores aceitos estão em [Ajustes de estilo](#ajustes-de-estilo).

---

## Problemas comuns

| Sintoma | Causa | O que fazer |
|---|---|---|
| "a próxima reunião cai num sábado" | Data errada | Confirme a data e rode de novo |
| "o e-mail pós-Aprof cita a data da apresentação de proposta" | Falta `--proxima` | Informe a data da próxima reunião |
| `erro_interno` sobre os textos | O hash não bate com `MENSAGENS` | Alguém mudou um texto: atualize texto e hash juntos |
| `erro_interno` sobre o perfil | Campo faltando ou ajuste fora da tabela | Corrija o JSON do perfil |
| Mensagem livre recusada | Travessão, marcador entre colchetes ou e-mail sem assunto | Reescreva a mensagem |
| "nada gravado: o card é de {fulano}" | Card de outro CN | A skill só grava no card do próprio CN |
| Link do Fathom não abre | Link de compartilhamento de gravação de outra pessoa | A skill usa a nota de resumo do card ou busca a gravação pela data |
| Rascunho sem destinatário | Contato sem e-mail no Pipedrive | Complete o e-mail da pessoa no card |
| Pós-reunião não saiu | Já havia e-mail ao contato desde a reunião | É o esperado; rode com `--pular` vazio se quiser forçar |
| Etapa do card não bate | Card esquecido na etapa antiga | A skill segue a última reunião e avisa; mova o card à mão |

---

Mantenedor: Augustus Rivas (NTec · Poli Júnior).
