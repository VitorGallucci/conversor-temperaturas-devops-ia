# Evidências reais - Termo

Autor: Vitor Gallucci. Data local: 26/10/2026 (America/Sao_Paulo).

## Execuções principais

| Atividade | Evidência | Resultado |
|---|---|---|
| CI em main | https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/actions/runs/40424817351 | Linter, formatação, 50 testes, cobertura 91,89% e build aprovados |
| Terraform | https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/actions/runs/40424817274 | fmt, init, validate e plan aprovados |
| IA: cenário saudável | https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/actions/runs/40424872636 | Seis gates aprovados; ai_executed=true |
| IA: incidentes | https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/actions/runs/40425134805 | Seis gates bloqueados; ai_executed=true; seis issues reais |
| Agente | https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/actions/runs/40425442825 | Cinco novos casos, 55 testes aprovados, commit e PR |
| Pull request | https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/pull/17 | Aberto pelo github-actions[bot]; sem merge automático |

## Issues automáticas dos cenários de incidente

- costs: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/issues/16
- security: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/issues/15
- metrics: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/issues/13
- tests: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/issues/11
- logs: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/issues/12
- traces: https://github.com/VitorGallucci/conversor-temperaturas-devops-ia/issues/14

## Origem e limitações

A cobertura do gate é medida durante o workflow. Os dados de logs, métricas, traces,
segurança e custos em fixtures são sintéticos e identificados. As chamadas à Groq,
as decisões, as execuções Actions e as issues são reais. Há logs e traces reais da
aplicação anexos às entregas, correlacionados por trace_id.

O modo local executa apenas regras determinísticas e nunca é apresentado como IA.
As primeiras tentativas ficaram no histórico: modelo antigo indisponível, cliente HTTP
sem User-Agent e prompt amplo que exigia critérios de outros gates. A correção do
modelo foi confirmada pela listagem real da Groq. Modelo final: qwen/qwen3.8-27b.
O agente também revelou a necessidade de formatar o código gerado antes do linter.

Os 50 testes da main têm 91,89% de cobertura; com os cinco casos do PR são 55 testes,
com o mesmo percentual. Acrescentar casos não implica aumentar o número de linhas cobertas.
Terraform foi aplicado localmente e o plano posterior não mostrou alterações.
Nenhum recurso AWS foi criado. O servidor da biblioteca padrão destina-se à demonstração local.

## Como conferir

Abra os links acima, consulte os passos e os artefatos de cada workflow. O diretório
evidencias/ das entregas preserva prints reais, logs brutos de cada job, relatórios JSON,
JUnit, cobertura HTML e os arquivos gerados no PR. As imagens são capturas da interface,
sem montagem para alterar resultados. A chave de API não integra os arquivos entregues.

## Referências técnicas

- Groq API: https://console.groq.com/docs/api-reference
- Modelos: https://console.groq.com/docs/models
- Terraform: https://developer.hashicorp.com/terraform/language
- GitHub token: https://docs.github.com/en/actions/concepts/security/github_token

