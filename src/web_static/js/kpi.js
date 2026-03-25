import { loadCSV } from './utils/csv.js';
import { numberFormatter, percentFormatter } from './utils/helpers.js';

const DATASET_PATH = 'datasets/natureza_participacao.csv';

async function carregarKPIs() {
  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch {
    return;
  }

  if (!rows.length) return;

  const total = rows.reduce((soma, r) => soma + Number(r.qtd || 0), 0);

  function encontrar(natureza) {
    return rows.find(
      (r) => (r.Natureza_Participacao || r.natureza_participacao || '').trim() === natureza,
    );
  }

  const rowPresencial = encontrar('Presencial');
  const rowEAD = encontrar('A Distância');

  const qtdPresencial = rowPresencial ? Number(rowPresencial.qtd) : 0;
  const qtdEAD = rowEAD ? Number(rowEAD.qtd) : 0;

  function pct(valor) {
    return total ? (valor / total) * 100 : 0;
  }

  function preencher(id, valor) {
    const el = document.getElementById(id);
    if (el) el.textContent = valor;
  }

  preencher('kpiTotal', numberFormatter.format(total));
  preencher('kpiPresencial', numberFormatter.format(qtdPresencial));
  preencher('kpiPresencialPct', `${percentFormatter.format(pct(qtdPresencial))}%`);
  preencher('kpiEAD', numberFormatter.format(qtdEAD));
  preencher('kpiEADPct', `${percentFormatter.format(pct(qtdEAD))}%`);
}

document.addEventListener('DOMContentLoaded', carregarKPIs);
