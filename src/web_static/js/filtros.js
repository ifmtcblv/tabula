let incluirEAD = false;
const listeners = [];

export function getFiltroNatureza() {
  return incluirEAD ? ['Presencial', 'A Distância'] : ['Presencial'];
}

export function isEADIncluido() {
  return incluirEAD;
}

export function setIncluirEAD(valor) {
  incluirEAD = valor;
  listeners.forEach((fn) => fn(incluirEAD));
}

export function onFiltroChange(callback) {
  listeners.push(callback);
}
