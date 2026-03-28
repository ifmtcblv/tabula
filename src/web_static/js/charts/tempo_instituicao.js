import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/tempo_instituicao.csv';

const ORDEM_FAIXAS = [
  'Menos de 6 meses',
  '6 a 12 meses',
  '1 a 2 anos',
  '2 a 3 anos',
  '3 a 4 anos',
  'Mais de 4 anos',
];

let chart;
let originalRows = [];

function processData() {
  const faixas = ORDEM_FAIXAS.filter((f) => originalRows.some((r) => r.faixa_tempo === f));
  const naturezas = [...new Set(originalRows.map((r) => r.natureza_participacao))].sort();

  const totaisPorFaixa = {};
  for (const faixa of faixas) {
    totaisPorFaixa[faixa] = originalRows
      .filter((r) => r.faixa_tempo === faixa)
      .reduce((s, r) => s + (Number(r.qtd) || 0), 0);
  }

  const datasets = naturezas.map((natureza, index) => ({
    label: natureza,
    data: faixas.map((faixa) => {
      const row = originalRows.find((r) => r.faixa_tempo === faixa && r.natureza_participacao === natureza);
      return row ? Number(row.qtd) || 0 : 0;
    }),
    backgroundColor: getColorByIndex(index),
    borderWidth: 0,
  }));

  return { faixas, datasets, totaisPorFaixa };
}

export async function renderTempoInstituicaoChart() {
  const canvas = document.getElementById('chartTempoInstituicao');
  if (!canvas) {
    return;
  }

  try {
    originalRows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem dados de tempo na instituição no arquivo mestre.');
    return;
  }

  if (!originalRows.length) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem registros para o gráfico de tempo na instituição.');
    return;
  }

  const { faixas, datasets, totaisPorFaixa } = processData();

  chart = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: { labels: faixas, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: 'Tempo desde o ingresso' },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Alunos matriculados' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
      },
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed.y ?? 0;
              const faixa = context.label;
              const total = totaisPorFaixa[faixa] || 0;
              const pct = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
              return `${context.dataset.label}: ${numberFormatter.format(value)} (${pct}%)`;
            },
            footer(items) {
              const total = totaisPorFaixa[items[0]?.label] || 0;
              return `Total: ${numberFormatter.format(total)} alunos`;
            },
          },
        },
      },
    },
  });
}
