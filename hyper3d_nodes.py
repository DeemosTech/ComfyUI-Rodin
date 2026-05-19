from .modules.Rodin_Mainsite import process_full_generation, full_polygen_pipeline, QUALITY_MESH_DEFAULT, QUALITY_MESH_OPTIONS

RODIN_GEN_1_5_PARAS = {
    "images": ("IMAGE", {"forceInput": True, "multiline": True}),
    "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
    "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
    "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"PBR"}),
    "Polygon_count": (["4K-Quad", "8K-Quad", "18K-Quad", "50K-Quad", "200K-Quad", "200K-Triangle"], {"default": "18K-Quad"}),
}

RODIN_GEN_2_PARAS = {
    "images": ("IMAGE", {"forceInput": True, "multiline": True}),
    "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
    "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
    "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"PBR"}),
    "Polygon_count": (["4K-Quad", "8K-Quad", "18K-Quad", "50K-Quad", "200K-Quad", "2K-Triangle", "20K-Triangle", "150K-Triangle", "500K-Triangle", "1M-Triangle"], {"default": "500K-Triangle"}),
    "TAPose": ("BOOLEAN", {"default": False}),
}

class mLoadRodinAPIKEY:

    RETURN_TYPES = ("APIKEY",)
    RETURN_NAMES = ("api_key",)
    FUNCTION = "main_func"
    CATEGORY = "Mesh/Rodin"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": "Get your API KEY from: https://hyper3d.ai/api-dashboard", "multiline": True})
            },
        }

    async def main_func(self, api_key):
        return (api_key,)
    
class mRodin3D_bbox_controlnet():
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("bbox",)
    FUNCTION = "main_func"
    CATEGORY = "Mesh/Rodin"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":{
                "Width": ("INT", {"default": 100, "min": 1, "max": 300, "step": 1, "display": "number"}),
                "Height": ("INT", {"default": 100, "min": 1, "max": 300, "step": 1, "display": "number"}),
                "Length": ("INT", {"default": 100, "min": 1, "max": 300, "step": 1, "display": "number"}),
            },
        }
    
    async def main_func(self, Width, Height, Length):
        bbox_control = str([Width, Height, Length])
        # print(bbox_control)
        return (bbox_control,)
    
class Rodin3D_simple():
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_path",)
    FUNCTION = "main_func"
    OUTPUT_NODE = True
    CATEGORY = "Mesh/Rodin"
    
class mRodin3D_Regular(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **RODIN_GEN_1_5_PARAS,
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, images, api_key, seed_, Material_Type, Polygon_count, bbox = None, height_cm = None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])

        quality_override, mesh_mode = QUALITY_MESH_OPTIONS[Polygon_count]
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier="Regular",
            seed=seed_, 
            quality=None,
            geometry_file_format="glb",
            material=Material_Type, 
            texture_mode=None,
            quality_override=quality_override,
            mesh_mode=mesh_mode,
            ta_pose=False,
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm
        )
        return (model_path,)
    
class mRodin3D_Detail(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **RODIN_GEN_1_5_PARAS,
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, images, api_key, seed_, Material_Type, Polygon_count, bbox = None, height_cm = None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])

        quality_override, mesh_mode = QUALITY_MESH_OPTIONS[Polygon_count]
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier="Detail",
            seed=seed_, 
            quality=None,
            geometry_file_format="glb",
            material=Material_Type, 
            texture_mode=None,
            quality_override=quality_override,
            mesh_mode=mesh_mode,
            ta_pose=False,
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm
        )
        return (model_path,)
    
class mRodin3D_Smooth(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **RODIN_GEN_1_5_PARAS,
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, images, api_key, seed_, Material_Type, Polygon_count, bbox = None, height_cm = None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])

        quality_override, mesh_mode = QUALITY_MESH_OPTIONS[Polygon_count]
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier="Smooth",
            seed=seed_, 
            quality=None,
            geometry_file_format="glb",
            material=Material_Type, 
            texture_mode=None,
            quality_override=quality_override,
            mesh_mode=mesh_mode,
            ta_pose=False,
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm
        )
        return (model_path,)
    
class mRodin3D_Sketch(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"forceInput": True, "multiline": True}),
                "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
                "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
                "Material_Type": (["PBR", "Shaded"], {"default":"PBR"}),
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
            },
        }
    
    async def main_func(self, images, api_key, seed_, Material_Type, bbox=None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier="Sketch",
            seed=seed_, 
            quality=None,
            geometry_file_format="glb",
            material=Material_Type, 
            texture_mode=None,
            quality_override=None,
            mesh_mode=None,
            ta_pose=False,
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=None,
        )
        return (model_path,)
    
