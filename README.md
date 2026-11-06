# LLM Output Arbitration System

## Project Overview

O LLM Output Arbitration System é uma proposta de sistema multiagente com Python e LangGraph para avaliar respostas geradas por modelos de linguagem. Essas respostas podem conter erros factuais, raciocínios inconsistentes ou omissões difíceis de identificar em uma única avaliação. O objetivo do projeto é analisar cada resposta em relação à pergunta original e consolidar os resultados em um veredito final.

## Core Concept

Três agentes críticos independentes avaliam a mesma resposta sob perspectivas diferentes. Em seguida, o **Adjudicator** analisa as avaliações dos críticos e as consolida em um veredito final.

## Critic Agents

- **Factual Accuracy Critic:** verifica a exatidão dos fatos e identifica afirmações potencialmente incorretas ou que não podem ser verificadas.
- **Logical Consistency Critic:** avalia a coerência do raciocínio, possíveis contradições e se as conclusões decorrem dos argumentos apresentados.
- **Completeness Critic:** verifica se a resposta atende a todos os requisitos da pergunta original.

## Planned Tech Stack

- Python
- LangGraph
- Pydantic
- OpenAI
- Anthropic
- Ollama

## Development Status

O projeto está na **Phase 1**, dedicada à definição da arquitetura dos agentes críticos. O sistema descrito acima é uma proposta e ainda não é apresentado como implementado.
