import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getStatusColor,
  numberFormatter,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/forma_ingresso_situacao.csv';

let chart;
let currentGrouping = 'forma';
let originalRows = [];

function processData(grouping) {
  const group1 = grouping === 'forma' ? 'forma_ingresso' : 'status_simplificado';
  const group2 = grouping === 'forma' ? 'status_simplificado' : 'forma_ingresso';

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
      backgroundColor:
        grouping === 'forma'
          ? getStatusColor(category, index)
          : undefined,
    };
  });

  return { labels, datasets };
}

function updateChart() {
  const { labels, datasets } = processData(currentGrouping);
  const group1Name =
    currentGrouping === 'forma'
      ? 'Forma de Ingresso'
      : 'Situação no Curso';

  chart.data.labels = labels;
  chart.data.datasets = datasets;
  chart.options.scales.y.title.text = group1Name;
  chart.update();
}

export async function renderFormaIngressoSituacaoChart() {
  const canvas = document.getElementById('chartFormaIngressoSituacao');
  if (!canvas) return;

  try {
    originalRows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem dados para o gráfico de Forma de Ingresso × Situação.');
    return;
  }

  if (!originalRows.length) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem registros para o gráfico de Forma de Ingresso × Situação.');
    return;
  }

  const { labels, datasets } = processData(currentGrouping);
  const group1Name =
    currentGrouping === 'forma'
      ? 'Forma de Ingresso'
      : 'Situação no Curso';

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
      currentGrouping = currentGrouping === 'forma' ? 'situacao' : 'forma';
      updateChart();
    });
  }
}
