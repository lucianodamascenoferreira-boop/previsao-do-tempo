from __future__ import annotations

import math

import requests
from flask import Flask, render_template_string, request


app = Flask(__name__)

ESCALAS = {
    "celsius": {"rotulo": "Celsius", "simbolo": "°C"},
    "fahrenheit": {"rotulo": "Fahrenheit", "simbolo": "°F"},
    "kelvin": {"rotulo": "Kelvin", "simbolo": "K"},
}

TEMPOS = {
    0: "Ceu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com geada",
    51: "Garoa fraca",
    53: "Garoa moderada",
    55: "Garoa intensa",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva intensa",
    71: "Neve fraca",
    73: "Neve moderada",
    75: "Neve intensa",
    80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva fortes",
    82: "Pancadas de chuva intensas",
    95: "Trovoada",
    96: "Trovoada com granizo fraco",
    99: "Trovoada com granizo forte",
}

HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Consulta do Clima</title>
  <style>
    :root {
      --azul: #2563eb;
      --azul-escuro: #1e40af;
      --texto: #172033;
      --cinza: #64748b;
      --borda: #dbe3ef;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", Arial, sans-serif;
      color: var(--texto);
      background:
        radial-gradient(circle at 15% 15%, rgba(96, 165, 250, .28), transparent 32%),
        linear-gradient(135deg, #eef4ff, #f8fafc);
    }
    main { width: min(980px, 92vw); margin: 48px auto; }
    header { text-align: center; margin-bottom: 24px; }
    h1 { margin: 0 0 8px; font-size: 32px; }
    header p { margin: 0; color: var(--cinza); }
    .painel {
      border-radius: 18px;
      padding: 28px;
      background: rgba(255, 255, 255, .96);
      box-shadow: 0 14px 40px rgba(30, 64, 175, .12);
    }
    form { display: grid; grid-template-columns: 1fr 190px auto; gap: 12px; align-items: end; }
    label { display: block; margin-bottom: 8px; font-weight: 700; }
    input, select, button {
      width: 100%;
      height: 46px;
      border-radius: 8px;
      font: inherit;
    }
    input, select { border: 1px solid var(--borda); padding: 0 14px; }
    input:focus, select:focus { outline: 3px solid #bfdbfe; border-color: var(--azul); }
    button {
      border: 0;
      padding: 0 22px;
      background: var(--azul);
      color: white;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { background: var(--azul-escuro); }
    .erro {
      margin: 18px 0 0;
      padding: 12px 14px;
      border-radius: 8px;
      background: #fee2e2;
      color: #991b1b;
    }
    .resultado { margin-top: 24px; }
    .local { margin-bottom: 18px; }
    .local h2 { margin: 0 0 4px; font-size: 25px; }
    .local p { margin: 0; color: var(--cinza); }
    .grade { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .item {
      min-height: 112px;
      padding: 18px;
      border: 1px solid var(--borda);
      border-radius: 12px;
      background: #f8fafc;
    }
    .item span { display: block; margin-bottom: 8px; color: var(--cinza); font-size: 13px; }
    .item strong { font-size: 24px; }
    .principal { grid-column: span 2; background: #eff6ff; }
    .acoes, .favoritos { display:flex; gap:10px; flex-wrap:wrap; margin-top:12px; }
    .acao, .favorito {
      width:auto; height:38px; padding:0 14px; border:1px solid var(--borda);
      border-radius:8px; background:white; color:var(--texto); font-weight:600; cursor:pointer;
    }
    .acao.primaria { border-color:var(--azul); background:var(--azul); color:white; }
    .previsao { margin-top:24px; }
    .previsao h3 { margin-bottom:12px; }
    .dias { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; }
    .dia { text-align:center; }
    .dia strong { display:block; margin-bottom:10px; font-size:15px; }
    .dia .chuva { margin-top:8px; color:var(--cinza); font-size:13px; }
    .dia .condicao { min-height:38px; font-size:13px; }
    @media (max-width: 760px) {
      main { margin: 24px auto; }
      form { grid-template-columns: 1fr; }
      .grade { grid-template-columns: repeat(2, 1fr); }
      .principal { grid-column: span 2; }
      .dias { grid-template-columns:repeat(2,1fr); }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Consulta do Clima</h1>
      <p>Pesquise o clima atual por nome da cidade.</p>
    </header>
    <section class="painel">
      <form method="post">
        <div>
          <label for="cidade">Cidade</label>
          <input id="cidade" name="cidade" value="{{ cidade }}" placeholder="Exemplo: Sao Paulo" required>
        </div>
        <div>
          <label for="escala">Temperatura</label>
          <select id="escala" name="escala">
            {% for chave, escala in escalas.items() %}
              <option value="{{ chave }}" {% if chave == escala_selecionada %}selected{% endif %}>{{ escala.rotulo }}</option>
            {% endfor %}
          </select>
        </div>
        <button type="submit">Consultar</button>
      </form>
      <div class="acoes">
        <button class="acao primaria" id="usar-localizacao" type="button">Usar minha localizacao</button>
        <button class="acao" id="salvar-favorito" type="button" hidden>Salvar cidade favorita</button>
      </div>
      <div class="favoritos" id="lista-favoritos"></div>

      {% if erro %}
        <p class="erro" role="alert">{{ erro }}</p>
      {% endif %}

      {% if clima %}
        <div class="resultado">
          <div class="local">
            <h2>{{ clima.cidade }}, {{ clima.pais }}</h2>
            <p>{{ clima.tempo }}</p>
          </div>
          <div class="grade">
            <article class="item principal">
              <span>Temperatura atual</span>
              <strong>{{ clima.temperatura }} {{ simbolo }}</strong>
            </article>
            <article class="item principal">
              <span>Sensacao termica</span>
              <strong>{{ clima.sensacao }} {{ simbolo }}</strong>
            </article>
            <article class="item"><span>Umidade</span><strong>{{ clima.umidade }}%</strong></article>
            <article class="item"><span>Vento</span><strong>{{ clima.vento }} km/h</strong></article>
          </div>
          {% if previsao %}
            <section class="previsao">
              <h3>Previsao para os proximos 5 dias</h3>
              <div class="dias">
                {% for dia in previsao %}
                  <article class="item dia">
                    <strong>{{ dia.data }}</strong>
                    <div class="condicao">{{ dia.tempo }}</div>
                    <strong>{{ dia.minima }} / {{ dia.maxima }} {{ simbolo }}</strong>
                    <div class="chuva">{{ dia.chuva }} mm de chuva</div>
                  </article>
                {% endfor %}
              </div>
            </section>
          {% endif %}
        </div>
      {% endif %}
    </section>
  </main>
  <script>
    const escala = document.getElementById("escala");
    const cidade = document.getElementById("cidade");
    const chaveFavoritos = "clima_favoritos";
    const favoritos = JSON.parse(localStorage.getItem(chaveFavoritos) || "[]");
    const lista = document.getElementById("lista-favoritos");
    const botaoFavorito = document.getElementById("salvar-favorito");

    function salvarFavoritos() {
      localStorage.setItem(chaveFavoritos, JSON.stringify(favoritos));
      renderizarFavoritos();
    }

    function renderizarFavoritos() {
      lista.innerHTML = favoritos.map((nome, indice) =>
        `<button type="button" class="favorito" data-indice="${indice}">${nome} x</button>`
      ).join("");
      lista.querySelectorAll("button").forEach(botao => {
        botao.addEventListener("click", () => {
          const nome = favoritos[Number(botao.dataset.indice)];
          if (event.detail === 2) {
            favoritos.splice(Number(botao.dataset.indice), 1);
            salvarFavoritos();
          } else {
            cidade.value = nome;
            document.querySelector("form").requestSubmit();
          }
        });
      });
    }

    botaoFavorito.addEventListener("click", () => {
      const nome = cidade.value.trim();
      if (nome && !favoritos.some(item => item.toLowerCase() === nome.toLowerCase())) {
        favoritos.push(nome);
        salvarFavoritos();
      }
    });

    renderizarFavoritos();
    {% if clima %}
      botaoFavorito.hidden = false;
    {% endif %}

    document.getElementById("usar-localizacao").addEventListener("click", () => {
      if (!navigator.geolocation) {
        alert("Seu navegador nao suporta geolocalizacao.");
        return;
      }
      navigator.geolocation.getCurrentPosition(async posicao => {
        const formulario = new FormData();
        formulario.append("latitude", posicao.coords.latitude);
        formulario.append("longitude", posicao.coords.longitude);
        formulario.append("escala", escala.value);
        const resposta = await fetch("/coordenadas", { method: "POST", body: formulario });
        if (!resposta.ok) {
          alert("Nao foi possivel consultar o clima da sua localizacao.");
          return;
        }
        document.open();
        document.write(await resposta.text());
        document.close();
      }, () => alert("Permissao de localizacao negada ou localizacao indisponivel."));
    });
  </script>
</body>
</html>
"""


def converter_temperatura(celsius: float, escala: str) -> float:
    if escala == "fahrenheit":
        return celsius * 9 / 5 + 32
    if escala == "kelvin":
        return celsius + 273.15
    return celsius


def consultar_geocodificacao(cidade: str) -> dict | None:
    resposta = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": cidade, "count": 1, "language": "pt", "format": "json"},
        timeout=10,
    )
    resposta.raise_for_status()
    resultados = resposta.json().get("results", [])
    return resultados[0] if resultados else None


def consultar_clima(latitude: float, longitude: float) -> dict:
    resposta = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
            "forecast_days": 5,
            "timezone": "auto",
        },
        timeout=10,
    )
    resposta.raise_for_status()
    dados = resposta.json()
    return {"atual": dados["current"], "diario": dados["daily"]}


def montar_previsao(dados_diarios: dict, escala: str) -> list[dict]:
    from datetime import datetime

    previsao = []
    for indice, data in enumerate(dados_diarios["time"]):
        minima = converter_temperatura(dados_diarios["temperature_2m_min"][indice], escala)
        maxima = converter_temperatura(dados_diarios["temperature_2m_max"][indice], escala)
        codigo = dados_diarios["weather_code"][indice]
        previsao.append({
            "data": datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m"),
            "tempo": TEMPOS.get(codigo, "Condicao nao informada"),
            "minima": f"{minima:.1f}".replace(".", ","),
            "maxima": f"{maxima:.1f}".replace(".", ","),
            "chuva": f"{dados_diarios['precipitation_sum'][indice]:.1f}".replace(".", ","),
        })
    return previsao


@app.get("/")
def pagina() -> str:
    return render_template_string(
        HTML,
        cidade="",
        escala_selecionada="celsius",
        escalas=ESCALAS,
        clima=None,
        erro=None,
        simbolo=ESCALAS["celsius"]["simbolo"],
    )


@app.post("/")
def pesquisar_clima() -> str:
    cidade = request.form.get("cidade", "").strip()
    escala = request.form.get("escala", "celsius")

    if escala not in ESCALAS:
        escala = "celsius"

    if not cidade:
        erro = "Informe o nome de uma cidade."
    else:
        try:
            local = consultar_geocodificacao(cidade)
            if not local:
                erro = "Cidade nao encontrada. Verifique o nome e tente novamente."
                clima = None
            else:
                dados_clima = consultar_clima(local["latitude"], local["longitude"])
                atual = dados_clima["atual"]
                temperatura = converter_temperatura(atual["temperature_2m"], escala)
                sensacao = converter_temperatura(atual["apparent_temperature"], escala)
                previsao = montar_previsao(dados_clima["diario"], escala)

                if not all(
                    math.isfinite(valor)
                    for valor in (temperatura, sensacao, atual["relative_humidity_2m"], atual["wind_speed_10m"])
                ):
                    raise ValueError("A API retornou dados meteorologicos invalidos.")

                clima = {
                    "cidade": local["name"],
                    "pais": local.get("country_code", ""),
                    "tempo": TEMPOS.get(atual["weather_code"], "Condicao nao informada"),
                    "temperatura": f"{temperatura:.1f}".replace(".", ","),
                    "sensacao": f"{sensacao:.1f}".replace(".", ","),
                    "umidade": atual["relative_humidity_2m"],
                    "vento": f"{atual['wind_speed_10m']:.1f}".replace(".", ","),
                }
                erro = None
        except requests.RequestException:
            clima = None
            erro = "Nao foi possivel consultar o clima. Verifique sua conexao e tente novamente."
        except (KeyError, TypeError, ValueError):
            clima = None
            erro = "O servico meteorologico retornou dados incompletos. Tente novamente."

    return render_template_string(
        HTML,
        cidade=cidade,
        escala_selecionada=escala,
        escalas=ESCALAS,
        clima=clima if "clima" in locals() else None,
        previsao=previsao if "previsao" in locals() else None,
        erro=erro if "erro" in locals() else None,
        simbolo=ESCALAS[escala]["simbolo"],
    )


@app.post("/coordenadas")
def consultar_por_coordenadas() -> tuple[str, int] | str:
    escala = request.form.get("escala", "celsius")
    if escala not in ESCALAS:
        escala = "celsius"

    try:
        latitude = float(request.form["latitude"])
        longitude = float(request.form["longitude"])
        if not math.isfinite(latitude) or not math.isfinite(longitude):
            raise ValueError
        dados_clima = consultar_clima(latitude, longitude)
        atual = dados_clima["atual"]
        temperatura = converter_temperatura(atual["temperature_2m"], escala)
        sensacao = converter_temperatura(atual["apparent_temperature"], escala)
        clima = {
            "cidade": "Sua localizacao",
            "pais": f"{latitude:.2f}, {longitude:.2f}",
            "tempo": TEMPOS.get(atual["weather_code"], "Condicao nao informada"),
            "temperatura": f"{temperatura:.1f}".replace(".", ","),
            "sensacao": f"{sensacao:.1f}".replace(".", ","),
            "umidade": atual["relative_humidity_2m"],
            "vento": f"{atual['wind_speed_10m']:.1f}".replace(".", ","),
        }
        return render_template_string(
            HTML,
            cidade="",
            escala_selecionada=escala,
            escalas=ESCALAS,
            clima=clima,
            previsao=montar_previsao(dados_clima["diario"], escala),
            erro=None,
            simbolo=ESCALAS[escala]["simbolo"],
        )
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return render_template_string(
            HTML,
            cidade="",
            escala_selecionada=escala,
            escalas=ESCALAS,
            clima=None,
            previsao=None,
            erro="Nao foi possivel consultar o clima da sua localizacao.",
            simbolo=ESCALAS[escala]["simbolo"],
        ), 400


if __name__ == "__main__":
    app.run(debug=True)