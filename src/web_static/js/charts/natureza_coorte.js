import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/natureza_coorte.csv';

export async function renderNaturezaCoorteChart() {
  const canvas = document.getElementById('chartNaturezaCoorte');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem dados de evolução temporal no arquivo mestre.');
    return;
  }

  if (!rows.length) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem registros para o gráfico de evolução temporal.');
    return;
  }

  const anos = [...new Set(rows.map((r) => String(r.coorte_ano)))].sort();
  const naturezas = [...new Set(rows.map((r) => r.natureza_participacao))].sort();

  const datasets = naturezas.map((natureza, index) => ({
    label: natureza,
    data: anos.map((ano) => {
      const row = rows.find((r) => String(r.coorte_ano) === ano && r.natureza_participacao === natureza);
      return row ? Number(row.qtd) : 0;
    }),
    borderColor: getColorByIndex(index),
    backgroundColor: getColorByIndex(index),
    tension: 0.3,
    fill: false,
  }));

  new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: { labels: anos, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: 'Ano de Ingresso' },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Quantidade de Alunos' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
      },
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed.y ?? 0;
              return `${context.dataset.label}: ${numberFormatter.format(value)} alunos`;
            },
          },
        },
      },
    },
  });
}
