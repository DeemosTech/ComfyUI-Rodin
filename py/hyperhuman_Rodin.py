import requests
import torch
import os
import trimesh.exchange
import trimesh.exchange.gltf
import folder_paths as comfy_paths
import logging
import time
import datetime
import shutil
import json
import time
from PIL import Image, ImageOps, ImageSequence
import node_helpers
import numpy as np
import io
import comfy.utils
import trimesh

ROOT_PATH = os.path.join(comfy_paths.get_folder_paths("custom_nodes")[0], "ComfyUI-Rodin")

# Constants
BASE_URL = "https://hyperhuman.deemos.com/api/v2"
API_HEADERS = {}

API_KEY_PARAMETER = {
    "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
}

COMMON_PARAMETERS = {
    "tier": (["Regular", "Sketch"], {"default": "Regular"}),
    "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
    "geometry_file_format":
    (["glb", "usdz", "fbx", "obj", "stl"],
     {"default": "glb", "label_off": "glb",
      "pysssss.binding": [{
          "source": "tier",
          "callback": [{
              "type": "if",
              "condition": [{"left": "$source.value", "op": "eq", "right": '"Sketch"'}],
              "true": [{
                  "type": "set", "target": "$this.options.values", "value": ["glb"]
              }, {
                  "type": "set", "target": "$this.value", "value": '"glb"'
              }, {
                  "type": "set", "target": "$this.disabled", "value": True
              },],
              "false": [{
                  "type": "set", "target": "$this.disabled", "value": False
              }, {
                  "type": "set", "target": "$this.options.values", "value": ["glb", "usdz", "fbx", "obj", "stl"]
              }],
          }]
      }]
      }),
    "material":
    (["PBR", "Shaded"],
     {"default": "PBR",
      "pysssss.binding": [{
          "source": "tier",
          "callback": [{
              "type": "if",
              "condition": [{"left": "$source.value", "op": "eq", "right": '"Sketch"'}],
              "true": [{
                  "type": "set", "target": "$this.options.values", "value": ["PBR"]
              }, {
                  "type": "set", "target": "$this.value", "value": '"PBR"'
              },
                  {
                  "type": "set", "target": "$this.disabled", "value": True
              },],
              "false": [{
                  "type": "set", "target": "$this.disabled", "value": False
              }, {
                  "type": "set", "target": "$this.options.values", "value": ["PBR", "Shaded"]
              }],
          }]
      }]
      }),
    "quality":
    (["high", "medium", "low", "extra-low"],
     {"default": "medium",
      "pysssss.binding": [{
          "source": "tier",
          "callback": [{
              "type": "if",
              "condition": [{"left": "$source.value", "op": "eq", "right": '"Sketch"'}],
              "true": [{
                  "type": "set", "target": "$this.options.values", "value": ["medium"]
              }, {
                  "type": "set", "target": "$this.value", "value": '"medium"'
              }, {
                  "type": "set", "target": "$this.disabled", "value": True
              },],
              "false": [{
                  "type": "set", "target": "$this.disabled", "value": False
              }, {
                  "type": "set", "target": "$this.options.values", "value": ["high", "medium", "low", "extra-low"]
              }],
          }]
      }]
      }),
    "use_hyper":
    ("BOOLEAN",
     {"default": False,
      "pysssss.binding": [{
          "source": "tier",
          "callback": [{
              "type": "if",
              "condition": [{"left": "$source.value", "op": "eq", "right": '"Sketch"'
                             }],
              "true": [{
                  "type": "set", "target": "$this.value", "value": False
              }, {
                  "type": "set", "target": "$this.disabled", "value": True
              },],
              "false": [{
                  "type": "set", "target": "$this.disabled", "value": False
              }, {
                  "type": "set", "target": "$this.options.values", "value": "$result"
              }],
          }]
      }]
      }),
}

SUPPORTED_3D_EXTENSIONS = (
    '.obj',
    '.glb',
    '.fbx',
    '.stl',
    '.usdz',
)

SIMPLE_COMMON_PARAS = {
    "images": ("IMAGE", {"forceInput": True, "multiline": True}),
    "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
    "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
    "Material_Type": (["PBR", "Shaded"], {"default":"PBR"}),
    "Polygon_count": (["4K-Quad", "8K-Quad", "18K-Quad", "50K-Quad", "200K-Triangle"], {"default": "18K-Quad"})
}

