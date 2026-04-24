/**
 * Mapeamento de tags internas para labels amigáveis no frontend.
 * Apenas para exibição — não altera o valor real da tag no banco.
 */
const TAG_LABELS = {
  'entrou-grupo': 'Interagiu com Boas Vindas',
  'saiu-grupo': 'Saiu do Grupo',
}

/**
 * Retorna o label amigável para uma tag, ou a própria tag se não houver mapeamento.
 * @param {string} tag
 * @returns {string}
 */
export function tagLabel(tag) {
  return TAG_LABELS[tag] ?? tag
}
