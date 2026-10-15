# Recarga do prazo de entrega (vistoria de 15/10/2026)

Gera, a partir do relatório de entregas do TMS (CSV latin1, `;`) e da abrangência do TMS, a carga das tabelas
`prazos_tms` (prazo registrado por pedido), `prazos_cep_cliente`, `prazos_cep_bloqueio` e `prazos_cep_liberado`,
e confere com o `prazo_cep.py` (teste cego + página com a carga). O relatório tem dado pessoal: rodar só no PC,
com `python -I`, fora da pasta dos downloads. Nada de dado vai para o repositório (público) nem para o log.

1. `python -I tools/prazo/gerar_carga.py <entregas.csv> <abrangencia.csv> <raiz do repo> <pasta de saida>`
   (saída: `parte1.b64`... com até 45 mil caracteres cada; só vale subir se o teste cego der 0 erro).
2. `python tools/prazo/gerar_yaml_carga.py tools/prazo/carga_servidor.py .github/workflows/prazo-vistoria-uso-unico.yml <N partes>`
   na `main`; segredos `PRAZO_VIST_1..N` com as partes.
3. Rodar o workflow sem `confirmar` (só relata), depois com `confirmar = CARREGAR` (backup do banco antes, confere
   28 pedidos na página). Apagar o workflow e os segredos depois.