SIMPLE_GEN2_PARAS = {
    "images": ("IMAGE", {"forceInput": True, "multiline": True}),
    "api_key": ("APIKEY", {"forceInput": True, "multiline": True}),
    "seed_": ("INT", {"default": 0, "min": 0, "max": 65535, "step": 1, "display": "number", }),
    "Material_Type": (["PBR", "Shaded"], {"default":"PBR"}),
    "Polygon_count": (["4K-Quad", "8K-Quad", "18K-Quad", "50K-Quad", "2K-Triangle", "20K-Triangle", "150K-Triangle", "500K-Triangle"], {"default": "500K-Triangle"}),
    "TAPose": ("BOOLEAN", {"default": False})
}


def post_request(url, api_key, data, files=None, max_retries=5, delay=2):
    headers = {"Authorization": f"Bearer {api_key}"}
    full_url = f"{BASE_URL}/{url}"

    for attempt in range(max_retries):
        try:
            response = requests.post(full_url, headers={**API_HEADERS, **headers}, data=data, files=files)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            logging.info(f"Connection error: {e}. Retrying {attempt + 1}/{max_retries}...")
        except requests.Timeout as e:
            logging.info(f"Timeout error: {e}. Retrying {attempt + 1}/{max_retries}...")
        except requests.HTTPError as e:
            logging.info(f"HTTP error: {e}. Response: {response.text if response else 'No response'}")

            break
        except Exception as e:
            logging.info(f"An unexpected error occurred: {e}. Retrying {attempt + 1}/{max_retries}...")

        time.sleep(delay)
    
    logging.info("[ Rodin3D.process_request ] Max retries reached. Request failed.")
    return None
    


def check_status(api_key, subscription_key):
    data = {"subscription_key": subscription_key}
    return post_request("status", api_key, data)["jobs"]

def load_image(image_path):        
        img = node_helpers.pillow(Image.open, image_path)
        
        output_images = []
        w, h = None, None

        excluded_formats = ['MPO']
        
        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]
            
            if image.size[0] != w or image.size[1] != h:
                continue
            
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            output_images.append(image)

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
        else:
            output_image = output_images[0]

        return output_image

def handle_image(img):
    if not img:
        return load_image(ROOT_PATH+'/asset/error.png')
    for i in ImageSequence.Iterator(img):
        i = node_helpers.pillow(ImageOps.exif_transpose, i)

        if i.mode == 'I':
            i = i.point(lambda i: i * (1 / 255))
        image = i.convert("RGB")
        w = image.size[0]
        h = image.size[1]
        
        if image.size[0] != w or image.size[1] != h:
            continue
        
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
        return image

