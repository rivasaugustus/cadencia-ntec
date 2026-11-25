#!/usr/bin/env python3
"""Monta a cadência de follow-up de um card do funil Vendas (CN) do NTec.

Uso:
  python3 montar_cadencia.py --momento {pos-diag|pos-aprof|pos-proposta} \
      --perfil references/perfis/nome.sobrenome.json \
      --nome "Fulana" --empresa "Empresa" --ultima-reuniao 2026-11-25 \
      [--proxima "2026-12-03 17:00"] [--link-sala URL] [--link-prototipo URL] \
      [--paragrafo "texto"] [--pedido "texto" --pedido-objeto {solucao|proposta|prototipo}] \
      [--grupo] [--spoiler] [--pular M1-F01,M1-F02] [--remarcacao] \
      [--livre mensagens.json] [--so-livre] [--reuniao "TouchPoint"] \
      [--rascunho M1-F01=URL ...] [--agora "2026-11-25 14:00"]

  --livre: lista JSON de mensagens escritas para casos sem modelo no documento,
  cada uma com rotulo, canal (whatsapp|email), texto, assunto (e-mail) e, opcional,
  data (AAAA-MM-DD) ou apos_dias_uteis (N dias úteis depois de hoje); sem nenhum
  dos dois, o primeiro dia útil com vaga. Com --so-livre,
  nenhuma mensagem do documento sai: só as livres, a sala e a reunião.

Saída: JSON com as tasks prontas (canal, tipo, assunto, data, note em HTML e,
nas de e-mail, o assunto e o corpo do rascunho), as que ficaram de fora (com
motivo), pendências e avisos. Erro de entrada: {"erro": ...}, código 2.
Erro da skill ou do perfil: {"erro_interno": ...}, código 3.
"""
import argparse
import hashlib
import html
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone

BRASILIA = timezone(timedelta(hours=-3))  # sem horário de verão desde 2019

