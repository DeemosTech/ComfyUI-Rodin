import io
from PIL import Image
import datetime
import asyncio
import aiohttp
import os
from typing import Optional, Tuple, List
import logging
import folder_paths as comfy_paths

ERROR_MEG = {
    "MISS_API_KEY": "MISS_API_KEY",
    "MISS_IMAGES_OR_PROMPT": "MISS_IMAGES_OR_PROMPT",
    "UNKNOWN_ERROR": "UNKNOWN_ERROR",
    "RODIN_ERROR": "RODIN_ERROR",
    "NO_JOBS_FOUND": "NO_JOBS_FOUND",
    "MISS_SUBSCRIPTION_KEY": "MISS_SUBSCRIPTION_KEY",
    "MISS_JOB_UUID": "MISS_JOB_UUID",
    "NO_FILES_FOUND": "NO_FILES_FOUND",
    "RODIN_POLYGEN_ERROR": "RODIN_POLYGEN_ERROR",
    "MISS_MODEL_ASSET_ID": "MISS_MODEL_ASSET_ID",
}

SUPPORTED_3D_EXTENSIONS = [
    '.obj',
    '.glb',
    '.fbx',
    '.stl',
    '.usdz',
]

QUALITY_MESH_OPTIONS = {
    "4K-Quad": (4000, "Quad"),
    "8K-Quad": (8000, "Quad"), 
    "18K-Quad": (18000, "Quad"),
    "50K-Quad": (50000, "Quad"),
    "200K-Quad": (200000, "Quad"),
    "2K-Triangle": (2000, "Raw"),
    "20K-Triangle": (20000, "Raw"),
    "150K-Triangle": (150000, "Raw"),
    "200K-Triangle": (200000, "Raw"),
    "500K-Triangle": (500000, "Raw"),
    "1M-Triangle": (1000000, "Raw")
}

QUALITY_MESH_DEFAULT = {
    "Gen-2.5-Minimum": (50000, "Raw"),
    "Gen-2.5-Extreme-Low": (50000, "Raw"),
    "Gen-2.5-Low": (50000, "Raw"),
    "Gen-2.5-Medium": (500000, "Raw"),
    "Gen-2.5-High": (500000, "Raw"),
    "Gen-2.5-ExtremeHigh": (1000000, "Raw")
}

RODIN_API_BASE_URL = "https://api.hyper3d.com"

MAX_PARALLEL = 3

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

async def submit_generate_job(
    api_key: str,
    images: Optional[List[str]],
    prompt: Optional[str],
    seed: Optional[int],
    quality: Optional[str],
    quality_override: Optional[int],
    mesh_mode: Optional[str] = 'Raw',
    geometry_file_format: Optional[str] = 'glb',
    material: Optional[str] = 'PBR',
    texture_mode: Optional[str] = None,
    tier: Optional[str] = None,
    ta_pose: Optional[bool] = False,
    hd_texture: Optional[bool] = False,
    model_early_export: Optional[bool] = False,
    is_micro: Optional[bool] = False,
    geometry_instruct_mode: Optional[str] = 'faithful',
    bbox: Optional[str] = None,
    height_cm: Optional[int] = None,
) -> Tuple[str, Optional[str], Optional[str]]:
    
    """Submit a job job"""

    if not api_key:
        return ERROR_MEG["MISS_API_KEY"], None, None
    
    # Prepare the request
    url = f"{RODIN_API_BASE_URL}/api/v2/rodin"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    if images is None and prompt is None:
        return ERROR_MEG["MISS_IMAGES_OR_PROMPT"], None, None

    # Prepare form_data
    form_data = aiohttp.FormData()

    # Handle images
    if images is not None:
        if isinstance(images, list):
            for img in images:
                if isinstance(img, str):
                    with open(img, "rb") as f:
                        file_content = f.read()
                        form_data.add_field("images", file_content)
                else:
                    form_data.add_field("images", tensor_to_filelike(img))
        else:
            # Handle single image case
            if isinstance(images, str):
                with open(images, "rb") as f:
                    file_content = f.read()
                    form_data.add_field("images", file_content)
            else:
                form_data.add_field("images", tensor_to_filelike(images))

    # Handle prompt
    if prompt is not None and prompt != "":
        form_data.add_field("prompt", prompt)
        
    # Handle seed
    if seed is not None and seed != 0 and seed != "":
        form_data.add_field("seed", str(seed))

    # Handle quality
    if quality is not None and quality_override is None:
        form_data.add_field("quality", quality)
        
    # Handle quality_override
    if quality_override is not None:
        form_data.add_field("quality_override", str(quality_override))

    # Handle mesh_mode
    if mesh_mode is not None:
        form_data.add_field("mesh_mode", mesh_mode)

    # Handle geometry_file_format
    if geometry_file_format is not None:
        form_data.add_field("geometry_file_format", geometry_file_format)
    
    # Handle material
    if material is not None:
        form_data.add_field("material", material)
    
    # Handle texture_mode
    if texture_mode is not None and texture_mode != "Default":
        form_data.add_field("texture_mode", texture_mode)
    
    # Handle tier
    if tier is not None:
        form_data.add_field("tier", tier)
    
    # Handle ta_pose
    if ta_pose is not None:
        form_data.add_field("ta_pose", str(ta_pose).lower())
    
    # Handle hd_texture
    if hd_texture is not None:
        form_data.add_field("hd_texture", str(hd_texture).lower())
    
    # Handle model_early_export
    if model_early_export is not None:
        form_data.add_field("model_early_export", str(model_early_export).lower())
    
    # Handle is_micro
    if is_micro is not None:
        form_data.add_field("is_micro", str(is_micro).lower())

    # Handle geometry_instruct_mode
    if geometry_instruct_mode is not None:
        form_data.add_field("geometry_instruct_mode", geometry_instruct_mode)

    # Handle bbox

    if bbox is not None:
        # Format as [width, height, length] for API
        form_data.add_field("bbox_condition", str(bbox))

    if height_cm is not None:
        form_data.add_field("height", str(height_cm))

    for field in form_data._fields:
        print(field)
        
    # Post requests
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=form_data) as resp:
            response = await resp.json()
            print(response)

            if resp.status in [200, 201]:
                job_uuid = response.get("uuid", None)
                subscription_key = response.get("jobs", {}).get("subscription_key", None)

                if job_uuid is None or subscription_key is None:
                    return ERROR_MEG["RODIN_ERROR"], None, None
                else: 
                    return "Success! Job submitted successfully.", job_uuid, subscription_key
            else:
                return ERROR_MEG["RODIN_ERROR"], None, None
            