def download_files(api_key, uuid):
    data = {"task_uuid": uuid}
    files_info = post_request("download", api_key, data)
    save_path = os.path.join(comfy_paths.get_output_directory(), datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(save_path, exist_ok=True)
    
    shaded = diffuse = normal = pbr = load_image(ROOT_PATH+'/asset/error.png')
    for file_info in files_info["list"]:
        filename = file_info["name"].split('/')[-1]
        file_path = os.path.join(save_path, filename)
        if file_path.endswith(SUPPORTED_3D_EXTENSIONS):
            model_file_path = file_path
        print(f"[ download_files ] Downloading file: {file_path}")
        max_retries = 5
        for attempt in range(max_retries): #max_retries = 5
            try:

                with requests.get(file_info["url"], stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                break
            except Exception as e:
                print(f"Error downloading {file_path}:{e}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print(f"[ download_file_error ] Failed to download {file_path} after {max_retries} attempts.")

        if file_path.endswith('.glb'):
            for attempt in range(max_retries):
                try:
                    with requests.get(file_info["url"], stream=True) as r:
                        r.raise_for_status()
                        if file_path.endswith('.glb'):
                            kwargs =  trimesh.exchange.gltf.load_glb(r.raw)
                            for key, value in kwargs['geometry'].items():
                                material = value['visual'].material
                                shaded = handle_image(material.emissiveTexture)
                                diffuse = handle_image(material.baseColorTexture)
                                normal = handle_image(material.normalTexture)
                                pbr = handle_image(material.metallicRoughnessTexture)
                    break
                except Exception as e:
                    print(f"Error processing GLB file {file_path}: {e}")
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        time.sleep(2)
                    else:
                        print(f"[ download_file_error ] Failed to process {file_path} after {max_retries} attempts.")
        if filename == "shaded.png":
            shaded = load_image(file_path)
        elif filename == "texture_diffuse.png":
            diffuse = load_image(file_path)
        elif filename == "texture_normal.png":
            normal = load_image(file_path)
        elif filename == "texture_pbr.png":
            pbr = load_image(file_path)


    #logging.info(model_file_path)

    return shaded, diffuse, normal, pbr, model_file_path, 


def tensor_to_filelike(tensor):
    """
    Converts a PyTorch tensor to a file-like object.

    Args:
    - tensor (torch.Tensor): A tensor representing an image of shape (H, W, C)
      where C is the number of channels (3 for RGB), H is height, and W is width.

    Returns:
    - io.BytesIO: A file-like object containing the image data.
    """
    array = tensor.cpu().numpy()
    array = (array * 255).astype('uint8')
    image = Image.fromarray(array, 'RGB')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')  # PNG is used for lossless compression
    img_byte_arr.seek(0)
    return img_byte_arr

def LogInfomation(data, name):
    logging.info(f"[ Rodin3D.process_request ]\n{name} =")
    if isinstance(data, (dict)):
        logging.info(json.dumps(data, indent=4))
    elif isinstance(data, (list)) and name == "files":
        logging.info(repr(data))
    elif isinstance(data, (list)) and name == "status":
        table_header = f"{'UUID':<40} {'Status':<12}"
        separator = '-' * 52
        logging.info(table_header)
        logging.info(separator)
        for item in data:
            logging.info(f"{item['uuid']:<40} {item['status']:<12}")
        
    
    

class Rodin3D:

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "STRING", )
    RETURN_NAMES = ("shaded", "diffuse", "normal", "pbr", "model_path")
    FUNCTION = "main_func"
    OUTPUT_NODE = True
    CATEGORY = "Mesh/Rodin"

    def process_request(self, api_key, images, prompt, condition_mode, seed, geometry_file_format, material, quality, use_hyper, tier) -> None:
        # Prepare request data and files
        files = [
            (
                "images",
                open(image, "rb") if isinstance(image, str) else tensor_to_filelike(image)
            )
            for image in images if image is not None]
        data = {
            "prompt": prompt,
            "condition_mode": condition_mode,
            "seed": seed,
            "geometry_file_format": geometry_file_format,
            "material": material,
            "quality": quality,
            "use_hyper": use_hyper,
            "tier": tier,
        }
        #logging.info(f"[ Rodin3D.process_request ]\n data = {data}, files = {files}")
        LogInfomation(data, "data")
        LogInfomation(files, "files")
        response = post_request("rodin", api_key, data, files=files)

        # Submit and handle the response
        if response is not None and "uuid" in response:
            shaded, diffuse, normal, pbr, model_path = self.submit_poll_download(api_key, data, response['uuid'], response['jobs']['subscription_key'])
            return shaded, diffuse, normal, pbr, model_path, 
        else:
            logging.info(f"[ Rodin3D.process_request ] Error submitting the job:\n{response}")
            shaded = diffuse = normal = pbr = load_image(ROOT_PATH+'/asset/error.png')
            return shaded, diffuse, normal, pbr, ""

    def submit_poll_download(self, api_key, data, uuid, subscription_key):
        """Submits the job, polls for its completion, and downloads the result when ready."""
        polling_interval = 2  # Interval in seconds to wait between checks

        total_seconds_estimated = 20 if data["tier"] == "Sketch" else 60
        pbar = comfy.utils.ProgressBar(total_seconds_estimated)

        while True:
            status = check_status(api_key, subscription_key)
            #logging.info(f"[ Rodin3D.process_request ] status = {status}")
            LogInfomation(status, "status")

            if all([job["status"] == "Done" for job in status]):
                logging.info(f"[ Rodin3D.process_request ] Generation complete. Downloading files...")
                save_model_path = download_files(api_key, uuid)
                #print(f"[save model path] : {save_model_path}")
                return save_model_path
            
            if any([job["status"] == "Failed" for job in status]):
                shaded = diffuse = normal = pbr = load_image(ROOT_PATH+'/asset/error.png')
                return shaded, diffuse, normal, pbr, ""

            time.sleep(polling_interval)
            pbar.update(2)


class RodinImage3D(Rodin3D):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **API_KEY_PARAMETER,
                "image": ("IMAGE", {"forceInput": True, "multiline": True}),
            },
            "optional": {
                "prompt": ("STRING",{"forceInput":True,"multiline": True}),
                **COMMON_PARAMETERS
            },
        }

    def main_func(self, api_key, image, seed_, geometry_file_format, material, quality, use_hyper, tier, prompt=None):
        images = [image]
        condition_mode = "concat"

        shaded, diffuse, normal, pbr, model_path = self.process_request(api_key, images, prompt, condition_mode, seed_, geometry_file_format, material, quality, use_hyper, tier)
        #logging.info(m_model_path)
        #logging.info(type(m_model_path))
        return (shaded, diffuse, normal, pbr, model_path)