# Textos do documento "Cadências, mensagens e follow-up | CNs", como estão lá.
# Os marcadores entre colchetes são preenchidos; o resto não muda.
MENSAGENS = """
=== M1-F01-S1 ===
Assunto: Próximos passos | Projeto [Empresa] + Poli Júnior

Olá, [Nome]!

Muito obrigado pelo tempo e pela conversa de hoje.

Foi muito importante entender melhor o cenário de vocês, os principais desafios enfrentados atualmente e os objetivos que esperam alcançar com o projeto.

A partir das informações levantadas durante nossa reunião, iniciaremos agora a construção de um protótipo da solução, que servirá como base para validarmos juntos os fluxos, funcionalidades e requisitos antes da elaboração da proposta comercial.

Conforme alinhamos, nossa próxima etapa será a Reunião de Aprofundamento, onde apresentaremos esse protótipo para refinarmos a solução e garantir que ela esteja aderente à realidade da operação de vocês.

Enquanto isso, caso lembrem de alguma informação relevante ou tenham qualquer dúvida, fiquem totalmente à vontade para entrar em contato.

Mais uma vez, obrigado pela disponibilidade.

Nos vemos em breve!
=== M1-F01-S2 ===
Assunto: Próximos passos | Projeto [Empresa] + Poli Júnior

Olá, [Nome]!

Muito obrigado pelo tempo e pela conversa de hoje.

Conforme conversamos, vamos iniciar a construção da solução com base no cenário que vocês compartilharam.

Para garantir que estamos partindo do mesmo entendimento, nosso principal foco será ajudar vocês a resolver:

[Parágrafo autoral]

Agora nossa equipe iniciará a construção do protótipo da solução, que será apresentado na próxima reunião. Esse protótipo servirá como base para validarmos juntos os fluxos, funcionalidades e requisitos antes da elaboração da proposta.

Caso lembrem de qualquer informação relevante ou tenham alguma dúvida, basta responder este e-mail ou me chamar no WhatsApp.

Até breve!
=== M1-F02-S1 ===
Olá, [Nome]! Tudo bem?

[Nome e Sobrenome] do Núcleo de Tecnologia da Poli Júnior aqui.

Passando apenas para abrir nosso canal de comunicação pelo Whats também.

Acabei de encaminhar um e-mail resumindo os próximos passos do projeto.

Se surgir qualquer dúvida, informação nova ou até alguma ideia que vocês lembrem ao longo dos próximos dias, podem me chamar por aqui mesmo.

Vamos trabalhar na construção do protótipo e nos vemos na nossa próxima reunião!
=== M1-F02-S2 ===
Olá, pessoal! Tudo bem?

Criei este grupo para concentrarmos toda a comunicação do projeto.

Por aqui compartilharei os próximos passos, materiais, links das reuniões e eventuais alinhamentos até a conclusão da proposta.

Se surgir qualquer informação importante ao longo do processo, podem compartilhar por aqui também.
=== M1-F03 ===
Olá, [Nome]! Tudo bem?

Passando para avisar que já está tudo preparado para nossa reunião de amanhã, às [horário].

Desde nossa última conversa trabalhamos na construção de um protótipo baseado nos desafios, processos e objetivos que vocês compartilharam conosco.

Amanhã vamos validar essa construção juntos, refinando fluxos, regras de negócio e funcionalidades para garantir que ela represente da melhor forma a realidade da operação de vocês.

Até amanhã!
=== M1-F04 ===
Aproveitando...

Estamos finalizando os últimos detalhes do protótipo e acredito que vocês vão conseguir visualizar muito bem como a solução foi desenhada para atender aos desafios que conversamos.

[Spoiler]Amanhã apresento tudo com mais detalhes!
=== M1-F05 ===
Oi, [Nome]!

Já estou na sala da reunião.

Segue o link para facilitar o acesso:

[Link]

Até já!
=== M2-F01-S1 ===
Assunto: Próximos passos | Projeto [Empresa] + Poli Júnior

Obrigado pela participação na reunião de hoje.

Conforme combinado, segue o link para acesso ao protótipo apresentado durante nossa conversa:

🔗 [Link do protótipo]

Agora vocês podem navegar pela solução com mais calma e compartilhá-la com as demais pessoas envolvidas no projeto, caso considerem necessário.

Nos próximos dias consolidaremos todas as validações realizadas para finalizar a solução e preparar nossa próxima reunião, onde apresentaremos o escopo final do projeto e a proposta comercial construída com base em tudo o que desenvolvemos juntos até aqui.

Caso identifique algum ajuste ou oportunidade de melhoria relevante para o escopo, pedimos que nos sinalize até 3 dias antes da reunião para que possamos ajustá-lo com antecedência.

Estamos disponíveis pelo e-mail ou WhatsApp.

Até [Dia da semana] às [Horário]. Abraço!
=== M2-F01-S2 ===
Assunto: Próximos passos | Projeto [Empresa] + Poli Júnior

Olá, [Nome]!

Obrigado pela participação na reunião de hoje.

Conforme alinhamos, segue abaixo o link para acesso ao protótipo apresentado durante nossa conversa:

🔗 Protótipo: [Link do protótipo]

Durante os próximos dias, vocês podem navegar pela solução e compartilhá-la com as demais áreas envolvidas no projeto, caso façam sentido novas validações internas.

Nosso principal alinhamento durante a reunião foi:

[Parágrafo autoral]

Caso identifiquem qualquer ajuste, melhoria ou nova necessidade, podem responder este e-mail ou me chamar diretamente pelo WhatsApp. Todas as contribuições serão avaliadas antes da consolidação da solução.

Próximos passos conforme combinamos:

- Revisão interna do protótipo pela equipe da [Empresa];
- Consolidação dos ajustes e validações realizadas;
- Estruturação da proposta comercial;
- Apresentação da proposta na reunião agendada para [data].

Fico à disposição!
=== M2-F02 ===
Olá, [Nome]!

Acabei de encaminhar um e-mail com o resumo da nossa reunião, os próximos passos e o link do protótipo apresentado hoje.

Deixo o link por aqui também para facilitar o acesso:

🔗 [Link do protótipo]

Se durante a análise surgir qualquer ajuste ou nova ideia, podem me chamar por aqui mesmo. Ainda estamos no momento ideal para incorporar essas contribuições à solução.
=== M2-F03 ===
Olá, [Nome]! Tudo bem?

Passando para avisar que já está tudo preparado para nossa reunião de amanhã, às [horário].

Desde nossa última conversa consolidamos todos os ajustes discutidos, refinamos a solução e estruturamos a proposta considerando o cenário e as prioridades que vocês compartilharam ao longo de todo o processo.

Amanhã vamos apresentar o resultado desse trabalho, detalhando a solução proposta, o escopo do projeto e como ela foi construída para atender às necessidades da operação de vocês.

Até amanhã!
=== M2-F04 ===
Olá, [Nome]!

Já estou na sala e deixo abaixo o link para facilitar o acesso:

[Link]

Até já!
=== M2-F05 ===
Olá, [Nome]! Tudo bem?

Estamos finalizando os últimos detalhes da solução/proposta/protótipo e surgiu um ponto que gostaríamos de validar com vocês.

[Pedido]

Assim que tiverem essa informação, conseguem me encaminhar por aqui por favor?

Obrigado!
=== M3-F01 ===
Assunto: Proposta Comercial | [Empresa] + Poli Júnior

Olá, [Nome]!

Quero agradecer pelo tempo, confiança e transparência ao longo das nossas conversas.

Desde nossa primeira reunião buscamos compreender não apenas o projeto que vocês desejam desenvolver, mas, principalmente, os desafios que motivaram essa iniciativa e os objetivos que esperam alcançar.

Ao longo desse processo construímos, juntos, uma solução pensada para a realidade da [Empresa], sempre buscando equilibrar aderência ao negócio, viabilidade técnica e potencial de impacto para a operação.

Em anexo, encaminho a Proposta Comercial apresentada durante nossa reunião. Também compartilho novamente o link do protótipo para que vocês possam consultá-lo caso necessário:

🔗 Protótipo: [Link do protótipo]

Agora, conforme combinamos, vocês terão este período para avaliar internamente a proposta e consolidar os feedbacks.

Nossa próxima conversa está agendada para [dia], quando alinharemos a definição sobre o projeto, esclareceremos eventuais dúvidas e discutiremos os próximos passos.

Acreditamos que essa solução pode contribuir para reduzir os desafios discutidos durante nossas reuniões e apoiar a empresa na conquista dos resultados esperados.

Independentemente da decisão final, foi um prazer conhecer melhor o negócio de vocês e participar dessa construção.

Seguimos à disposição para qualquer esclarecimento e esperamos ter a oportunidade de desenvolver esse projeto juntos.

Um grande abraço!
=== M3-F02 ===
Olá, [Nome]!

Acabei de encaminhar por e-mail a proposta comercial, o protótipo e os materiais que apresentamos durante nossa reunião.

Fiquem à vontade para analisar tudo com calma e, se surgir qualquer dúvida ou ponto que gostariam de discutir, podem me chamar por aqui.
=== M3-F03 ===
Olá, [Nome]! Tudo bem?

Passando para dizer que sigo à disposição caso surja qualquer dúvida durante a análise da proposta ou se precisarem de algum material complementar para apoiar as discussões internas.

Se eu puder ajudar de alguma forma nesse processo, é só me chamar por aqui. 😊
=== M3-F04 ===
Oi, [Nome]!

Já estou na sala da reunião.

Segue o link para facilitar o acesso:

[Link]

Até já!
"""

