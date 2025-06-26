import os
import tempfile
import time
import zipfile
from io import BytesIO
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from hloc import extract_features, match_features, pairs_from_retrieval, reconstruction

app = FastAPI()


@app.post("/sfm", response_model=None)
async def sfm_endpoint(
    images: List[UploadFile] = File(...),
    retrieval_conf_key: str = "netvlad",
    feature_conf_key: str = "superpoint_aachen",
    matcher_conf_key: str = "superpoint+lightglue",
) -> StreamingResponse | JSONResponse:
    """
    Endpoint to perform Structure from Motion (SfM) using uploaded images and specified configurations.

        Args:
            images (List[UploadFile], optional): List of images to process. Defaults to File(...).
            retrieval_conf_key (str, optional): Configuration key for retrieval. Defaults to "netvlad".
            feature_conf_key (str, optional): Configuration key for feature extraction. Defaults to "superpoint_aachen".
            matcher_conf_key (str, optional): Configuration key for matching. Defaults to "superpoint+lightglue".

        Returns:
            StreamingResponse: A zip file containing the SfM output if successful.
            JSONResponse: An error message if any issues occur during processing.
    """

    try:
        # Check if the provided configuration keys exist in the respective modules
        if retrieval_conf_key not in extract_features.confs:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"retrieval_conf_key '{retrieval_conf_key}' not found in extract_features.confs"
                },
            )
        if feature_conf_key not in extract_features.confs:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"feature_conf_key '{feature_conf_key}' not found in extract_features.confs"
                },
            )
        if matcher_conf_key not in match_features.confs:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"matcher_conf_key '{matcher_conf_key}' not found in match_features.confs"
                },
            )

        # Create temp dirs
        with tempfile.TemporaryDirectory() as tmpdir:
            images_dir = Path(tmpdir) / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            outputs = Path(tmpdir) / "outputs"
            outputs.mkdir(parents=True, exist_ok=True)
            sfm_pairs = outputs / "pairs.txt"
            sfm_dir = outputs / "sfm_colmap"

            # Save uploaded images
            for img in images:
                filename = img.filename or f"image_{int(time.time()*1000)}.jpg"
                img_path = images_dir / filename
                with open(img_path, "wb") as f:
                    f.write(await img.read())

            # Get configs
            retrieval_conf = extract_features.confs[retrieval_conf_key]
            feature_conf = extract_features.confs[feature_conf_key]
            matcher_conf = match_features.confs[matcher_conf_key]

            # Run pipeline
            retrieval_path = extract_features.main(retrieval_conf, images_dir, outputs)
            pairs_from_retrieval.main(
                retrieval_path, sfm_pairs, num_matched=min(5, len(images))
            )
            feature_path = extract_features.main(feature_conf, images_dir, outputs)
            match_path = match_features.main(
                matcher_conf, sfm_pairs, feature_conf["output"], outputs
            )
            reconstruction.main(
                sfm_dir, images_dir, sfm_pairs, feature_path, match_path
            )

            # Zip the output dir
            zip_path = Path(tmpdir) / "sfm_output.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(sfm_dir):
                    for file in files:
                        file_path = Path(root) / file
                        zipf.write(file_path, file_path.relative_to(sfm_dir.parent))

            # Read the zip file into memory before the tempdir is deleted
            with open(zip_path, "rb") as f:
                zip_bytes = BytesIO(f.read())

            zip_bytes.seek(0)
            return StreamingResponse(
                zip_bytes,
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=sfm_output.zip"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"},
        )
