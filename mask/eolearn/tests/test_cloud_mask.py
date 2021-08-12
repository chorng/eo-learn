"""
Credits:
Copyright (c) 2017-2019 Matej Aleksandrov, Matej Batič, Andrej Burja, Eva Erzin (Sinergise)
Copyright (c) 2017-2019 Grega Milčinski, Matic Lubej, Devis Peresutti, Jernej Puc, Tomislav Slijepčević (Sinergise)
Copyright (c) 2017-2019 Blaž Sovdat, Nejc Vesel, Jovan Višnjić, Anže Zupanc, Lojze Žust (Sinergise)

This source code is licensed under the MIT license found in the LICENSE
file in the root directory of this source tree.
"""

import pytest
from pytest import approx
import numpy as np

from eolearn.core import FeatureType
from eolearn.mask import CloudMaskTask


def test_raises_errors(test_eopatch):
    add_tcm = CloudMaskTask(data_feature='bands')
    with pytest.raises(ValueError):
        add_tcm(test_eopatch)


def test_mono_temporal_cloud_detection(test_eopatch):
    add_tcm = CloudMaskTask(
        data_feature='BANDS-S2-L1C',
        all_bands=True,
        is_data_feature='IS_DATA',
        mono_features=('CLP_TEST', 'CLM_TEST'),
        mask_feature=None,
        average_over=4,
        dilation_size=2,
        mono_threshold=0.4
    )
    eop_clm = add_tcm(test_eopatch)

    assert np.array_equal(eop_clm.mask['CLM_TEST'], eop_clm.mask['CLM_S2C'])
    assert np.array_equal(eop_clm.data['CLP_TEST'], eop_clm.data['CLP_S2C'])


def test_multi_temporal_cloud_detection_downscaled(test_eopatch):

    add_tcm = CloudMaskTask(
        data_feature='BANDS-S2-L1C',
        processing_resolution=120,
        mono_features=('CLP_TEST', 'CLM_TEST'),
        multi_features=('CLP_MULTI_TEST', 'CLM_MULTI_TEST'),
        mask_feature='CLM_INTERSSIM_TEST',
        average_over=8,
        dilation_size=4
    )
    eop_clm = add_tcm(test_eopatch)

    # Check shape and type
    for feature in ((FeatureType.MASK, 'CLM_TEST'), (FeatureType.DATA, 'CLP_TEST')):
        assert eop_clm[feature].ndim == 4
        assert eop_clm[feature].shape[:-1] == eop_clm.data['BANDS-S2-L1C'].shape[:-1]
        assert eop_clm[feature].shape[-1] == 1
    assert eop_clm.mask['CLM_TEST'].dtype == bool
    assert eop_clm.data['CLP_TEST'].dtype == np.float32

    # Compare mean cloud coverage with provided reference
    assert np.mean(eop_clm.mask['CLM_TEST']) == approx(np.mean(eop_clm.mask['CLM_S2C']), abs=0.01)
    assert np.mean(eop_clm.data['CLP_TEST']) == approx(np.mean(eop_clm.data['CLP_S2C']), abs=0.01)

    # Check if most of the same times are flagged as cloudless
    cloudless = np.mean(eop_clm.mask['CLM_TEST'], axis=(1, 2, 3)) == 0
    assert np.mean(cloudless == eop_clm.label['IS_CLOUDLESS'][:, 0]) > 0.94

    # Check multi-temporal results and final mask
    assert np.array_equal(eop_clm.data['CLP_MULTI_TEST'], eop_clm.data['CLP_MULTI'])
    assert np.array_equal(eop_clm.mask['CLM_MULTI_TEST'], eop_clm.mask['CLM_MULTI'])
    assert np.array_equal(eop_clm.mask['CLM_INTERSSIM_TEST'], eop_clm.mask['CLM_INTERSSIM'])