# Impressão digital dos textos acima. Se não bater, algum texto mudou: o script para.
HASH_MENSAGENS = "c104a6f78f790b6e8ef7968ab264a65643f66ae758b422b96401cd608ee4625c"

# Textos cuja última linha é só despedida e pode seguir o perfil do CN (fecho_email).
FECHO_LIVRE = {"M1-F01-S1", "M1-F01-S2", "M2-F01-S2", "M3-F01"}

LIMITE_TOQUES_DIA = 2  # um por canal aberto (e-mail e WhatsApp)

SEM_LINK_SALA = "LINK DA SALA DA REUNIÃO"
SEM_LINK_PROTO = "LINK DO PROTÓTIPO"

# Momento → reunião seguinte e as chaves de cada papel na cadência.
MOMENTOS = {
    "pos-diag": {
        "reuniao": "AT Aprofundamento",
        "pos_email": "M1-F01", "pos_whats": "M1-F02",
        "vespera": "M1-F03", "complemento": "M1-F04", "sala": "M1-F05",
        "disponibilidade": None, "pedido": None,
        "rotulo_pos": "Pós AT Diag.", "rotulo_vespera": "Véspera AT Aprof.",
    },
    "pos-aprof": {
        "reuniao": "Apresentação de Proposta",
        "pos_email": "M2-F01", "pos_whats": "M2-F02",
        "vespera": "M2-F03", "complemento": None, "sala": "M2-F04",
        "disponibilidade": None, "pedido": "M2-F05",
        "rotulo_pos": "Pós AT Aprof.", "rotulo_vespera": "Véspera Proposta",
    },
    "pos-proposta": {
        "reuniao": "Próximos passos",
        "pos_email": "M3-F01", "pos_whats": "M3-F02",
        "vespera": None, "complemento": None, "sala": "M3-F04",
        "disponibilidade": "M3-F03", "pedido": None,
        "rotulo_pos": "Pós Proposta", "rotulo_vespera": None,
    },
}

DIA_CURTO = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
DIA_LONGO = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
DIA_FEIRA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

OBJETO_PEDIDO = {"solucao": "da solução", "proposta": "da proposta", "prototipo": "do protótipo"}

ESTILO_PADRAO = {
    "saudacao": "manter",
    "tudo_bem": True,
    "emoji": True,
    "fecho_email": None,
    "sugestao_pos_diag": "auto",
    "sugestao_pos_aprof": "auto",
}


class ErroEntrada(Exception):
    pass


# ---------- datas ----------

def hora(h, m):
    return f"{h}h" if m == 0 else f"{h}h{m:02d}"


def curto(d):
    return f"{DIA_CURTO[d.weekday()]}, {d:%d/%m}"


def dia_util_anterior(d):
    d -= timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def proximo_dia_util(d):
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def menos_dias_uteis(d, n):
    for _ in range(n):
        d = dia_util_anterior(d)
    return d


# ---------- textos ----------

def textos():
    if hashlib.sha256(MENSAGENS.encode("utf-8")).hexdigest() != HASH_MENSAGENS:
        raise RuntimeError("os textos da cadência mudaram em relação à versão conferida (HASH_MENSAGENS)")
    blocos, atual = {}, None
    for linha in MENSAGENS.strip("\n").split("\n"):
        m = re.fullmatch(r"=== (.+) ===", linha)
        if m:
            atual = m.group(1)
            blocos[atual] = []
        else:
            blocos[atual].append(linha)
    return {k: "\n".join(v).strip("\n") for k, v in blocos.items()}


def preencher(chave, trocas):
    """Troca os marcadores numa passada só e confere que nenhum colchete sobrou."""
    texto = textos()[chave]
    for marcador in trocas:
        if marcador not in texto:
            raise RuntimeError(f"marcador {marcador!r} não aparece em {chave}")
    if trocas:
        padrao = "|".join(re.escape(m) for m in sorted(trocas, key=len, reverse=True))
        texto = re.sub(padrao, lambda m: trocas[m.group(0)], texto)
    sobra = re.findall(r"\[[^\]\n]+\]", texto)
    if sobra:
        raise RuntimeError(f"{chave} ficou com marcador sem preencher: {', '.join(sobra)}")
    return texto


