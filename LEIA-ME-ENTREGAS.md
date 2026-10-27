# Entregas - Conversor de temperaturas

Autor: Vitor Gallucci. Projeto criado do zero para as atividades de DevOps e IA Generativa.

## O que enviar em cada atividade

1. **01_Projeto_Completo**: PDF com descrição e especificações; código completo em `codigo-fonte/` e ZIP do projeto.
2. **02_Manual_Execucao**: PDF com instalação, execução local, linter, testes, build e link do GitHub; README editável em anexo.
3. **03_Terraform**: envie `main.tf` e o PDF com resumo e dificuldade encontrada. Lock do provider e manifesto de exemplo são anexos.
4. **04_QualityGate_Observabilidade**: PDF com prints e explicações de aprovação/bloqueio da IA, logs, métricas, traces, issues e respostas do item 3.6 e do fechamento da aula.
5. **05_Agente_IA_PR**: PDF com a execução real do agente, alteração de código e PR; arquivos gerados e log do agente em anexo.

`06_Evidencias_Brutas/` reúne prints reais, logs das execuções, decisões JSON, cobertura HTML e JUnit.
`07_Pacote_Executavel/conversor.zip` é o build da aplicação. Extraia e rode `python -m conversor.server`.

## Resultados comprovados

- Main: 50 testes aprovados, 91,89% de cobertura com branches; regras de conversão com 100%.
- PR do agente: cinco casos adicionais, 55 testes aprovados; cobertura total permanece 91,89%.
- Cenário saudável: seis gates aprovados com API de IA real.
- Cenário de incidente: seis gates bloqueados com IA real e issues #11 a #16 criadas automaticamente.
- Terraform local validado e aplicado; plano posterior sem alterações. Não houve provisionamento AWS.

Repositório: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia

PR aberto pelo agente: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/pull/17

Links de pipelines, decisões e limitações estão em `codigo-fonte/docs/EVIDENCIAS.md`.
O PR permanece aberto para revisão, sem merge automático.

## Origem dos cenários

A cobertura é medida pelo pytest. Fixtures de logs, métricas, traces, segurança e custos são sintéticas,
identificadas como demonstração acadêmica. As chamadas à Groq, decisões, jobs, issues e PR são reais.
Logs e traces reais de conversões locais também estão anexos. A falha didática intencional fica fora
da suíte padrão, em `fixtures/demo_failure.py`.

## Executar o código completo no Windows

Abra o PowerShell em `codigo-fonte` e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest --cov=conversor --cov-branch --cov-fail-under=90
.\.venv\Scripts\python.exe -m conversor.server
```

Abra http://127.0.0.1:8000. Encerre com Ctrl+C. O README contém os demais comandos.
O ambiente virtual não foi copiado: deve ser criado na máquina de destino.
Chaves, state e planos Terraform não integram a entrega. A chave Groq está somente como secret no GitHub.
