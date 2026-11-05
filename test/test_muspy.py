"""Paginación y filtros de Muspy, sin red. Se ejecuta con: python3 test/test_muspy.py"""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from muspy_lanzamientos import PAGE, fecha, lanzamientos


def rel(artist, name, d, tipo='Album'):
    return {'date': d, 'type': tipo, 'name': name, 'artist': {'name': artist}}


class Resp:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class Muspy(unittest.TestCase):
    def test_fechas_incompletas(self):
        self.assertEqual(fecha('2026-11-05'), date(2026, 11, 5))
        self.assertEqual(fecha('2026-02'), date(2026, 2, 28))
        self.assertEqual(fecha('2026-12'), date(2026, 12, 31))
        self.assertEqual(fecha('2026'), date(2026, 12, 31))
        self.assertIsNone(fecha(''))
        self.assertIsNone(fecha('2026-13-01'))

    def test_filtra_futuro_viejo_y_tipo(self):
        datos = [rel('Futuro', 'x', '2026-12-01'), rel('A', 'Bueno', '2026-11-01'),
                 rel('B', 'Single', '2026-11-01', 'Single'), rel('C', 'Viejo', '2026-01-01'),
                 rel('D', 'Tras el corte', '2025-01-01')]
        got = list(lanzamientos('u', date(2026, 10, 1), date(2026, 11, 5), {'Album', 'EP'}, lambda *a, **k: Resp(datos)))
        self.assertEqual(got, [('A', 'Bueno')])

    def test_pagina_hasta_que_se_acaba(self):
        offsets = []
        def get(url, params, headers, timeout):
            offsets.append(params['offset'])
            n = PAGE if params['offset'] == 0 else 3
            return Resp([rel('A', f'D{params["offset"]}-{i}', '2026-11-01') for i in range(n)])
        got = list(lanzamientos('u', date(2026, 1, 1), date(2026, 11, 5), set(), get))
        self.assertEqual(offsets, [0, PAGE])
        self.assertEqual(len(got), PAGE + 3)


if __name__ == '__main__':
    unittest.main()