def aplicar_estilo(chave, texto, estilo):
    """Ajustes controlados do perfil do CN. Só mexem em abertura, despedida e emoji."""
    linhas = texto.split("\n")
    i = 1 if linhas[0].startswith("Assunto: ") else 0
    while i < len(linhas) and not linhas[i].strip():
        i += 1
    if i < len(linhas):
        abertura = linhas[i]
        if estilo["saudacao"] != "manter":
            abertura = re.sub(r"^(Olá|Oi), ", estilo["saudacao"] + ", ", abertura)
        if not estilo["tudo_bem"]:
            abertura = abertura.replace(" Tudo bem?", "")
        linhas[i] = abertura
    if estilo["fecho_email"] and chave in FECHO_LIVRE:
        linhas[-1] = estilo["fecho_email"]
    texto = "\n".join(linhas)
    if not estilo["emoji"]:
        texto = texto.replace("🔗 ", "").replace(" 😊", "").replace(" 😄", "").replace("😊", "").replace("😄", "")
    return texto


def trocar_amanha(texto, dia_reuniao):
    """Véspera que não cai no dia anterior (reunião de segunda, véspera na sexta)."""
    dia = DIA_FEIRA[dia_reuniao.weekday()]
    return (texto.replace("de amanhã", f"de {dia}")
                 .replace("Amanhã vamos", f"Na {dia} vamos")
                 .replace("Amanhã apresento", f"Na {dia} apresento")
                 .replace("Até amanhã!", f"Até {dia}!"))


def referencia_dia(ultima, envio):
    """Como o texto se refere ao dia da reunião quando o pós sai depois dela."""
    delta = (envio - ultima).days
    if delta == 1:
        return "de ontem", "ontem"
    if delta < 7:
        dia = DIA_FEIRA[ultima.weekday()]
        return f"de {dia}", f"na {dia}"
    return f"do dia {ultima:%d/%m}", f"no dia {ultima:%d/%m}"


def trocar_hoje(texto, ultima, envio):
    """Pós-reunião enviado depois do dia da reunião: o "hoje" passa a apontar para ela."""
    de, em = referencia_dia(ultima, envio)
    return (texto.replace("conversa de hoje", f"conversa {de}")
                 .replace("reunião de hoje", f"reunião {de}")
                 .replace("apresentado hoje", f"apresentado {em}"))


def separar_assunto(texto):
    linhas = texto.split("\n")
    if linhas[0].startswith("Assunto: "):
        return linhas[0][len("Assunto: "):].strip(), "\n".join(linhas[1:]).lstrip("\n")
    return None, texto


def para_html(texto):
    return html.escape(texto, quote=False).replace("\n", "<br>")


# ---------- perfil ----------

