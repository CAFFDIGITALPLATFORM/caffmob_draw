"""071, correção da importação (LIMITS e NORMAL): armários, peças espelhadas e peças em outras superfícies.

Conferido nos projetos do titular: `LIMITS` é a caixa do item a partir do ponto base (peça espelhada tem x ∈ [−W, 0]),
e `NORMAL` é o eixo da altura (a cama do Promob tem a normal em +Y e fica deitada).
"""
import unittest

import _promob_sintetico as ps
from caffmob_draw.promob import leitor, para_v2


def converter(itens):
    mapa = ps.entradas()
    mapa['solucao\\container1\\document2\\document2.ambient3d'] = ps._ambiente(itens)
    return para_v2.converter(leitor.abrir(ps.zip_de(mapa)).projeto(1))


def caixa(no):
    o, (x, y, z), d = no['origem'], no['eixos'], no['dimensoes']
    pts = [tuple(o[k] + a * x[k] + b * y[k] + c * z[k] for k in range(3))
           for a in (0, d[0]) for b in (0, d[1]) for c in (0, d[2])]
    return (tuple(round(min(p[k] for p in pts)) for k in range(3)), tuple(round(max(p[k] for p in pts)) for k in range(3)))


def por_nome(nos, nome):
    for n in nos:
        if n['nome'] == nome:
            return n
        achou = por_nome(n['filhos'], nome)
        if achou:
            return achou
    return None


class ReferencialTest(unittest.TestCase):
    def test_leitor_le_normal_e_limites(self):
        item = ps._item('MODULO', 'p', base=(100, 0, 0), dim=(300, 900, 15), rot=0, nome='P', limites=((-300, -15, 0), (0, 0, 900)),
                        normal=(0, 1, 0))
        mapa = ps.entradas()
        mapa['solucao\\container1\\document2\\document2.ambient3d'] = ps._ambiente([item])
        it = leitor.abrir(ps.zip_de(mapa)).projeto(1).itens[0]
        self.assertEqual((it.normal, it.limites), ((0, 1, 0), ((-300, -15, 0), (0, 0, 900))))

    def test_peca_espelhada_pelo_limits(self):
        porta = ps._item('MODULO', 'porta', base=(1000, 500, 0), dim=(308, 924, 15), rot=0, nome='Porta espelhada',
                         limites=((-308, -15, 0), (0, 0, 924)))
        r = converter([porta])
        self.assertEqual(caixa(por_nome(r['complemento']['moveis'], 'Porta espelhada')), ((692, 485, 0), (1000, 500, 924)))

    def test_cama_deitada_pela_normal(self):
        cama = ps._item('MODULO', 'cama', base=(2402, -24, 620), dim=(1188, 2088, 652), rot=90, nome='Cama',
                        normal=(0, 1, 0), limites=((0, -652, 0), (1188, 0, 2088)))
        lo, hi = caixa(por_nome(converter([cama])['complemento']['moveis'], 'Cama'))
        self.assertEqual((hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), (1188, 2088, 652))   # deitada: 652 de altura
        self.assertEqual((lo[2], hi[2]), (-32, 620))

    def test_peca_com_normal_cabe_no_pai(self):
        perfil = ps._item('MODULO', 'gola', base=(690, 859, 171), dim=(2260, 42, 21), rot=90, nome='Puxador gola',
                          normal=(0, 1, 0), limites=((0, -21, 0), (2260, 0, 42)))
        porta = ps._item('MODULO', 'porta', base=(690, 901, 171), dim=(920, 2260, 15), rot=90, nome='Porta gola',
                         limites=((-920, -15, 0), (0, 0, 2260)), filhos=[perfil])
        lo, hi = caixa(por_nome(converter([porta])['complemento']['moveis'], 'Puxador gola'))
        self.assertEqual((lo[2], hi[2]), (171, 2431))              # em pé, como a porta, e não atravessando a parede
        self.assertTrue(lo[0] >= 680 and hi[0] <= 720, (lo, hi))

    def test_normal_para_baixo(self):
        base = ps._item('MODULO', 'base', base=(0, 0, 2445), dim=(860, 15, 510), rot=0, nome='Base de cima',
                        normal=(0, 0, -1), limites=((0, -510, 0), (860, 0, 15)))
        lo, hi = caixa(por_nome(converter([base])['complemento']['moveis'], 'Base de cima'))
        self.assertEqual((lo[2], hi[2]), (2430, 2445))              # a altura vai para baixo do ponto base


if __name__ == '__main__':
    unittest.main()
