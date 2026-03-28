import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/turno_escola.csv';

let chart;
let currentGrouping = 'turno';
let originalRows = [];

function processData(grouping) {
  const group1 = grouping === 'turno' ? 'turno' : 'tipo_escola_origem';
  const group2 = grouping === 'turno' ? 'tipo_escola_origem' : 'turno';

  const labels = [...new Set(originalRows.map((row) => row[group1]))];
  const categories = [...new Set(originalRows.map((row) => row[group2]))].sort();

  const datasets = categories.map((category, index) => {
    return {
      label: category,
      data: labels.map((label) => {
        const row = originalRows.find(
          (r) => r[group1] === label && r[group2] === category
        );
        return row ? Number(row.qtd) : 0;
      }),
      backgroundColor: getColorByIndex(index),
    };
  });

  return { labels, datasets };
}

function updateChart() {
  const { labels, datasets } = processData(currentGrouping);
  const group1Name =
    currentGrouping === 'turno'
      ? 'Turno'
      : 'Tipo de Escola de Origem';

  chart.data.labels = labels;
  chart.data.datasets = datasets;
  chart.options.scales.y.title.text = group1Name;
  chart.update();
}

export async function renderTurnoEscolaChart() {
  const canvas = document.getElementById('chartTurnoEscola');
  if (!canvas) return;

  try {
    originalRows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem dados para o gráfico de Turno × Tipo de Escola.');
    return;
  }

  if (!originalRows.length) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem registros para o gráfico de Turno × Tipo de Escola.');
    return;
  }

  const { labels, datasets } = processData(currentGrouping);
  const group1Name =
    currentGrouping === 'turno'
      ? 'Turno'
      : 'Tipo de Escola de Origem';

  const ctx = canvas.getContext('2d');
  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          stacked: true,
          title: { display: true, text: 'Quantidade de Alunos' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
        y: {
          stacked: true,
          title: { display: true, text: group1Name },
        },
      },
      plugins: {
        legend: {
          position: 'top',
        },
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
      currentGrouping = currentGrouping === 'turno' ? 'escola' : 'turno';
      updateChart();
    });
  }
}
