import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  percentFormatter,
  percentage,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/etnia_raca.csv';

export async function renderEtniaChart() {
  const canvas = document.getElementById('chartEtnia');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing('etnia_raca.csv');
    renderPlaceholder(canvas, 'Sem dados de etnia/raça no arquivo mestre.');
    return;
  }

  if (!rows.length) {
    datasetMissing('etnia_raca.csv');
    renderPlaceholder(canvas, 'Sem registros de etnia/raça para exibir.');
    return;
  }

  const items = rows
    .map((row) => ({
      label: row.Etnia_Raca || row.etnia_raca || 'Não informado',
      value: Number(row.qtd || row.Qtd || 0) || 0,
    }))
    .filter((item) => item.label && item.label.length > 0)
    .sort((a, b) => b.value - a.value);

  if (!items.length) {
    renderPlaceholder(canvas, 'Categorias de etnia não informadas.');
    return;
  }

  const total = items.reduce((sum, item) => sum + item.value, 0);
  const labels = items.map((item) => item.label);
  const values = items.map((item) => item.value);

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Alunos',
          data: values,
          backgroundColor: labels.map((_, index) => getColorByIndex(index)),
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          title: { display: true, text: 'Quantidade de Alunos' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
        y: { title: { display: true, text: 'Etnia/Raça' } },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed.x ?? 0;
              const pct = percentage(value, total);
              return `${numberFormatter.format(value)} alunos (${percentFormatter.format(pct)}%)`;
            },
          },
        },
      },
    },
  });
}
