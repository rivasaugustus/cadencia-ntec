# cadencia-ntec

Skill do Claude para a cadência de follow-up do funil Vendas (CN) do NTec, o Núcleo de Tecnologia da Poli Júnior.

Depois da AT Diagnóstica, do Aprofundamento e da Apresentação de Proposta, a skill preenche as mensagens do documento "Cadências, mensagens e follow-up | CNs" com o contexto do card (Fathom e notas), aplica o perfil de estilo do CN e cria no Pipedrive as tasks com o texto pronto de WhatsApp ou o link do rascunho no Gmail, mais a task da próxima reunião (ex.: `AT Aprofundamento - 17h`). Nos casos que o documento não cobre (lead que sumiu, contrato, cobrança, TouchPoint, lead que ficou de falar com o TI), escreve as mensagens a partir do repertório do documento.

## Instalar

1. Baixe a pasta `cadencia-ntec/` e compacte em .zip.
2. No Claude: Configurações > Capacidades > Skills > Upload skill.
3. Conecte Pipedrive, Fathom, Google Calendar e Gmail na sua conta.

## Usar

- "acabei a AT da {empresa}, a aprof ficou pra quinta 17h"
- "monta a cadência da {empresa}"
- "simula a cadência da {empresa}" (não grava nada)
- "a aprof da {empresa} mudou para segunda 10h"
- "o lead da {empresa} sumiu"

## Novo CN

Cada CN tem um perfil em `cadencia-ntec/references/perfis/{nome.sobrenome}.json`. Na primeira vez, a skill faz o cadastro no chat e devolve o arquivo: abra um PR adicionando-o nessa pasta.

## Estrutura

```
cadencia-ntec/
├── SKILL.md
├── scripts/montar_cadencia.py   textos do documento (com hash), datas e tasks
└── references/
    ├── pipedrive.md             funil, etapas, tasks
    ├── contexto.md              fontes e parágrafo autoral
    ├── cadencia.md              regras de datas e sugestões
    ├── sem-modelo.md            casos sem modelo no documento
    ├── perfis.md                perfis dos CNs
    └── perfis/                  um JSON por CN
```

Mantenedor: Augustus Rivas.