class RodinMultipleImage3D(RodinImage3D):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **API_KEY_PARAMETER,
            },
            "optional": {
                "image_1": ("IMAGE", {"forceInput": True, "multiline": True}),
                "image_2": ("IMAGE", {"forceInput": True, "multiline": True}),
                "image_3": ("IMAGE", {"forceInput": True, "multiline": True}),
                "image_4": ("IMAGE", {"forceInput": True, "multiline": True}),
                "image_5": ("IMAGE", {"forceInput": True, "multiline": True}),
                "prompt": ("STRING",{"forceInput":True,"multiline": True}),
                "condition_mode": (["concat", "fuse"], {"default": "concat"}),
                **COMMON_PARAMETERS
            },
        }

    def main_func(self, api_key, seed_, geometry_file_format, material, quality, use_hyper, tier, condition_mode, image_1=None, image_2=None, image_3=None, image_4=None, image_5=None, prompt=None):
        images = [image_1, image_2, image_3, image_4, image_5]
        # Filter out None values
        images = [img for img in images if img is not None]

        shaded, diffuse, normal, pbr, model_path = self.process_request(api_key, images, prompt, condition_mode, seed_, geometry_file_format, material, quality, use_hyper, tier)

        return (shaded, diffuse, normal, pbr, model_path)


class RodinText3D(RodinImage3D):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **API_KEY_PARAMETER,
                "prompt": ("STRING", {"forceInput": True, "multiline": True}),
            },
            "optional": {
                **COMMON_PARAMETERS
            },
        }

    def main_func(self, api_key, prompt, seed_, geometry_file_format, material, quality, use_hyper, tier):
        images = []
        condition_mode = None

        shaded, diffuse, normal, pbr, model_path = self.process_request(api_key, images, prompt, condition_mode, seed_, geometry_file_format, material, quality, use_hyper, tier)

        return (shaded, diffuse, normal, pbr, model_path,)


class PromptForRodin:

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)

    FUNCTION = "main_func"
    CATEGORY = "Mesh/Rodin"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"default": "A textual prompt to guide the 3d generation.", "multiline": True})
            }
        }

    def main_func(self, prompt):
        return (prompt,)


class LoadRodinAPIKEY:

    RETURN_TYPES = ("APIKEY",)
    RETURN_NAMES = ("api_key",)
    FUNCTION = "main_func"
    CATEGORY = "Mesh/Rodin"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": "Get your API KEY from: https://hyperhuman.deemos.com/api-dashboard", "multiline": True})
            },
        }

    def main_func(self, api_key):
        return (api_key,)
    

def get_quality_mode(poly_count):
    polycount = poly_count.split("-")
    poly = polycount[1]
    count = polycount[0]
    if poly == "Triangle":
        mesh_mode = "Raw"
    elif poly == "Quad":
        mesh_mode = "Quad"
    else:
        mesh_mode = "Quad"

    if count == "4K":
        quality_override = 4000
    elif count == "8K":
        quality_override = 8000
    elif count == "18K":
        quality_override = 18000
    elif count == "50K":
        quality_override = 50000
    elif count == "2K":
        quality_override = 2000
    elif count == "20K":
        quality_override = 20000
    elif count == "150K":
        quality_override = 150000
    elif count == "500K":
        quality_override = 500000
    else:
        quality_override = 18000

    return mesh_mode, quality_override
    

