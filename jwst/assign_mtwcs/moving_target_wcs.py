"""
Adjust the WCS of a moving target exposure.

Computes the average RA and DEC of a moving
target in all exposures in an association and adds a step to
each of the WCS pipelines to allow aligning the exposures to the average
location of the target.

"""
from copy import deepcopy
import numpy as np
from astropy.modeling.models import Shift, Identity
from gwcs import WCS
from gwcs import coordinate_frames as cf
from jwst import datamodels


def assign_moving_target_wcs(input_model):

    if not isinstance(input_model, datamodels.ModelContainer):
        raise ValueError("Expected a ModelContainer object")

    mt_ra = np.array([model.meta.wcsinfo.mt_ra for model in input_model._models])
    mt_dec = np.array([model.meta.wcsinfo.mt_dec for model in input_model._models])
    mt_avra = mt_ra.mean()
    mt_avdec = mt_dec.mean()

    for model in input_model:
        pipeline = model.meta.wcs._pipeline[:-1]

        mt = deepcopy(model.meta.wcs.output_frame)
        mt.name = 'moving_target'

        mt_ra = model.meta.wcsinfo.mt_ra
        mt_dec = model.meta.wcsinfo.mt_dec
        model.meta.wcsinfo.mt_avra = mt_avra
        model.meta.wcsinfo.mt_avdec = mt_avdec

        rdel = mt_avra - mt_ra
        ddel = mt_avdec - mt_dec

        if isinstance(mt, cf.CelestialFrame):
            transform_to_mt = Shift(rdel) & Shift(ddel)
        elif isinstance(mt, cf.CompositeFrame):
            transform_to_mt = Shift(rdel) & Shift(ddel) & Identity(1)
        else:
            raise ValueError("Unrecognized coordinate frame.")
        pipeline.append((model.meta.wcs.output_frame, transform_to_mt))
        pipeline.append((mt, None))
        new_wcs = WCS(pipeline)
        del model.meta.wcs
        model.meta.wcs = new_wcs
        model.meta.cal_step.assign_mtwcs = 'COMPLETE'
    return input_model
