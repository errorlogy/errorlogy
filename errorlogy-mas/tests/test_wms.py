from mas.engine import wms


def test_wms_cep(challenger_case):
    r1 = wms.detect(challenger_case, prev_cep=0.0)
    r2 = wms.detect(challenger_case, prev_cep=r1.cep)
    assert 0.0 <= r1.msi <= 1.0
    assert 0.0 <= r2.cep <= 1.0
    assert r2.cep >= 0.85 * r1.cep
