import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  numberFormatter,
  percentFormatter,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_SITUACAO = 'datasets/alunos_por_situacao_presencial.csv';
const DATASET_MODALIDADE = 'datasets/modalidade_presencial.csv';
const DATASET_PROFESSORES = 'datasets/professores.csv';

const METAS = {
  alunoProfessor: 20,
  ensinoTecnico: 50,
};

export async function renderCriteriosOrcamentariosChart() {
  const canvas = document.getElementById('chartCriteriosOrcamentarios');
  if (!canvas) {
    return;
  }

  try {
    let professoresRows = [];
    try {
      professoresRows = await loadCSV(DATASET_PROFESSORES);
    } catch (error) {
      console.warn('Dataset de professores não encontrado');
    }

    let situacaoRows = [];
    let modalidadeRows = [];
    try {
      situacaoRows = await loadCSV(DATASET_SITUACAO);
    } catch (error) {
      console.error('Erro ao carregar situacao:', error);
    }
    try {
      modalidadeRows = await loadCSV(DATASET_MODALIDADE);
    } catch (error) {
      console.error('Erro ao carregar modalidade:', error);
    }

    if (situacaoRows.length === 0 || modalidadeRows.length === 0) {
      console.error('Dados insuficientes para renderizar');
      renderPlaceholder(canvas, 'Dados insuficientes para exibir.');
      return;
    }

    const criterios = [];

    const numProfessores = professoresRows.length > 0 ? Number(professoresRows[0].qtd_professores || 0) : 0;
    const totalAlunos = situacaoRows.reduce((sum, r) => sum + Number(r.qtd || 0), 0);
    const relacaoAlunoProfessor = numProfessores > 0 ? totalAlunos / numProfessores : 0;

    criterios.push({
      label: 'Ratio Aluno/Professor',
      valor: relacaoAlunoProfessor,
      meta: METAS.alunoProfessor,
      unidade: 'alunos/prof',
      tipo: 'numerico',
      metaLabel: 'Referência: 20:1',
      detalhe: numProfessores > 0 ? `${numberFormatter.format(totalAlunos)} alunos / ${numProfessores} professores` : 'Dados de professores não disponíveis',
      cor: '#1976d2',
    });

    const concluidos = situacaoRows.find(
      (r) => (r.Situacao || r.situacao || '').trim() === 'Concluído',
    );
    const formados = situacaoRows.find(
      (r) => (r.Situacao || r.situacao || '').trim() === 'Formado',
    );
    const evasao = situacaoRows.find(
      (r) => (r.Situacao || r.situacao || '').trim() === 'Evasão',
    );
    const cancelado = situacaoRows.find(
      (r) => (r.Situacao || r.situacao || '').trim() === 'Cancelado',
    );

    const qtdConcluidos = concluidos ? Number(concluidos.qtd || 0) : 0;
    const qtdFormados = formados ? Number(formados.qtd || 0) : 0;
    const qtdEvasao = evasao ? Number(evasao.qtd || 0) : 0;
    const qtdCancelado = cancelado ? Number(cancelado.qtd || 0) : 0;
    const qtdNaoConcluido = situacaoRows.find((r) => (r.Situacao || r.situacao || '').trim() === 'Não concluído');
    const qtdNaoConcluidoValor = qtdNaoConcluido ? Number(qtdNaoConcluido.qtd || 0) : 0;

    const totalIngressantes = qtdConcluidos + qtdFormados + qtdEvasao + qtdCancelado + qtdNaoConcluidoValor;
    const eficiencia = totalIngressantes > 0 ? ((qtdConcluidos + qtdFormados) / totalIngressantes) * 100 : 0;

    criterios.push({
      label: 'Taxa de Conclusão',
      valor: eficiencia,
      meta: 100,
      unidade: '%',
      tipo: 'percentual',
      metaLabel: 'Estudantes que concluíram no ciclo',
      detalhe: `${qtdConcluidos + qtdFormados} concluídos de ${totalIngressantes} ingressantes`,
      cor: '#2e7d32',
    });

    const tecnicoIntegrado = modalidadeRows.find(
      (r) => (r.Modalidade || r.modalidade || '').trim() === 'Técnico Integrado',
    );
    const tecnicoSubsequente = modalidadeRows.find(
      (r) => (r.Modalidade || r.modalidade || '').trim() === 'Técnico Subsequente',
    );

    const qtdTecnicoIntegrado = tecnicoIntegrado ? Number(tecnicoIntegrado.qtd || 0) : 0;
    const qtdTecnicoSubsequente = tecnicoSubsequente ? Number(tecnicoSubsequente.qtd || 0) : 0;
    const totalModalidades = modalidadeRows.reduce((sum, r) => sum + Number(r.qtd || 0), 0);

    const pctTecnicos = totalModalidades > 0 ? ((qtdTecnicoIntegrado + qtdTecnicoSubsequente) / totalModalidades) * 100 : 0;

    criterios.push({
      label: 'Alunos em Cursos Técnicos',
      valor: pctTecnicos,
      meta: METAS.ensinoTecnico,
      unidade: '%',
      tipo: 'percentual',
      metaLabel: 'Referência: 50%',
      detalhe: `${qtdTecnicoIntegrado + qtdTecnicoSubsequente} técnicos de ${totalModalidades} alunos`,
      cor: '#f9a825',
    });

    const labels = criterios.map((c) => c.label);
    const valores = criterios.map((c) => c.valor);
    const metas = criterios.map((c) => c.meta);
    const cores = criterios.map((c) => c.cor);

    const ctx = canvas.getContext('2d');

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Valor Atual',
            data: valores,
            backgroundColor: cores,
            borderRadius: 6,
            borderWidth: 2,
            borderColor: cores,
          },
          {
            label: 'Meta',
            data: metas,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            borderColor: 'rgba(0, 0, 0, 0.3)',
            borderWidth: 2,
            borderRadius: 6,
            borderDash: [5, 5],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
            },
          },
          tooltip: {
            callbacks: {
              afterLabel(context) {
                const criterio = criterios[context.dataIndex];
                if (criterio.observacao) {
                  return criterio.observacao;
                }
                if (criterio.detalhe) {
                  return criterio.detalhe;
                }
                if (criterio.metaLabel) {
                  return criterio.metaLabel;
                }
                return '';
              },
            },
          },
          title: {
            display: true,
            text: 'Indicadores do Campus',
            font: {
              size: 16,
              weight: 'bold',
            },
            padding: {
              bottom: 20,
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Valor',
            },
          },
          y: {
            grid: {
              display: false,
            },
          },
        },
      },
    });

    const kpiContainer = document.getElementById('kpiCriterios');
    if (kpiContainer) {
      kpiContainer.innerHTML = `
        <div class="kpi-grid">
          ${criterios.map(
            (c) => `
            <div class="kpi-card" style="border-left: 4px solid ${c.cor}">
              <div class="kpi-label">${c.label}</div>
              <div class="kpi-valor">
                ${c.tipo === 'percentual' ? percentFormatter.format(c.valor) : numberFormatter.format(c.valor)}${c.unidade}
              </div>
              <div class="kpi-meta">Meta: ${c.tipo === 'percentual' ? percentFormatter.format(c.meta) : numberFormatter.format(c.meta)}${c.unidade}</div>
              ${c.observacao ? `<div class="kpi-observacao">${c.observacao}</div>` : ''}
              ${c.detalhe ? `<div class="kpi-detalhe">${c.detalhe}</div>` : ''}
              ${c.metaLabel ? `<div class="kpi-meta-label">${c.metaLabel}</div>` : ''}
            </div>
          `,
          ).join('')}
        </div>
      `;
    }
  } catch (error) {
    console.error('Erro ao carregar dados:', error);
    datasetMissing('datasets de critérios orçamentários');
    renderPlaceholder(canvas, 'Erro ao carregar dados dos critérios orçamentários.');
  }
}
