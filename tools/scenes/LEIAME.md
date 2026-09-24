# Cenas SVG do portal de rastreio

Animações por cliente (cor, logo e personalidade da marca) que substituem os GIFs/Lottie do cartão de status.
O portal só carrega `static/scenes/<cliente>.js` (gerado); nada aqui roda em produção.

## Arquivos
| Arquivo | O que é |
|---|---|
| `scenes.py` | **Fonte da verdade**: kits dos clientes (`KITS`) e as 9 cenas (`SCENE_FUNCS`). Mudou uma cena, muda para todos. |
| `build.py` | Gera `static/scenes/<cliente>.js` (`python tools/scenes/build.py` = todos; ou passe o slug). Só usa a biblioteca padrão. |
| `logos_vetor.py` | Logos em vetor (GERADO). É o que deixa o logo nítido em qualquer tamanho. |
| `vetorizar_logo.py` | Regenera `logos_vetor.py` a partir dos PNGs de `static/logos` (`pip install scikit-image scipy pillow numpy`, só no build). |

## Regras do desenho
- Menos texto: só o balão do "Insucesso" tem texto (fonte Inter, já carregada pelo portal).
- Sem GIF e sem dependência: CSS `@keyframes` dentro do SVG, com prefixo único por cliente+status.
- `prefers-reduced-motion` mostra o quadro estático.
- CCXP não tem `atencao`, `devolucao` nem `devolvido` (o front usa a animação de reenvio própria, `resolveCcXpTreatment`).
- O gerador tem `assert` de colisão do logo com telhado/vão. Depois de mexer em medidas, confira em zoom.

## Fluxo de mudança
1. Edite `scenes.py` (ou o kit do cliente).
2. `python tools/scenes/build.py`
3. `python -m unittest discover -s tests` (confere arquivos em dia, status, recursos locais, manifesto, lista de clientes).
4. Suba `VERSAO_CENAS` em `static/tracking_publico.js` e o `?v=` do script em `templates/tracking_publico.html` (cache do navegador).
5. Deploy pelo workflow manual.

## Cliente novo
1. Kit em `KITS` (cores, `prop`, `vetor`) e, se o logo for PNG comum, entrada em `vetorizar_logo.CLIENTES` + `python tools/scenes/vetorizar_logo.py <slug>`.
2. Slug em `CLIENTES_COM_CENAS` (`static/tracking_publico.js`) e linha `static/scenes/<slug>.js` no `deploy/deploy-manifest.tsv`.
3. Passos 2 a 5 acima.

## Observações
- `static/logos/logo-ccxp.png` é só a fonte do vetor do CCXP (extraída do cabeçalho do portal); não vai no manifesto.
- `logo-panini-cena*.png` são versões reduzidas do logo ilustrado da Panini (ele não vira vetor limpo): entram no manifesto.
- Sem gzip no nginx cada arquivo de cenas pesa 120 a 200 KB; ligar `gzip on` derruba isso para ~20 a 30 KB.
