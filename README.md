# Termo - Conversor de temperaturas

Projeto acadêmico de Vitor Gallucci: aplicação web Celsius/Fahrenheit com testes,
CI, Terraform local e agentes de IA para qualidade e observabilidade.

Repositório público: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia

## Requisitos

Python 3.11 ou superior (validado em 3.13), Git e navegador. Terraform 1.9.8 é necessário
somente para a atividade de IaC. A aplicação usa exclusivamente a biblioteca padrão.
Os testes e o linter usam as dependências de desenvolvimento fixadas no projeto.

## Diário de comandos - Windows / PowerShell

Execute na raiz do projeto, que contém este README. Não é necessário ativar o ambiente.

```powershell
git clone https://github.com/VitorGallucci/conversor-temperaturas-devops-ia.git
cd conversor-temperaturas-devops-ia
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest --cov=conversor --cov-branch --cov-report=term-missing --cov-report=json:build/coverage.json --cov-report=html:build/htmlcov --cov-fail-under=90 --junitxml=build/junit.xml
.\.venv\Scripts\python.exe -m scripts.build
.\.venv\Scripts\python.exe -m conversor.server
```

Abra http://127.0.0.1:8000. Para encerrar o servidor: Ctrl+C.
O build gera `dist/conversor.zip`; extraia e execute `python -m conversor.server`
na pasta extraída. Esse pacote não precisa de pip para executar.

## Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m pytest --cov=conversor --cov-branch --cov-fail-under=90
.venv/bin/python -m scripts.build
.venv/bin/python -m conversor.server
```

## Especificações

- Celsius para Fahrenheit: F = C × 1,8 + 32.
- Fahrenheit para Celsius: C = (F - 32) / 1,8.
- Aceita vírgula decimal na interface; API recebe número JSON.
- Mesma unidade preserva o valor; não há arredondamento intermediário.
- Interface exibe até seis casas decimais; API mantém precisão de ponto flutuante.
- Rejeita vazio, texto, booleano, NaN, infinito, unidade desconhecida, overflow
  e temperaturas abaixo de -273,15 °C / -459,67 °F.
- `GET /health`, `GET /metrics`, `POST /api/convert`.
- Exemplo de corpo: `{"value":25,"source":"C","target":"F"}`.
- Runtime grava logs e traces correlacionados por `trace_id` em `runtime/`.
- `p95_ms` usa as últimas 1000 conversões; `error_rate` é cumulativa e conta erros 5xx.
  Entradas inválidas (400) não são falhas internas da aplicação.

## Testes e falha intencional

Há testes unitários, de ida e volta, integração HTTP, validação e falha interna injetada.
Testes que verificam rejeições esperadas passam quando o sistema rejeita corretamente.
Para demonstrar um teste realmente vermelho, separado da suíte de produção:

```powershell
.\.venv\Scripts\python.exe -m pytest fixtures/demo_failure.py -v
```

Esse comando deve falhar: o exemplo exige propositalmente o valor errado para 0 °C.
Para mostrar baixa cobertura, execute apenas os pontos de referência:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_core.py -k reference_values --cov=conversor --cov-branch --cov-report=json:build/coverage.json --junitxml=build/junit.xml
.\.venv\Scripts\python.exe -m scripts.coverage_input
.\.venv\Scripts\python.exe -m scripts.gate tests build/tests-input.json --mode local
```

Rode novamente a suíte completa para restaurar o relatório de cobertura alta.

## IA e GitHub Actions

`ci.yml` roda linter, formatação, testes com cobertura de linhas e branches >=90%, e build.
`terraform.yml` roda fmt, init, validate e plan. Os outros workflows são manuais:

1. `ai-gates.yml`: selecione `real` e `healthy` ou `incident`. A matriz analisa testes,
   logs, métricas, traces, segurança e custos. Um bloqueio abre issue com a decisão
   e impede a etapa seguinte. Para testes, a entrada é medida pelo pytest;
   observabilidade/custos/segurança usam cenários didáticos identificados em `fixtures/`.
2. `ai-agent-pr.yml`: envia core e testes à API Groq; propõe novos casos e notas de versão,
   gera código de teste a partir de dados numéricos validados, roda testes e abre PR.
   Não faz merge nem executa Python arbitrário retornado pelo modelo.

O secret do repositório é `GROQCLOUD_API_KEY`. Nunca coloque seu valor no código.
O modelo padrão é `qwen/qwen3.8-27b`; `GROQ_MODEL` permite alterá-lo.
O modo `local` é uma simulação determinística, sem chamada a IA.
API indisponível, chave ausente, JSON inválido ou contrato inválido bloqueiam o gate.
A IA não pode liberar uma violação das regras mínimas.

Limites: cobertura >=90%, nenhum teste falhando, erro <=1%, p95 <=500ms,
nenhum log ERROR/CRITICAL, nenhum span error/timeout ou acima de 500ms,
zero instâncias ociosas e orçamento mensal <=R$100. São critérios didáticos.

Em Settings > Actions > General, habilite a opção que permite Actions criar PRs.
PR criado com GITHUB_TOKEN pode não disparar CI automaticamente; a validação já
ocorre no workflow do agente. Se necessário, execute CI manualmente na branch do PR.
Os resultados das execuções e os links de evidências ficam em `docs/EVIDENCIAS.md`.

## Terraform local

```powershell
terraform -chdir=infra init
terraform -chdir=infra fmt -check
terraform -chdir=infra validate
terraform -chdir=infra plan -out=local.tfplan
terraform -chdir=infra apply local.tfplan
terraform -chdir=infra plan
terraform -chdir=infra destroy
```

No PowerShell, se o argumento do plano for interpretado incorretamente, use
`terraform -chdir=infra plan '-out=local.tfplan'`.
O recurso local_file gera `infra/generated/deployment.json` com comando, porta e health check.
Ele não inicia o servidor: execute o comando de aplicação acima. `destroy` remove apenas
o manifesto gerenciado. State e planos ficam fora do Git. O lock do provider é versionado.

O exemplo AWS do material mostra ALB + Launch Template + Auto Scaling Group + health check.
Este mini projeto usa IaC local para demonstrar init/plan/apply sem conta ou custos de nuvem;
não alega ter provisionado alta disponibilidade na AWS.

## Estrutura e entregas

`conversor/`: aplicação; `web/`: interface; `tests/`: suíte;
`scripts/`: build e agentes; `infra/`: Terraform; `.github/workflows/`: automações;
`fixtures/`: dados didáticos saudáveis e incidentes; `docs/`: decisões e evidências.
Na pasta de entregas da Área de Trabalho, cada atividade possui uma pasta própria,
PDF correspondente e anexos necessários. Consulte `LEIA-ME-ENTREGAS.md`.

## Fontes técnicas

- https://docs.python.org/3/library/http.server.html
- https://docs.pytest.org/en/stable/
- https://console.groq.com/docs/api-reference
- https://console.groq.com/docs/models
- https://developer.hashicorp.com/terraform/language
- https://docs.github.com/en/actions/concepts/security/github_token

O servidor HTTP da biblioteca padrão é suficiente para a demonstração local acadêmica;
uma implantação pública exigiria servidor de produção, HTTPS e controles operacionais.