def carregar_perfil(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            p = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise RuntimeError(f"perfil ilegível ({caminho}): {e}")
    for campo in ("nome", "email", "pipedrive_user_id", "apresentacao_whats"):
        if not p.get(campo):
            raise RuntimeError(f"perfil sem o campo {campo}")
    estilo = dict(ESTILO_PADRAO)
    desconhecidos = set(p.get("estilo", {})) - set(ESTILO_PADRAO)
    if desconhecidos:
        raise RuntimeError(f"perfil com ajuste desconhecido: {', '.join(sorted(desconhecidos))}")
    estilo.update(p.get("estilo", {}))
    if estilo["saudacao"] not in ("manter", "Olá", "Oi"):
        raise RuntimeError("saudacao deve ser 'manter', 'Olá' ou 'Oi'")
    if not isinstance(estilo["tudo_bem"], bool) or not isinstance(estilo["emoji"], bool):
        raise RuntimeError("tudo_bem e emoji devem ser true ou false")
    if estilo["fecho_email"] is not None:
        f = str(estilo["fecho_email"]).strip()
        if not f or "\n" in f or len(f) > 40:
            raise RuntimeError("fecho_email deve ser uma linha curta (até 40 caracteres) ou null")
        estilo["fecho_email"] = f
    for k in ("sugestao_pos_diag", "sugestao_pos_aprof"):
        estilo[k] = str(estilo[k])
        if estilo[k] not in ("auto", "1", "2"):
            raise RuntimeError(f"{k} deve ser 'auto', '1' ou '2'")
    p["estilo"] = estilo
    return p


# ---------- montagem ----------

def montar(a, agora):
    perfil = carregar_perfil(a.perfil)
    estilo = perfil["estilo"]
    cfg = MOMENTOS.get(a.momento)
    if not cfg:
        raise ErroEntrada(f"momento '{a.momento}' deve ser pos-diag, pos-aprof ou pos-proposta")

    nome = " ".join((a.nome or "").split())
    empresa = " ".join((a.empresa or "").split())
    if not nome:
        raise ErroEntrada("falta o primeiro nome do contato (--nome)")
    if not empresa:
        raise ErroEntrada("falta o nome da empresa (--empresa)")

    hoje = agora.date()
    if not a.ultima_reuniao:
        if not a.so_livre:
            raise ErroEntrada("falta a data da última reunião (--ultima-reuniao)")
        a.ultima_reuniao = hoje.isoformat()
    try:
        ultima = datetime.strptime(a.ultima_reuniao.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ErroEntrada(f"--ultima-reuniao '{a.ultima_reuniao}' fora do formato AAAA-MM-DD")
    if a.so_livre and not a.livre and not a.proxima:
        raise ErroEntrada("--so-livre sem --livre nem --proxima não gera nada")
    if ultima > hoje:
        raise ErroEntrada(f"a última reunião ({ultima:%d/%m}) está no futuro")

    prox = None
    if a.proxima:
        try:
            prox = datetime.strptime(a.proxima.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            raise ErroEntrada(f"--proxima '{a.proxima}' fora do formato AAAA-MM-DD HH:MM")
        if prox.weekday() >= 5:
            raise ErroEntrada(f"a próxima reunião cai num {DIA_LONGO[prox.weekday()]} ({prox:%d/%m}); confirme a data")
        if prox <= agora:
            raise ErroEntrada(f"a próxima reunião ({prox:%d/%m} às {hora(prox.hour, prox.minute)}) já passou")
    if a.remarcacao and not prox:
        raise ErroEntrada("remarcação precisa da nova data (--proxima)")

    pular = {c.strip() for c in (a.pular or "").split(",") if c.strip()}
    ja_hoje = {c.strip() for c in (a.pular_hoje or "").split(",") if c.strip()}
    pular |= ja_hoje
    rascunhos = {}
    for r in a.rascunho or []:
        if "=" not in r:
            raise ErroEntrada(f"--rascunho '{r}' deve ser CHAVE=URL")
        k, v = r.split("=", 1)
        rascunhos[k.strip()] = v.strip()

    link_sala = (a.link_sala or "").strip() or None
    link_proto = (a.link_prototipo or "").strip() or None
    paragrafo = " ".join((a.paragrafo or "").split()) or None
    pedido = (a.pedido or "").strip() or None

    tasks, nao_criadas, pendencias, avisos = [], [], [], []
    # Toques de follow-up por dia. Com dois canais abertos (e-mail e WhatsApp), até dois
    # no mesmo dia; mais que isso é demais. A sala e a task da reunião não contam.
    toques = {}

    def cabe(dia):
        return toques.get(dia, 0) < LIMITE_TOQUES_DIA

    def marcar(dia, n=1):
        toques[dia] = toques.get(dia, 0) + n

    if ja_hoje:
        marcar(hoje if hoje.weekday() < 5 else proximo_dia_util(hoje), len(ja_hoje))

    if prox:
        D = prox.date()
        h_prox = hora(prox.hour, prox.minute)
        sala_dt = prox - timedelta(minutes=3)
        h_sala = hora(sala_dt.hour, sala_dt.minute)
        data_ext = f"{DIA_FEIRA[prox.weekday()]}, {prox:%d/%m}, às {h_prox}"
    else:
        D = h_prox = h_sala = data_ext = None

    def item(chave, canal, tipo, assunto, dia, texto):
        out = {"chave": chave, "canal": canal, "tipo": tipo, "assunto": assunto,
               "data": dia.isoformat(), "data_curta": curto(dia), "note": None,
               "email": None, "rascunho": None}
        if texto is None:
            return out
        if tipo == "email":
            assunto_msg, corpo = separar_assunto(texto)
            out["email"] = {"assunto": assunto_msg, "corpo": corpo}
            url = rascunhos.get(chave)
            if url:
                out["rascunho"] = url
                out["note"] = (f'<a href="{html.escape(url, quote=True)}">Abrir rascunho no Gmail</a>'
                               "<br><br>" + para_html(corpo))
            else:
                out["note"] = "(rascunho ainda não criado)<br><br>" + para_html(corpo)
        else:
            out["note"] = para_html(texto)
        return out

    def texto_de(chave_txt, trocas):
        return aplicar_estilo(chave_txt, preencher(chave_txt, trocas), estilo)

    def colocar_livres(limite):
        """Mensagens escritas pelo Claude para casos sem modelo no documento (--livre)."""
        if not a.livre:
            return
        try:
            with open(a.livre, encoding="utf-8") as f:
                itens = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise ErroEntrada(f"--livre ilegível: {e}")
        if not isinstance(itens, list) or not itens:
            raise ErroEntrada("--livre deve ser uma lista JSON com pelo menos uma mensagem")
        for n, it in enumerate(itens, 1):
            chave = f"LIVRE-{n}"
            rotulo = " ".join(str(it.get("rotulo", "")).split())
            canal = str(it.get("canal", "")).strip().lower()
            texto = str(it.get("texto", "")).strip()
            if not rotulo or len(rotulo) > 40:
                raise ErroEntrada(f"{chave}: 'rotulo' curto é obrigatório (até 40 caracteres)")
            if canal not in ("whatsapp", "email"):
                raise ErroEntrada(f"{chave}: 'canal' deve ser whatsapp ou email")
            if not texto:
                raise ErroEntrada(f"{chave}: falta o texto")
            sobra = re.findall(r"\[[^\]\n]+\]", texto)
            if sobra:
                raise ErroEntrada(f"{chave}: texto com marcador sem preencher: {', '.join(sobra)}")
            if "—" in texto:
                raise ErroEntrada(f"{chave}: texto com travessão; reescreva sem ele")
            texto = aplicar_estilo(chave, texto, estilo)
            if canal == "email":
                assunto = " ".join(str(it.get("assunto", "")).split())
                if not assunto:
                    raise ErroEntrada(f"{chave}: e-mail precisa de 'assunto'")
                texto = f"Assunto: {assunto}\n\n{texto}"
            canal_txt, tipo = ("E-mail", "email") if canal == "email" else ("WhatsApp", "mensagem")
            if it.get("data"):
                try:
                    dia = datetime.strptime(str(it["data"]).strip(), "%Y-%m-%d").date()
                except ValueError:
                    raise ErroEntrada(f"{chave}: data '{it['data']}' fora do formato AAAA-MM-DD")
                if dia < hoje or dia.weekday() >= 5:
                    raise ErroEntrada(f"{chave}: a data {dia:%d/%m} já passou ou cai no fim de semana")
                if limite and dia >= limite:
                    nao_criadas.append({"chave": chave, "motivo": f"{curto(dia)} não é antes da próxima reunião ({curto(limite)})"})
                    continue
                if not cabe(dia):
                    nao_criadas.append({"chave": chave, "motivo": f"{curto(dia)} já tem dois toques"})
                    continue
            else:
                inicio = dia_envio
                if it.get("apos_dias_uteis") is not None:
                    try:
                        n_dias = int(it["apos_dias_uteis"])
                    except (TypeError, ValueError):
                        raise ErroEntrada(f"{chave}: 'apos_dias_uteis' deve ser um número inteiro")
                    for _ in range(max(n_dias, 0)):
                        inicio = proximo_dia_util(inicio)
                dias, d = [], inicio
                while len(dias) < 15 and (not limite or d < limite):
                    dias.append(d)
                    d = proximo_dia_util(d)
                com_vaga = [d for d in dias if cabe(d)]
                if it.get("apos_dias_uteis") is not None:
                    # Dia pedido: fica nele enquanto couber; senão, o próximo com vaga.
                    dia = (com_vaga or [None])[0]
                else:
                    livre = [d for d in dias if toques.get(d, 0) == 0]
                    dia = (livre or com_vaga or [None])[0]
                if dia is None:
                    nao_criadas.append({"chave": chave, "motivo": "não há dia com vaga antes da próxima reunião"})
                    continue
                if it.get("apos_dias_uteis") is not None and dia != inicio:
                    avisos.append(f"{chave} foi para {curto(dia)}: {curto(inicio)} já tinha dois toques.")
            marcar(dia)
            tasks.append(item(chave, canal_txt, tipo, f"{canal_txt} - {rotulo}", dia, texto))

    dia_envio = hoje if hoje.weekday() < 5 else proximo_dia_util(hoje)

    # 1. Pós-reunião (e-mail + WhatsApp). Sai sempre, no primeiro dia útil a partir de hoje.
    # Se a reunião não foi nesse dia, o "hoje" dos textos passa a apontar para o dia dela.
    if not a.remarcacao and not a.so_livre:
        k_email, k_whats = cfg["pos_email"], cfg["pos_whats"]
        atrasado = ultima != dia_envio
        def texto_pos(chave_txt, trocas):
            texto = texto_de(chave_txt, trocas)
            if atrasado:
                novo = trocar_hoje(texto, ultima, dia_envio)
                if novo != texto:
                    de, em = referencia_dia(ultima, dia_envio)
                    avisos.append(f"{chave_txt} sai depois da reunião ({curto(ultima)}): o \"hoje\" do texto virou \"{de}\" / \"{em}\".")
                texto = novo
            return texto

        # Conta só o que sai agora. Pós que o CN já mandou hoje por conta própria vai em
        # --pular-hoje, que também ocupa o dia.
        n_pos = len({k_email, k_whats} - pular)
        if n_pos:
            marcar(dia_envio, n_pos)
        # E-mail
        if k_email not in pular:
            if a.momento == "pos-diag":
                pref = estilo["sugestao_pos_diag"]
                sug = "2" if (pref == "2" or (pref == "auto" and paragrafo)) else "1"
                if sug == "2" and not paragrafo:
                    raise ErroEntrada("o perfil pede a sugestão 2 do pós-Diag, que precisa do parágrafo autoral (--paragrafo)")
                chave_txt = f"M1-F01-S{sug}"
                trocas = {"[Nome]": nome, "[Empresa]": empresa}
                if sug == "2":
                    trocas["[Parágrafo autoral]"] = paragrafo
            elif a.momento == "pos-aprof":
                if not prox:
                    raise ErroEntrada("o e-mail pós-Aprof cita a data da apresentação de proposta: falta --proxima")
                pref = estilo["sugestao_pos_aprof"]
                prazo_curto = (D - hoje).days < 4
                if pref == "2" or (pref == "auto" and paragrafo):
                    sug = "2"
                else:
                    sug = "1"
                if sug == "2" and not paragrafo:
                    raise ErroEntrada("a sugestão 2 do pós-Aprof precisa do parágrafo de alinhamento (--paragrafo)")
                if sug == "1" and prazo_curto:
                    pendencias.append("O e-mail pós-Aprof (sugestão 1) pede ajustes \"até 3 dias antes da reunião\", e a proposta é em menos de 4 dias: revise essa linha no rascunho ou use a sugestão 2 com --paragrafo.")
                chave_txt = f"M2-F01-S{sug}"
                trocas = {"[Empresa]": empresa, "[Link do protótipo]": link_proto or SEM_LINK_PROTO}
                if sug == "1":
                    trocas["[Dia da semana]"] = DIA_FEIRA[prox.weekday()]
                    trocas["[Horário]"] = h_prox
                else:
                    trocas.update({"[Nome]": nome, "[Parágrafo autoral]": paragrafo, "[data]": data_ext})
            else:
                if not prox:
                    raise ErroEntrada("a Champions Letter cita a data da reunião de próximos passos: falta --proxima")
                chave_txt = "M3-F01"
                trocas = {"[Nome]": nome, "[Empresa]": empresa,
                          "[Link do protótipo]": link_proto or SEM_LINK_PROTO, "[dia]": data_ext}
                pendencias.append("Champions Letter: anexe o PDF da proposta comercial no rascunho antes de enviar.")
            avisos.append(f"E-mail pós-reunião: {chave_txt}.")
            rotulo_email = "Champions Letter" if a.momento == "pos-proposta" else cfg["rotulo_pos"]
            tasks.append(item(k_email, "E-mail", "email", f"E-mail - {rotulo_email}", dia_envio,
                              texto_pos(chave_txt, trocas)))
        # WhatsApp
        if k_whats not in pular:
            if a.momento == "pos-diag":
                if a.grupo:
                    chave_txt, trocas = "M1-F02-S2", {}
                else:
                    chave_txt = "M1-F02-S1"
                    trocas = {"[Nome]": nome, "[Nome e Sobrenome]": perfil["apresentacao_whats"]}
            elif a.momento == "pos-aprof":
                chave_txt = "M2-F02"
                trocas = {"[Nome]": nome, "[Link do protótipo]": link_proto or SEM_LINK_PROTO}
            else:
                chave_txt, trocas = "M3-F02", {"[Nome]": nome}
            tasks.append(item(k_whats, "WhatsApp", "mensagem", f"WhatsApp - {cfg['rotulo_pos']}", dia_envio,
                              texto_pos(chave_txt, trocas)))
    # 2. Sem próxima reunião: só o que é de hoje.
    if not prox:
        colocar_livres(None)
        avisos.append("Sem próxima reunião marcada: aquecimento, sala e task da reunião ficaram de fora.")
        return resultado(a, perfil, None, tasks, nao_criadas, pendencias, avisos)

    modelo = not a.so_livre  # --so-livre: só as mensagens livres, a sala e a reunião

    # 3. Véspera (+ complemento do pós-Diag).
    k = cfg["vespera"]
    if modelo and k and k not in pular:
        dia_v = dia_util_anterior(D)
        if dia_v < hoje:
            nao_criadas.append({"chave": k, "motivo": f"o dia da véspera ({curto(dia_v)}) já passou"})
        elif not cabe(dia_v):
            nao_criadas.append({"chave": k, "motivo": f"o dia da véspera ({curto(dia_v)}) já tem os dois toques do pós-reunião"})
        else:
            texto = texto_de(k, {"[Nome]": nome, "[horário]": h_prox})
            comp = cfg["complemento"]
            if comp and comp not in pular and (D - ultima).days > 4:
                spoiler = "Separei um pequeno spoiler 😄\n\n" if a.spoiler else ""
                texto += "\n\n---\nMensagem 2, logo em seguida:\n\n" + texto_de(comp, {"[Spoiler]": spoiler})
                avisos.append(f"Aquecimento 2 (M1-F04) junto com a véspera: o Aprof é {(D - ultima).days} dias depois do Diag.")
                if a.spoiler:
                    pendencias.append("Aquecimento 2: mande o print do protótipo logo depois da mensagem.")
            if dia_v + timedelta(days=1) != D:
                texto = trocar_amanha(texto, D)
                avisos.append(f"Véspera na {DIA_FEIRA[dia_v.weekday()]} para reunião na {DIA_FEIRA[D.weekday()]}: \"amanhã\" virou \"{DIA_FEIRA[D.weekday()]}\" no texto.")
            marcar(dia_v)  # véspera e complemento são uma conversa só
            tasks.append(item(k, "WhatsApp", "mensagem", f"WhatsApp - {cfg['rotulo_vespera']}, horário {h_prox}", dia_v, texto))

    # 4. Disponibilidade (pós-Proposta, prazo longo).
    k = cfg["disponibilidade"]
    if modelo and k and k not in pular:
        dia_d = menos_dias_uteis(D, 2)
        if (D - hoje).days < 5:
            nao_criadas.append({"chave": k, "motivo": f"a reunião de próximos passos é em menos de 5 dias ({curto(D)}); o toque é para prazo longo"})
        elif dia_d <= hoje or not cabe(dia_d):
            nao_criadas.append({"chave": k, "motivo": f"o dia do toque ({curto(dia_d)}) já passou ou já tem dois toques"})
        else:
            marcar(dia_d)
            tasks.append(item(k, "WhatsApp", "mensagem", "WhatsApp - Disponibilidade", dia_d,
                              texto_de(k, {"[Nome]": nome})))

    # 5. Pedido de informação (pós-Aprof), só quando falta algo.
    k = cfg["pedido"]
    if modelo and k and pedido and k not in pular and not a.remarcacao:
        objeto = OBJETO_PEDIDO.get((a.pedido_objeto or "").strip())
        if not objeto:
            raise ErroEntrada("--pedido-objeto deve ser solucao, proposta ou prototipo")
        # Primeiro dia útil antes da reunião sem nenhum toque; se não houver, o primeiro com um só.
        dias = []
        d = hoje if hoje.weekday() < 5 else proximo_dia_util(hoje)
        while d < D:
            dias.append(d)
            d = proximo_dia_util(d)
        livre = [d for d in dias if toques.get(d, 0) == 0]
        com_vaga = [d for d in dias if cabe(d)]
        dia_p = (livre or com_vaga or [None])[0]
        if dia_p is None:
            nao_criadas.append({"chave": k, "motivo": "todos os dias até a reunião já têm dois toques"})
        else:
            if toques.get(dia_p, 0):
                avisos.append(f"Pedido de informação no mesmo dia de outro toque ({curto(dia_p)}): não sobrou dia livre antes da reunião.")
            marcar(dia_p)
            tasks.append(item(k, "WhatsApp", "mensagem", "WhatsApp - Pedido de informação", dia_p,
                              texto_de(k, {"[Nome]": nome, "da solução/proposta/protótipo": objeto, "[Pedido]": pedido})))

    # 6. Mensagens livres (casos sem modelo), antes da reunião.
    colocar_livres(D)

    # 7. Já estou na sala.
    k = cfg["sala"]
    if k not in pular:
        if (prox - timedelta(minutes=3)) <= agora:
            nao_criadas.append({"chave": k, "motivo": "o horário da sala já passou"})
        else:
            tasks.append(item(k, "WhatsApp", "mensagem", f"WhatsApp - Sala {h_sala}", D,
                              texto_de(k, {"[Nome]": nome, "[Link]": link_sala or SEM_LINK_SALA})))

    # 8. A própria reunião.
    nome_reuniao = " ".join((a.reuniao or "").split()) or cfg["reuniao"]
    tasks.append(item("REUNIAO", "—", "reuniao_remarcada" if a.remarcacao else "meeting",
                      f"{nome_reuniao} - {h_prox}", D, None))

    proxima = {"reuniao": nome_reuniao, "data": D.isoformat(), "hora": h_prox,
               "extenso": f"{DIA_LONGO[prox.weekday()]}, {prox:%d/%m}, às {h_prox}"}
    return resultado(a, perfil, proxima, tasks, nao_criadas, pendencias, avisos)


def resultado(a, perfil, proxima, tasks, nao_criadas, pendencias, avisos):
    # Marcadores de link que ficaram no texto por falta do dado.
    for falta, onde in ((SEM_LINK_SALA, "link da sala"), (SEM_LINK_PROTO, "link do protótipo")):
        chaves = [t["chave"] for t in tasks if t["note"] and falta in t["note"]]
        if chaves:
            pendencias.append(f"Sem {onde}: {', '.join(chaves)} sai com {falta} no lugar do link.")
    for t in tasks:
        if t["tipo"] == "email" and not t["rascunho"]:
            pendencias.append(f"{t['chave']}: rascunho ainda não criado; crie no Gmail e rode de novo com --rascunho {t['chave']}=URL.")
    return {
        "momento": a.momento,
        "cn": perfil["nome"],
        "remarcacao": bool(a.remarcacao),
        "proxima": proxima,
        "tasks": tasks,
        "nao_criadas": nao_criadas,
        "pendencias": pendencias,
        "avisos": avisos,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--momento", required=True, help="pos-diag, pos-aprof ou pos-proposta")
    p.add_argument("--perfil", required=True, help="arquivo JSON do perfil do CN")
    p.add_argument("--nome", required=True, help="primeiro nome do contato, ou 'Ana e João'")
    p.add_argument("--empresa", required=True, help="nome da empresa como o cliente usa")
    p.add_argument("--ultima-reuniao", help="data da reunião que define o momento: AAAA-MM-DD (opcional com --so-livre)")
    p.add_argument("--livre", help="arquivo JSON com mensagens escritas para casos sem modelo no documento")
    p.add_argument("--so-livre", action="store_true", help="não gera mensagens do documento; só as de --livre, a sala e a reunião")
    p.add_argument("--reuniao", help="nome da próxima reunião quando não é o padrão do momento (ex.: TouchPoint)")
    p.add_argument("--proxima", help="próxima reunião em Brasília: AAAA-MM-DD HH:MM")
    p.add_argument("--link-sala", help="link do Meet da próxima reunião")
    p.add_argument("--link-prototipo", help="link do protótipo")
    p.add_argument("--paragrafo", help="parágrafo autoral (cenário no pós-Diag, alinhamento no pós-Aprof)")
    p.add_argument("--pedido", help="o que falta pedir ao cliente (M2-F05)")
    p.add_argument("--pedido-objeto", help="solucao, proposta ou prototipo (M2-F05)")
    p.add_argument("--grupo", action="store_true", help="WhatsApp pós-Diag na versão de grupo")
    p.add_argument("--spoiler", action="store_true", help="aquecimento 2 com spoiler (print do protótipo)")
    p.add_argument("--pular", help="chaves já enviadas, separadas por vírgula (ex.: M1-F01,M1-F02)")
    p.add_argument("--pular-hoje", help="chaves que o CN já mandou hoje por conta própria (pulam e ocupam o dia)")
    p.add_argument("--remarcacao", action="store_true", help="só aquecimentos, sala e reunião, com a reunião como Reunião Remarcada")
    p.add_argument("--rascunho", action="append", help="CHAVE=URL do rascunho criado no Gmail (pode repetir)")
    p.add_argument("--agora", help="AAAA-MM-DD HH:MM em Brasília; padrão: agora")
    a = p.parse_args(argv)
    try:
        agora = (datetime.strptime(a.agora, "%Y-%m-%d %H:%M") if a.agora
                 else datetime.now(BRASILIA).replace(tzinfo=None))
        out = montar(a, agora)
    except ErroEntrada as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False))
        return 2
    except RuntimeError as e:
        print(json.dumps({"erro_interno": str(e)}, ensure_ascii=False))
        return 3
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