async def poll_job_status(
    api_key: str,
    job_uuid: str,
    subscription_key: str,
) -> Tuple[str, Optional[str], Optional[str]]:
    """Poll the job status"""
    if not api_key:
        return ERROR_MEG["MISS_API_KEY"], None, None
    
    if not subscription_key:
        return ERROR_MEG["MISS_SUBSCRIPTION_KEY"], None, None
    
    if not job_uuid:
        return ERROR_MEG["MISS_JOB_UUID"], None, None
    
    
    # Prepare the request
    url = f"{RODIN_API_BASE_URL}/api/v2/status"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {"subscription_key": subscription_key}

    # Post requests
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            response = await resp.json()
            
            if resp.status in [200, 201]:
                jobs = response.get("jobs", [])
                if jobs is None or len(jobs) == 0:
                    return ERROR_MEG["NO_JOBS_FOUND"], None, response

                # Check status of all jobs
                all_done = True
                any_failed = False
                statuses = []

                for job in jobs:
                    job_status = job.get("status", "unknown")
                    statuses.append(job_status)

                    if job_status == "Failed":
                        any_failed = True
                    elif job_status != "Done":
                        all_done = False
                if all_done:
                    print(f"Task {job_uuid} statuses: {statuses}")
                    print(f"Task {job_uuid} Done!")
                    return f"Success! Task {job_uuid} All jobs have completed successfully.", "done", response
                elif any_failed:
                    return f"Failed! Task {job_uuid} Jobs have failed. Statuses: {statuses}", "failed", response
                else:
                    print(f"Task {job_uuid} statuses: {statuses}")
                    return f"Running... Task {job_uuid} Some jobs are still running. Statuses: {statuses}", "running", response
            else:
                return ERROR_MEG["UNKNOWN_ERROR"], None, response
            
async def download_results(
    api_key: str,
    job_uuid: str,
    geometry_format: str = 'glb',
) -> Tuple[str, Optional[str], Optional[str]]:
    """Download the job results"""
    if not api_key:
        return ERROR_MEG["MISS_API_KEY"], None, None
    
    if not job_uuid:
        return ERROR_MEG["MISS_JOB_UUID"], None, None
    
    # Prepare request
    url = f"{RODIN_API_BASE_URL}/api/v2/download"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {"task_uuid": job_uuid}

    # Post requests
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            response = await resp.json()

            if resp.status in [200, 201]:
                file_list = response.get("list", [])
                if file_list is None or len(file_list) == 0:
                    return ERROR_MEG["NO_FILES_FOUND"], None, None
                else: 
                    return await _download_all_file(api_key=api_key, file_list=file_list, geometry_format=geometry_format, task_uuid=job_uuid)
            else:
                print(f"❌ Error downloading files: {response}")
                return ERROR_MEG["RODIN_ERROR"], None, None

