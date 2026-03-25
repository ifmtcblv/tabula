import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/campus_natureza.csv';

let chart;
let currentGrouping = 'campus'; // 'campus' or 'natureza'
let originalRows = [];

function processData(grouping) {
  const col1 = grouping === 'campus' ? 'campus' : 'natureza_participacao';
  const col2 = grouping === 'campus' ? 'natureza_participacao' : 'campus';

  const labels = [...new Set(originalRows.map((r) => r[col1]))].sort();
  const categories = [...new Set(originalRows.map((r) => r[col2]))].sort();

  const datasets = categories.map((category, index) => ({
    label: category,
    data: labels.map((label) => {
      const row = originalRows.find((r) => r[col1] === label && r[col2] === category);
      return row ? Number(row.qtd) : 0;
    }),
    backgroundColor: getColorByIndex(index),
  }));

  return { labels, datasets };
}

const LABELS = {
  campus: 'Campus',
  natureza: 'Natureza de Participação',
};

function updateChart() {
  const { labels, datasets } = processData(currentGrouping);
  chart.data.labels = labels;
  chart.data.datasets = datasets;
  chart.options.scales.y.title.text =
    currentGrouping === 'campus' ? LABELS.campus : LABELS.natureza;
  chart.update();
}

export async function renderCampusNaturezaChart() {
  const canvas = document.getElementById('chartCampusNatureza');
  if (!canvas) return;

  try {
    originalRows = await loadCSV(DATASET_PATH);
  } catch {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem dados de campus por natureza de participação no arquivo mestre.');
    return;
  }

  if (!originalRows.length) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem registros para o gráfico de Campus × Natureza.');
    return;
  }

  const { labels, datasets } = processData(currentGrouping);

  chart = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          stacked: true,
          beginAtZero: true,
          title: { display: true, text: 'Quantidade de Alunos' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
        y: {
          stacked: true,
          title: { display: true, text: LABELS.campus },
        },
      },
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed.x ?? 0;
              return `${context.dataset.label}: ${numberFormatter.format(value)} alunos`;
            },
          },
        },
      },
    },
  });

  const switchButton = document.getElementById('switchGroup');
  if (switchButton) {
    switchButton.addEventListener('click', () => {
      currentGrouping = currentGrouping === 'campus' ? 'natureza' : 'campus';
      updateChart();
    });
  }
}
