# Reflexões - Aula 3

## Item 3.6

### 1. O que aconteceu quando o pipeline rodou? A IA bloqueou ou aprovou?

O cenário saudável mede a cobertura completa e envia os dados ao modelo. O cenário de
incidente executa somente os testes de referência, reduzindo a cobertura do módulo HTTP.
As decisões efetivamente obtidas, modos, execuções e links são registrados em EVIDENCIAS.md
e no relatório de Quality Gate. Uma execução em modo local não comprova chamada à IA.
O gate combina a revisão da IA com limites mínimos verificáveis, e bloqueia em falhas de API.

### 2. Desafio: provocar uma falha e observar a mudança de decisão

A redução de cobertura é reproduzível com a seleção `-k reference_values`, sem apagar
testes ou degradar a versão estável. Também existe uma falha de expectativa isolada em
fixtures/demo_failure.py: ela afirma propositalmente que 0 °C seria 0 °F. Os relatórios
guardam os resultados de acertos, falha intencional e comparação de cobertura.

### 3. Podemos confiar 100% na IA para bloquear um deploy em produção?

Não. A resposta depende de contexto, prompt, modelo e disponibilidade; pode apresentar
falsos positivos, falsos negativos e sofrer influência de conteúdo malicioso em logs.
Por isso, regras determinísticas protegem critérios mínimos; a resposta JSON é validada,
uma falha bloqueia a promoção e alterações de código passam por testes e revisão humana.
Devem existir auditoria, limites de permissão e procedimento de exceção documentado.

## Fechamento - item 6

### 1. Qual dos seis agentes foi mais fácil de simular? Por quê?

O agente de incidente: o conversor já emite logs estruturados e a severidade permite
produzir casos claros de normalidade e erro. O agente de custo é fácil de exemplificar,
mas seus dados são sintéticos: este projeto local não gera uma fatura de cloud.

### 2. Em quais confiar para agir autonomamente em produção?

Abertura de issue e sugestão de documentação são ações limitadas e reversíveis que podem
ser automatizadas com acompanhamento. Não autorizaria merge, deploy, destruição de
infraestrutura ou mudança de segurança apenas pela decisão do modelo. O agente de testes
abre PR para avaliação; o agente de custos recomenda ações e não desliga recursos.

### 3. O que muda se o prompt system for mal escrito?

Critérios vagos podem aprovar falhas ou bloquear casos normais. Um formato de saída
indefinido torna o processamento frágil. Falta de separação entre instruções e dados
abre espaço para prompt injection. Usamos papel explícito, limites, JSON validado,
dados serializados e mínimos obrigatórios; ainda assim, o modelo precisa de avaliação.