async def _download_all_file(
    api_key: str,
    file_list: list[str],
    geometry_format: str,
    task_uuid: str,
) -> Tuple[str, Optional[str], Optional[str]]:
    """Download the file"""
    if not api_key:
        return ERROR_MEG["MISS_API_KEY"], None, None
    
    if not file_list:
        return ERROR_MEG["NO_FILES_FOUND"], None, None
    
    try: 
        save_path = os.path.join(comfy_paths.get_output_directory(), datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        os.makedirs(save_path, exist_ok=True)
        download_count = 0
        preview_model_path = None
        for file_info in file_list:
            file_url = file_info.get("url", None)
            file_name = file_info.get("name", f"file_download_{download_count}").split('/')[-1]
            file_path = os.path.join(save_path, file_name)
            format_supports_preview = f'.{geometry_format.lower()}' in SUPPORTED_3D_EXTENSIONS
            
            if format_supports_preview and preview_model_path is None:
                preview_model_path = file_path
            
            if not file_url:
                continue
            print(f"[ download_files ] Downloading file: {file_path}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    with open(file_path, "wb") as f:
                        f.write(await resp.read())
            
            print(f"Downloaded {file_name}")
            download_count += 1
            
        return f"Success! Downloaded {download_count} files successfully!", preview_model_path, task_uuid
                                                

    except Exception as e:
        logging.error(f"❌ Error downloading files: {str(e)}")
        print(e)
        return ERROR_MEG["UNKNOWN_ERROR"], None, None
    
async def process_full_generation(
    api_key: str,
    images: Optional[List[str]],
    prompt: Optional[str],
    tier: str,
    seed: Optional[int],
    quality: Optional[str],
    geometry_file_format: Optional[str],
    material: Optional[str],
    texture_mode: Optional[str],
    quality_override: Optional[int],
    mesh_mode: Optional[str],
    ta_pose: Optional[bool],
    hd_texture: Optional[bool],
    model_early_export: Optional[bool],
    is_micro: Optional[bool],
    geometry_instruct_mode: Optional[str],
    bbox: Optional[str],
    height_cm: Optional[int] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Full pipeline: submit job, poll status, and download results"""

    # Step 1: Submit job
    
    status_msg, job_uuid, subscription_key = await submit_generate_job(
        api_key=api_key,
        images=images, 
        prompt=prompt, 
        seed=seed,
        quality=quality,
        quality_override=quality_override, 
        mesh_mode=mesh_mode,
        geometry_file_format=geometry_file_format,
        material=material, 
        texture_mode=texture_mode,
        tier=tier, 
        ta_pose=ta_pose, 
        hd_texture=hd_texture,
        model_early_export=model_early_export,
        is_micro=is_micro,
        geometry_instruct_mode=geometry_instruct_mode,
        bbox=bbox,
        height_cm=height_cm,
    )

    if job_uuid is None or subscription_key is None:
        logging.error(f"Failed to submit job: {status_msg}")
        print(f"Error: {status_msg}")
        return None, None
    
    print(f"Job submitted successfully! Job UUID: {job_uuid}")
    
    # Step 2: Poll for completion
    max_attempts = 360  # 30 minutes with 5-second intervals (1800 seconds)
    attempt = 0
    
    while attempt < max_attempts:
        status_msg, ready_flag, full_response = await poll_job_status(api_key=api_key, job_uuid=job_uuid, subscription_key=subscription_key)
        
        print(f"Status: {status_msg}")
        
        if ready_flag == "done":  # Job completed
            break
        elif ready_flag == "failed":
            logging.error(f"Job failed: {status_msg}")
            print(f"Error: {status_msg}")
            return None, None
        
        await asyncio.sleep(5)
        attempt += 1
    
    if attempt >= max_attempts:
        logging.error("Job polling timed out. Please check the job status.")
        print("Error: Job polling timed out after 30 minutes. Please check the job status on the Rodin dashboard.")
        return None, None
    
    download_status, model_file,  task_uuid = await download_results(api_key=api_key, job_uuid=job_uuid, geometry_format=geometry_file_format)
    print(f"Download status: {download_status}")
    
    if not model_file:
        logging.error("Failed to download model file")
        print("Error: Failed to download model file. Please check your internet connection and try again.")
        return None, None
    
    print(f"Model downloaded successfully: {model_file}")
    return model_file, task_uuid

async def submit_polygen_task(
    api_key: str,
    asset_id: str,
    model: str,
    geometry_file_format: Optional[str],
    mesh_mode: Optional[str],
    quality: Optional[str],
) -> Tuple[str, Optional[str], Optional[str]]:
    """Submit a polygen task to the Rodin API"""

    if not api_key:
        return ERROR_MEG["MISS_API_KEY"], None, None
    
    # Prepare the request
    url = f"{RODIN_API_BASE_URL}/api/v2/polygen"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    # Prepare data

    if not model and not asset_id:
        return ERROR_MEG["MISS_MODEL_ASSET_ID"], None, None
    
    if model and asset_id:
        return ERROR_MEG["PLEASE_ONLY_MODEL_OR_ASSET_ID"], None, None

    
    # Prepare form_data
    form_data = aiohttp.FormData()

    if model:
        if isinstance(model, str):
            file_ext = os.path.splitext(model)[1].lower()
            content_type_map = {
                '.obj': 'model/obj',
                '.glb': 'model/gltf-binary',
                '.stl': 'model/stl',
                '.fbx': 'model/fbx',
                '.usdz': 'model/vnd.usdz+zip',
                '.usda': 'model/usda',
                '.usdc': 'model/usdc',
            }
            content_type = content_type_map.get(file_ext, 'application/octet-stream')
            with open(model, "rb") as f:
                file_content = f.read()
                form_data.add_field("model", file_content, filename=os.path.basename(model), content_type=content_type)
    
    if asset_id:
        form_data.add_field("asset_id", asset_id)

    if geometry_file_format:
        form_data.add_field("geometry_file_format", geometry_file_format)
    if mesh_mode:
        form_data.add_field("meshmesh_mode", mesh_mode)
    if quality:
        form_data.add_field("quality", quality)

    # Send the request
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=form_data) as resp:
            response = await resp.json()
            print(response)

            if resp.status in [200, 201]:
                job_uuid = response.get("uuid", None)
                subscription_key = response.get("jobs", {}).get("subscription_key", None)

                if job_uuid is None or subscription_key is None:
                    return ERROR_MEG["RODIN_POLYGEN_ERROR"], None, None
                else: 
                    return "Success! Polygen task submitted successfully.", job_uuid, subscription_key
            else:
                return ERROR_MEG["RODIN_POLYGEN_ERROR"], None, None
            
async def full_polygen_pipeline(
    api_key: str,
    asset_id: str,
    model: str,
    geometry_file_format: Optional[str],
    mesh_mode: Optional[str],
    quality: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """Full pipeline: submit polygen task, poll status, and download results"""

    # Step 1: Submit polygen task
    
    status_msg, job_uuid, subscription_key = await submit_polygen_task(
        api_key=api_key,
        asset_id=asset_id,
        model=model,
        geometry_file_format=geometry_file_format,
        mesh_mode=mesh_mode,
        quality=quality,
    )

    if job_uuid is None or subscription_key is None:
        logging.error(f"Failed to submit polygen task: {status_msg}")
        print(f"Error: {status_msg}")
        return None, None
    
    print(f"Polygen task submitted successfully! UUID: {job_uuid}")
    
    # Step 2: Poll for completion
    max_attempts = 360  # 30 minutes with 5-second intervals (1800 seconds)
    attempt = 0
    
    while attempt < max_attempts:
        status_msg, ready_flag, full_response = await poll_job_status(api_key=api_key, job_uuid=job_uuid, subscription_key=subscription_key)
        
        print(f"Status: {status_msg}")
        
        if ready_flag == "done":  # Polygen task completed
            break
        elif ready_flag == "failed":
            logging.error(f"Polygen task failed: {status_msg}")
            print(f"Error: {status_msg}")
            return None, None
        
        await asyncio.sleep(5)
        attempt += 1
    
    if attempt >= max_attempts:
        logging.error("Polygen task polling timed out. Please check the task status.")
        print("Error: Polygen task polling timed out after 30 minutes. Please check the task status on the Rodin dashboard.")
        return None, None
    
    download_status, model_file,  _ = await download_results(api_key=api_key, job_uuid=job_uuid, geometry_format=geometry_file_format)
    print(f"Download status: {download_status}")
    
    if not model_file:
        logging.error("Failed to download model file")
        print("Error: Failed to download model file. Please check your internet connection and try again.")
        return None, None
    
    print(f"Model downloaded successfully: {model_file}")
    return model_file, job_uuid
