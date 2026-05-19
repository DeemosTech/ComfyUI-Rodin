from .hyper3d_nodes import *

NODE_CLASS_MAPPINGS = {
    "mLoadRodinAPIKEY": mLoadRodinAPIKEY,
    "mRodin3D_Regular": mRodin3D_Regular,
    "mRodin3D_Detail": mRodin3D_Detail,
    "mRodin3D_Smooth": mRodin3D_Smooth,
    "mRodin3D_Sketch": mRodin3D_Sketch,
    "mRodin3D_Gen2": mRodin3D_Gen2,
    "mRodin3D_bbox_controlnet": mRodin3D_bbox_controlnet,
    "mRodin3D_Gen_2_5_Fast_Image": mRodin3D_Gen_2_5_Fast_Image,
    "mRodin3D_Gen_2_5_Fast_Text": mRodin3D_Gen_2_5_Fast_Text,
    "mRodin3D_Gen_2_5_Regular_Image": mRodin3D_Gen_2_5_Regular_Image,
    "mRodin3D_Gen_2_5_Regular_Text": mRodin3D_Gen_2_5_Regular_Text,
    "mRodin3D_Gen_2_5_ExtremeHigh_Image": mRodin3D_Gen_2_5_ExtremeHigh_Image,
    "mRodin3D_Gen_2_5_ExtremeHigh_Text": mRodin3D_Gen_2_5_ExtremeHigh_Text,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "mLoadRodinAPIKEY": "Rodin - API KEY",
    "mRodin3D_Regular": "Rodin - Regular Generate",
    "mRodin3D_Detail": "Rodin - Detail Generate",
    "mRodin3D_Smooth": "Rodin - Smooth Generate",
    "mRodin3D_Sketch": "Rodin - Sketch Generate",
    "mRodin3D_Gen2": "Rodin - Gen2 Generate",
    "mRodin3D_bbox_controlnet": "Rodin - BBox Controlnet",
    "mRodin3D_Gen_2_5_Fast_Image": "Rodin - Gen 2.5 Fast Image-to-3D",
    "mRodin3D_Gen_2_5_Fast_Text": "Rodin - Gen 2.5 Fast Text-to-3D",
    "mRodin3D_Gen_2_5_Regular_Image": "Rodin - Gen 2.5 Regular Image-to-3D",
    "mRodin3D_Gen_2_5_Regular_Text": "Rodin - Gen 2.5 Regular Text-to-3D",
    "mRodin3D_Gen_2_5_ExtremeHigh_Image": "Rodin - Gen 2.5 ExtremeHigh Image-to-3D",
    "mRodin3D_Gen_2_5_ExtremeHigh_Text": "Rodin - Gen 2.5 ExtremeHigh Text-to-3D",
}