class mRodin3D_Gen2(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **RODIN_GEN_2_PARAS,
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    async def main_func(self, images, api_key, seed_, Material_Type, Polygon_count, TAPose, height_cm=None, bbox=None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])

        quality_override, mesh_mode = QUALITY_MESH_OPTIONS[Polygon_count]
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier="Gen-2",
            seed=seed_, 
            quality=None,
            geometry_file_format="glb",
            material=Material_Type, 
            texture_mode=None,
            quality_override=quality_override,
            mesh_mode=mesh_mode,
            ta_pose=TAPose, 
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm,
        )
        return (model_path,)
    
class mRodin3D_Gen_2_5_Fast_Image(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
                "images": ("IMAGE", {"forceInput": True, "multiline": True}),
                "tier": (["Gen-2.5-Extreme-Low", "Gen-2.5-Low", "Gen-2.5-Medium", "Gen-2.5-High"], {"default":"Gen-2.5-Low"}),
                "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
                "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"Shaded"}),
                "geometry_file_format": (["glb", "usdz"], {"default":"glb"}),
                "mesh_faces": ("INT", {"default": 20000, "min": 1000, "max": 20000, "step": 1, "display": "number", }),
                "texture_mode": (["extreme-low", "low", "medium", "high", "Default"], {"default":"Default"}),
                "TAPose": ("BOOLEAN", {"default": False}),
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, images, tier, api_key, seed_, Material_Type, TAPose, geometry_file_format, mesh_faces, texture_mode, height_cm=None, bbox=None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier=tier,
            seed=seed_, 
            quality=None,
            geometry_file_format=geometry_file_format,
            material=Material_Type, 
            texture_mode=texture_mode,
            quality_override=mesh_faces,
            mesh_mode="Raw",
            ta_pose=TAPose, 
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm,
        )
        return (model_path,)
    
class mRodin3D_Gen_2_5_Fast_Text(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
                "prompt": ("STRING", {"forceInput": False, "multiline": True}),
                "tier": (["Gen-2.5-Extreme-Low", "Gen-2.5-Low", "Gen-2.5-Medium", "Gen-2.5-High"], {"default":"Gen-2.5-Low"}),
                "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
                "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"Shaded"}),
                "geometry_file_format": (["glb", "usdz"], {"default":"glb"}),
                "mesh_faces": ("INT", {"default": 20000, "min": 1000, "max": 20000, "step": 1, "display": "number", }),
                "texture_mode": (["extreme-low", "low", "medium", "high", "Default"], {"default":"Default"}),
                "TAPose": ("BOOLEAN", {"default": False}),
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, prompt, tier, api_key, seed_, Material_Type, TAPose, geometry_file_format, mesh_faces, texture_mode, height_cm=None, bbox=None):
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=None, 
            prompt = prompt,
            tier=tier,
            seed=seed_, 
            quality=None,
            geometry_file_format=geometry_file_format,
            material=Material_Type, 
            texture_mode=texture_mode,
            quality_override=mesh_faces,
            mesh_mode="Raw",
            ta_pose=TAPose, 
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm,
        )
        return (model_path,)
    
class mRodin3D_Gen_2_5_Regular_Image(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
                "images": ("IMAGE", {"forceInput": True, "multiline": True}),
                "tier": (["Gen-2.5-Low", "Gen-2.5-Medium", "Gen-2.5-High"], {"default":"Gen-2.5-High"}),
                "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
                "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"Shaded"}),
                "Polygon_count": (["4K-Quad", "8K-Quad", "18K-Quad", "50K-Quad", "2K-Triangle", "20K-Triangle", "150K-Triangle", "500K-Triangle", "1M-Triangle", "Default"], {"default": "Default"}),
                "geometry_file_format": (["glb", "usdz"], {"default":"glb"}),
                "texture_mode": (["extreme-low", "low", "medium", "high", "Default"], {"default":"Default"}),
                "TAPose": ("BOOLEAN", {"default": False}),
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, images, tier, api_key, seed_, Material_Type, TAPose, geometry_file_format, Polygon_count, texture_mode, height_cm=None, bbox=None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        
        if Polygon_count != "Default":
            quality_override, mesh_mode = QUALITY_MESH_OPTIONS[Polygon_count]
        else:
            quality_override, mesh_mode = QUALITY_MESH_DEFAULT[tier]
        
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier=tier,
            seed=seed_, 
            quality=None,
            geometry_file_format=geometry_file_format,
            material=Material_Type, 
            texture_mode=texture_mode,
            quality_override=quality_override,
            mesh_mode=mesh_mode,
            ta_pose=TAPose, 
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm,
        )
        return (model_path,)
    
