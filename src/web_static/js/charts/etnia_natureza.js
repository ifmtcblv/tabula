
import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/etnia_natureza.csv';

let chart;
let currentGrouping = 'natureza';
let originalRows = [];

function processData(grouping) {
  const group1 = grouping === 'natureza' ? 'natureza_participacao' : 'etnia_raca';
  const group2 = grouping === 'natureza' ? 'etnia_raca' : 'natureza_participacao';

  const labels = [...new Set(originalRows.map(row => row[group1]))];
  const categories = [...new Set(originalRows.map(row => row[group2]))];

  const datasets = categories.map((category, index) => {
    return {
      label: category,
      data: labels.map(label => {
        const row = originalRows.find(r => r[group1] === label && r[group2] === category);
        return row ? Number(row.qtd) : 0;
      }),
      backgroundColor: getColorByIndex(index),
    };
  });

  return { labels, datasets };
}

function updateChart() {
  const { labels, datasets } = processData(currentGrouping);
  const group1 = currentGrouping === 'natureza' ? 'Etnia/Raça' : 'Etnia/Raça';
  const group2 = currentGrouping === 'natureza' ? 'Etnia/Raça' : 'Etnia/Raça';

  chart.data.labels = labels;
  chart.data.datasets = datasets;
  chart.options.scales.y.title.text = group1;
  chart.options.plugins.title.text = `${group1} × ${group2}`;
  chart.update();
}

export async function renderEtniaNaturezaChart() {
  const canvas = document.getElementById('chartEtniaNatureza');
  if (!canvas) {
    return;
  }

  try {
    originalRows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem dados para o gráfico de Presencial × Etnia/Raça.');
    return;
  }

  if (!originalRows.length) {
    datasetMissing(DATASET_PATH);
    renderPlaceholder(canvas, 'Sem registros para o gráfico de Presencial × Etnia/Raça.');
    return;
  }

  const { labels, datasets } = processData(currentGrouping);
  const group1 = currentGrouping === 'natureza' ? 'Presencial' : 'Etnia/Raça';
  const group2 = currentGrouping === 'natureza' ? 'Etnia/Raça' : 'Presencial';

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
          title: { display: true, text: group1 },
        },
      },
      plugins: {
        title: {
            display: true,
            text: `${group1} × ${group2}`
        },
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
      currentGrouping = currentGrouping === 'natureza' ? 'etnia' : 'natureza';
      updateChart();
    });
  }
}
