#! python3
"""Minimal projection example with DeepDRR."""

import deepdrr
from deepdrr import geo
from deepdrr.utils import test_utils, image_utils
from deepdrr.projector import Projector
import numpy as np
from skimage import exposure
import matplotlib.pyplot as plt
from PIL import Image

class Generate:
    def __init__(self, file, path = "projector.png", extra_path="projector_side.png"):
        """
        Generate class

        Descriptions
        --------------------------------
        generate simulated x-ray image using Deep DRR

        Args
        --------------------------------
        file: str
            file path
        path: str
            output name
        """

        # set volume
        self.patient = deepdrr.Volume.from_nifti(file)
        self.patient.faceup()
        self.path = path
        self.extra_path = extra_path
    def deepdrr_run(self, x, y, z, a, b, g, file_path = "projector.png",):
        """
        deepdrr_run
        
        Descriptions
        --------------------------------
        generate simulated x-ray image using Deep DRR

        Args
        --------------------------------
        x: float
            x coordinate value from center of the volume
        y: float
            y coordinate value from center of the volume
        z: float
            z coordinate value from center of the volume
        a: float
            alpha value in radient
        b: float
            beta value in radient

        """

        low,top = self.patient.get_bounding_box_in_world()
        # define the simulated C-arm
        carm = deepdrr.MobileCArm(geo.Point3D((low[0] + (top[0] - low[0]) / 2,
                                               low[1] + (top[1] - low[1]) / 2,
                                               low[2] + (top[2] - low[2]) / 2, 1)) + geo.v(-float(x) ,-float(y), -float(z)), 
                                source_to_isocenter_vertical_distance=700,
                                alpha=float(a),
                                beta=float(b),
                                gamma=float(g))
    
        # project in the AP view
        with Projector(self.patient, carm=carm,     
                    step=0.5, 
            spectrum="90KV_AL40", 
            photon_count=100000, 
            intensity_upper_bound=40,) as projector:

            image = projector.project()
            image = Image.fromarray((image * 255).astype(np.uint8))
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
            image.save(file_path)

        return image

    def empty_file(self):
        """
        empty_file
        
        Descriptions
        --------------------------------
        remove previously generated files; create an image with white background
        """
        image_utils.save(self.path, np.ones((1536, 1536))) 
        image_utils.save(self.extra_path, np.ones((1536, 1536))) 