class mRodin3D_Gen_2_5_Regular_Text(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
                "prompt": ("STRING", {"forceInput": False, "multiline": True}),
                "tier": (["Gen-2.5-Low", "Gen-2.5-Medium", "Gen-2.5-High"], {"default":"Gen-2.5-High"}),
                "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
                "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"Shaded"}),
                "Polygon_count": (["4K-Quad", "8K-Quad", "18K-Quad", "50K-Quad", "2K-Triangle", "20K-Triangle", "150K-Triangle", "500K-Triangle", "1M-Triangle", "Default"], {"default": "Default"}),
                "geometry_file_format": (["glb", "usdz"], {"default":"glb"}),
                "texture_mode": (["extreme-low", "low", "medium", "high", "Default"], {"default":"Default"}),
                "TAPose": ("BOOLEAN", {"default": False}),
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, prompt, tier, api_key, seed_, Material_Type, TAPose, geometry_file_format, Polygon_count, texture_mode, height_cm=None, bbox=None):
        if Polygon_count != "Default":
            quality_override, mesh_mode = QUALITY_MESH_OPTIONS[Polygon_count]
        else:
            quality_override, mesh_mode = QUALITY_MESH_DEFAULT[tier]
        
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=None, 
            prompt = prompt,
            tier=tier,
            seed=seed_, 
            quality=None,
            geometry_file_format=geometry_file_format,
            material=Material_Type, 
            texture_mode=texture_mode,
            quality_override=quality_override,
            mesh_mode=mesh_mode,
            ta_pose=TAPose, 
            hd_texture=False,
            model_early_export=False,
            is_micro=False,
            geometry_instruct_mode='faithful',
            bbox=bbox,
            height_cm=height_cm,
        )
        return (model_path,)
    
class mRodin3D_Gen_2_5_ExtremeHigh_Image(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
                "images": ("IMAGE", {"forceInput": True, "multiline": True}),
                "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
                "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"Shaded"}),
                "mesh_mode": (["Raw", "Quad"], {"default":"Raw"}),
                "mesh_faces": ("INT", {"default": 1000000, "min": 20000, "max": 2000000, "step": 1, "display": "number", }),
                "geometry_file_format": (["glb", "usdz", "fbx", "obj", "stl"], {"default":"glb"}),
                "texture_mode": (["legacy", "extreme-low", "low", "medium", "high"], {"default":"high"}),
                "is_micro": ("BOOLEAN", {"default": False}),
                "Creative": ("BOOLEAN", {"default": False}),
                "TAPose": ("BOOLEAN", {"default": False}),
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, images, api_key, seed_, Material_Type, TAPose, mesh_mode, mesh_faces, geometry_file_format, texture_mode, is_micro, Creative, height_cm=None, bbox=None):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=m_images, 
            prompt = None,
            tier="Gen-2.5-Extreme-High",
            seed=seed_, 
            quality=None,
            geometry_file_format=geometry_file_format,
            material=Material_Type, 
            texture_mode=texture_mode,
            quality_override=mesh_faces,
            mesh_mode=mesh_mode,
            ta_pose=TAPose, 
            hd_texture=False,
            model_early_export=False,
            is_micro=is_micro,
            geometry_instruct_mode= 'creative' if Creative else 'faithful',
            bbox=bbox,
            height_cm=height_cm,
        )
        return (model_path, )

class mRodin3D_Gen_2_5_ExtremeHigh_Text(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
                "prompt": ("STRING", {"forceInput": False, "multiline": True}),
                "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
                "Material_Type": (["PBR", "Shaded", "All", "None"], {"default":"Shaded"}),
                "mesh_mode": (["Raw", "Quad"], {"default":"Raw"}),
                "mesh_faces": ("INT", {"default": 1000000, "min": 20000, "max": 2000000, "step": 1, "display": "number", }),
                "geometry_file_format": (["glb", "usdz", "fbx", "obj", "stl"], {"default":"glb"}),
                "texture_mode": (["legacy", "extreme-low", "low", "medium", "high"], {"default":"high"}),
                "is_micro": ("BOOLEAN", {"default": False}),
                "Creative": ("BOOLEAN", {"default": False}),
                "TAPose": ("BOOLEAN", {"default": False}),
            },
            "optional":{
                "bbox": ("STRING",{"forceInput":True,"multiline": True}),
                "height_cm":("INT", {"forceInput":True}),
            },
        }
    
    async def main_func(self, prompt, api_key, seed_, Material_Type, TAPose, mesh_mode, mesh_faces, geometry_file_format, texture_mode, is_micro, Creative, height_cm=None, bbox=None):
        model_path, _ = await process_full_generation(
            api_key=api_key, 
            images=None, 
            prompt = prompt,
            tier="Gen-2.5-Extreme-High",
            seed=seed_, 
            quality=None,
            geometry_file_format=geometry_file_format,
            material=Material_Type, 
            texture_mode=texture_mode,
            quality_override=mesh_faces,
            mesh_mode=mesh_mode,
            ta_pose=TAPose, 
            hd_texture=False,
            model_early_export=False,
            is_micro=is_micro,
            geometry_instruct_mode= 'creative' if Creative else 'faithful',
            bbox=bbox,
            height_cm=height_cm,
        )
        return (model_path, )

