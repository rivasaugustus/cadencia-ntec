# Perfis dos CNs

Cada CN que usa a skill tem um arquivo `references/perfis/{nome.sobrenome}.json`. O perfil diz quem é o CN (para achar os cards dele e gravar as tasks no nome dele) e como ele fala, dentro dos limites que mantêm o texto do documento.

## Campos

| Campo | Para quê |
|---|---|
| `nome` | Nome do CN, como aparece na resposta. |
| `usuario` | nome.sobrenome, igual ao nome do arquivo. |
| `email` | E-mail Poli Júnior. É por ele que a skill acha o perfil (comparado ao e-mail do get_identity do Fathom). |
| `pipedrive_user_id` | ID de usuário no Pipedrive: dono dos cards e `owner_id` das tasks. |
| `apresentacao_whats` | Como ele se apresenta no WhatsApp pós-Diag ("[Nome e Sobrenome] do Núcleo de Tecnologia da Poli Júnior aqui"). |
| `estilo` | Ajustes controlados, abaixo. |
| `voz_autoral` | Uma ou duas frases sobre como ele escreve. Vale só para os parágrafos autorais e o pedido. |
| `exemplos_autorais` | Até 3 parágrafos reais dele, de e-mails já enviados. Referência de tom, nunca de conteúdo. |

## Ajustes de estilo

O script aplica estes ajustes, e só estes. Qualquer outra chave em `estilo` faz o script parar com `erro_interno`.

| Ajuste | Valores | Efeito |
|---|---|---|
| `saudacao` | `manter`, `Olá`, `Oi` | Troca a primeira palavra da abertura ("Olá, Fulana!" ↔ "Oi, Fulana!"). `manter` deixa como no documento, que usa os dois. |
| `tudo_bem` | `true`, `false` | `false` tira o "Tudo bem?" da abertura. |
| `emoji` | `true`, `false` | `false` tira 🔗, 😊 e 😄. |
| `fecho_email` | `null` ou uma linha curta (até 40 caracteres) | Troca a despedida dos e-mails cuja última linha é só despedida ("Nos vemos em breve!", "Até breve!", "Fico à disposição!", "Um grande abraço!"). Não mexe em despedida com data, como "Até quinta-feira às 15h. Abraço!". |
| `sugestao_pos_diag` | `auto`, `1`, `2` | Fixa a sugestão do e-mail pós-Diag. `auto`: a 2 quando há parágrafo autoral. |
| `sugestao_pos_aprof` | `auto`, `1`, `2` | O mesmo para o e-mail pós-Aprof. |

O resto do texto é o do documento. Se o CN pedir uma mudança que não está nesta tabela ("eu falo 'a gente' em vez de 'nós'"), diga que o perfil não cobre e que mudar o texto é pedir a atualização do documento oficial (veja "Mudar um texto" em `cadencia.md`). Num caso pontual, ele pode editar o rascunho ou o texto antes de enviar.

## Achar o perfil do CN

1. get_identity no Fathom → e-mail. Compare sem caixa com o `email` de cada arquivo em `references/perfis/`.
2. Sem Fathom conectado, pergunte ao CN o e-mail Poli Júnior.
3. Achou: siga. Não achou: cadastro abaixo.

`_modelo.json` é o modelo vazio; não é perfil de ninguém.

## Cadastro de um CN novo

A pasta da skill é só leitura durante o uso, então o perfil novo nasce no chat e vai para a skill pelo mantenedor (hoje, o Augustus).

1. **Nome e e-mail:** do get_identity do Fathom; se faltar, pergunte.
2. **ID no Pipedrive:** peça ao CN o nome de uma empresa com card dele no funil. Ache o card (`pipedrive.md`) e leia o `owner_id`. Confirme com getNotes do card: a nota escrita por ele vem com `user.is_you: true` e o `user_id` dele. Os dois têm que bater; se não baterem, pergunte.
3. **Estilo:** uma pergunta com AskUserQuestion (multiSelect), com as opções "Abro com Oi em vez de Olá", "Não uso 'Tudo bem?'", "Não uso emoji", "Despedida própria nos e-mails". Se ele marcar a última, pergunte qual em texto livre. O que ele não marcar fica no padrão.
4. **Voz autoral:** peça um ou dois parágrafos de e-mails que ele já mandou para cliente. Resuma o jeito dele em `voz_autoral` (uma ou duas frases) e guarde até 3 exemplos.
5. Grave o JSON em `{diretório de trabalho}/perfil-{usuario}.json` e use esse caminho em `--perfil` nesta sessão.
6. Entregue o arquivo ao CN com SendUserFile e diga em uma linha para mandá-lo ao mantenedor da skill, que o coloca em `references/perfis/`. Até lá, toda sessão nova repete o cadastro.

Pedido de ajuste de um perfil existente ("tira o emoji do meu perfil"): gere o JSON atualizado do mesmo jeito, use-o na sessão e entregue para o mantenedor.
