import locale

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

from models import FundoImobiliario, Estrategia

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
locale.localeconv()


def trata_porcentagem(porcentagem_str):
    return locale.atof(porcentagem_str.split('%')[0])


def trata_decimal(decimal_str):
    return locale.atof(decimal_str)


# Foi necessário criar esse headers, pois a requisição voltava como 400
headers = {'User-Agent': 'Mozilla/5.0'}

# Como o método de chamada é um get, foi utilizado requests.get.
# Essa linha é encontrada na documentação.
res = requests.get('https://www.fundamentus.com.br/fii_resultado.php',
                   headers=headers)

# A chamada do soup como text traz a cópia da página em parser
soup = BeautifulSoup(res.text, 'html.parser')

# Aqui fomos entrando em cada um dos elementos até chegarmos onde queríamos.
# Como não pode usar um findAll após um findAll, fizemos o for abaixo.
lines = soup.find(id='tabelaResultado').find('tbody').findAll('tr')

resultado = []

estrategia = Estrategia(
    cotacao_atual_minima=50.0,
    dividend_yield_minimo=5,
    p_vp_minimo=0.70,
    valor_mercado_minimo=200000000,
    liquidez_minima=50000,
    qt_minima_imoveis=5,
    maxima_vacancia_media=10
)

for line in lines:
    data = line.findAll('td')
    codigo = data[0].text
    segmento = data[1].text
    cotacao = locale.atof(data[2].text)
    ffo_yield = trata_porcentagem(data[3].text)
    dividend_yield = trata_porcentagem(data[4].text)
    p_vp = trata_decimal(data[5].text)
    valor_mercado = trata_decimal(data[6].text)
    liquidez = trata_decimal(data[7].text)
    qt_imoveis = int(data[8].text)
    preco_m2 = trata_decimal(data[9].text)
    aluguel_m2 = trata_decimal(data[10].text)
    cap_rate = trata_porcentagem(data[11].text)
    vacancia = trata_porcentagem(data[12].text)

    fundo_imobiliario = FundoImobiliario(
        codigo, segmento, cotacao, ffo_yield, dividend_yield, p_vp,
        valor_mercado, liquidez,
        qt_imoveis, preco_m2, aluguel_m2, cap_rate, vacancia
    )

    if estrategia.aplica_estrategia(fundo_imobiliario):
        resultado.append(fundo_imobiliario)

cabecalho = ["CÓDIGO", "SEGMENTO", "COTAÇÃO ATUAL", "DIVIDEND YIELD"]

tabela = []

for elemento in resultado:
    tabela.append([
        elemento.codigo,
        elemento.segmento,
        f'R$ {locale.format_string("%.2f", elemento.cotacao_atual)}',
        f'{locale.str(elemento.dividend_yield)}%'
    ])

print(tabulate(tabela, headers=cabecalho, showindex='always',
               tablefmt='fancy_grid'))
