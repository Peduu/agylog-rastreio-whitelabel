# Dados geográficos do cartão "Onde está seu pedido"

Gerados por `tools/geo/preparar_geo.py` em 08/10/2026. Não editar à mão.

## `data/municipios.json` (sede de cada município; JSON porque o repositório ignora `*.csv`)
Fonte: https://github.com/kelvins/municipios-brasileiros (`csv/municipios.csv`), dados do IBGE. Licença MIT:

```
MIT License

Copyright (c) 2016 Kelvin S. do Prado

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## `static/data/uf/*.json` (contornos das UFs)
Fonte: IBGE, API de malhas v3, país BR por UF, qualidade intermediária:
https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&intrarregiao=UF&qualidade=intermediaria

## `static/flags/uf/*.png` (bandeiras das UFs, 72 px de largura)
Fonte: Wikidata (propriedade P41, imagem da bandeira) → Wikimedia Commons, miniatura gerada pelo próprio Commons.

| UF | Arquivo no Commons | Licença |
|---|---|---|
| AC | Bandeira do Acre.svg | Public domain |
| AL | Bandeira de Alagoas.svg | Public domain |
| AM | Bandeira do Amazonas.svg | Public domain |
| AP | Bandeira do Amapá.svg | Public domain |
| BA | Bandeira da Bahia.svg | Public domain |
| CE | Bandeira do Ceará.svg | Public domain |
| DF | Bandeira do Distrito Federal (Brasil).svg | Public domain |
| ES | Bandeira do Espírito Santo.svg | Public domain |
| GO | Flag of Goiás.svg | Public domain |
| MA | Bandeira do Maranhão.svg | Public domain |
| MG | Bandeira de Minas Gerais.svg | Public domain |
| MS | Bandeira de Mato Grosso do Sul.svg | Public domain |
| MT | Bandeira de Mato Grosso.svg | Public domain |
| PA | Bandeira do Pará.svg | Public domain |
| PB | Bandeira da Paraíba.svg | Public domain |
| PE | Bandeira de Pernambuco.svg | Public domain |
| PI | Bandeira do Piauí.svg | Public domain |
| PR | Bandeira do Paraná.svg | Public domain |
| RJ | Bandeira do estado do Rio de Janeiro.svg | Public domain |
| RN | Bandeira do Rio Grande do Norte.svg | Public domain |
| RO | Bandeira de Rondônia.svg | Public domain |
| RR | Bandeira de Roraima.svg | Public domain |
| RS | Bandeira do Rio Grande do Sul.svg | Public domain |
| SC | Bandeira de Santa Catarina.svg | Public domain |
| SE | Bandeira de Sergipe.svg | Public domain |
| SP | Bandeira do estado de São Paulo.svg | Public domain |
| TO | Bandeira do Tocantins.svg | Public domain |