class Rodin3D_simple():
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_path",)
    FUNCTION = "main_func"
    OUTPUT_NODE = True
    CATEGORY = "Mesh/Rodin"


    def process_request(self, api_key, images, tier, seed, material, poly_count, TAPose=False) -> None:

        mesh_mode, quality_override = get_quality_mode(poly_count)
        # Prepare request data and files
        files = [
            (
                "images",
                open(image, "rb") if isinstance(image, str) else tensor_to_filelike(image)
            )
            for image in images if image is not None]
        data = {
            "seed": seed,
            "material": material,
            "quality_override": quality_override,
            "mesh_mode": mesh_mode,
            "tier": tier,
            "TAPose": TAPose,
        }
        #logging.info(f"[ Rodin3D.process_request ]\n data = {data}, files = {files}")
        LogInfomation(data, "data")
        LogInfomation(files, "files")
        response = post_request("rodin", api_key, data, files=files)

        # Submit and handle the response
        if response is not None and "uuid" in response:
            model_path = self.submit_poll_download(api_key, response['uuid'], response['jobs']['subscription_key'])
            print(f"model_path = {model_path}")
            return model_path
        else:
            logging.info(f"[ Rodin3D.process_request ] Error submitting the job:\n{response}")
            # shaded = diffuse = normal = pbr = load_image(ROOT_PATH+'/asset/error.png')
            return ""

    def submit_poll_download(self, api_key, uuid, subscription_key):
        """Submits the job, polls for its completion, and downloads the result when ready."""
        polling_interval = 2  # Interval in seconds to wait between checks

        total_seconds_estimated = 60
        pbar = comfy.utils.ProgressBar(total_seconds_estimated)

        while True:
            status = check_status(api_key, subscription_key)
            #logging.info(f"[ Rodin3D.process_request ] status = {status}")
            LogInfomation(status, "status")

            if all([job["status"] == "Done" for job in status]):
                logging.info(f"[ Rodin3D.process_request ] Generation complete. Downloading files...")
                _, _, _, _,save_model_path = download_files(api_key, uuid)
                #print(f"[save model path] : {save_model_path}")
                return save_model_path
            
            if any([job["status"] == "Failed" for job in status]):
                # shaded = diffuse = normal = pbr = load_image(ROOT_PATH+'/asset/error.png')
                return ""

            time.sleep(polling_interval)
            pbar.update(2)

class mRodin3D_Regular(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **SIMPLE_COMMON_PARAS,
            },
        }
    

    def main_func(self, images, api_key, seed_, Material_Type, Polygon_count):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path = self.process_request(api_key, m_images, "Regular", seed_, Material_Type, Polygon_count, TAPose=False)
        return (model_path,)

class mRodin3D_Detail(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **SIMPLE_COMMON_PARAS,
            },
        }
    

    def main_func(self, images, api_key, seed_, Material_Type, Polygon_count):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path = self.process_request(api_key, m_images, "Detail", seed_, Material_Type, Polygon_count, TAPose=False)
        return (model_path,)


class mRodin3D_Smooth(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                **SIMPLE_COMMON_PARAS,
            },
        }
    

    def main_func(self, images, api_key, seed_, Material_Type, Polygon_count):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path = self.process_request(api_key, m_images, "Smooth", seed_, Material_Type, Polygon_count, TAPose=False)
        
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
        }
    

    def main_func(self, images, api_key, seed_, Material_Type):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path = self.process_request(api_key, m_images, "Sketch", seed_, Material_Type, "18K-Quad", TAPose=False)
        print(model_path)
        return (model_path,)
    

class mRodin3D_Gen2(Rodin3D_simple):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                    **SIMPLE_GEN2_PARAS,
            },
        }
    
    def main_func(self, images, api_key, seed_, Material_Type, Polygon_count, TAPose):
        num_images = images.shape[0]
        m_images = []
        for i in range(num_images):
            m_images.append(images[i])
        model_path = self.process_request(api_key, m_images, "Gen-2", seed_, Material_Type, Polygon_count, TAPose=TAPose)
        
        return (model_path,)
    


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "RodinImage3D": RodinImage3D,
    "RodinMultipleImage3D": RodinMultipleImage3D,
    "RodinText3D": RodinText3D,
    "PromptForRodin": PromptForRodin,
    "LoadRodinAPIKEY": LoadRodinAPIKEY,
    "mRodin3D_Regular": mRodin3D_Regular,
    "mRodin3D_Detail": mRodin3D_Detail,
    "mRodin3D_Smooth": mRodin3D_Smooth,
    "mRodin3D_Sketch": mRodin3D_Sketch,
    "mRodin3D_Gen2": mRodin3D_Gen2,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "RodinImage3D": "Rodin - Image to 3D",
    "RodinMultipleImage3D": "Rodin - Multiple Images to 3D",
    "RodinText3D": "Rodin - Text to 3D",
    "PromptForRodin": "Rodin - Prompt for Rodin",
    "LoadRodinAPIKEY": "Rodin - API KEY",
    "mRodin3D_Regular": "Rodin - Regular Generate",
    "mRodin3D_Detail": "Rodin - Detail Generate",
    "mRodin3D_Smooth": "Rodin - Smooth Generate",
    "mRodin3D_Sketch": "Rodin - Sketch Generate",
    "mRodin3D_Gen2": "Rodin - Gen2 Generate"
}
