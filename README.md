# Previsão do Tempo

Aplicação web em Flask para consultar o clima atual e a previsão dos próximos cinco dias por cidade ou localização do navegador.

## Funcionalidades

- Consulta de clima por nome da cidade.
- Seleção entre Celsius, Fahrenheit e Kelvin.
- Temperatura atual, sensação térmica, umidade e velocidade do vento.
- Previsão diária de cinco dias.
- Geolocalização do navegador.
- Cidades favoritas armazenadas localmente.
- Interface responsiva para computadores e celulares.

## Tecnologias

- Python
- Flask
- Requests
- Open-Meteo API
- HTML, CSS e JavaScript

## Como executar

Instale as dependências:

```powershell
python -m pip install flask requests
```

Execute a aplicação:

```powershell
python previsao_do_tempo.py
```

Acesse:

```text
http://127.0.0.1:5000
```

## Histórico do desenvolvimento

1. **Calculadora estatística:** a atividade começou com a criação de uma aplicação Flask em `calculadora.py`.
2. **Mudança de objetivo:** a aplicação foi transformada em uma página web para consulta meteorológica.
3. **Consulta por cidade:** foi integrada a API de geocodificação do Open-Meteo para localizar cidades e obter suas coordenadas.
4. **Dados meteorológicos atuais:** foram exibidos temperatura, sensação térmica, umidade, vento e descrição do tempo.
5. **Escalas de temperatura:** foram adicionadas opções para Celsius, Fahrenheit e Kelvin.
6. **Previsão de cinco dias:** o projeto passou a consultar mínimas, máximas e acumulado de chuva.
7. **Geolocalização:** foi implementada a consulta de clima pelas coordenadas fornecidas pelo navegador.
8. **Cidades favoritas:** favoritos passaram a ser armazenados no navegador com `localStorage`.
9. **Renomeação:** o arquivo principal recebeu o nome `previsao_do_tempo.py`.
10. **Publicação:** o projeto foi organizado como repositório Git para compartilhamento no GitHub.

## Fonte dos dados

Os dados geográficos e meteorológicos são fornecidos pela [Open-Meteo](https://open-meteo.com/).
