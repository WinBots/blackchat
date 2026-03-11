"""Router para upload e gerenciamento de mídia"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse
import uuid
import os
from pathlib import Path
import shutil
from typing import Literal

router = APIRouter()

# Diretórios para armazenar uploads
UPLOAD_DIR_IMAGES = Path("uploads/images")
UPLOAD_DIR_AUDIO = Path("uploads/audio")
UPLOAD_DIR_VIDEO = Path("uploads/video")

# Criar diretórios se não existirem
UPLOAD_DIR_IMAGES.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR_AUDIO.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR_VIDEO.mkdir(parents=True, exist_ok=True)

# Tipos de arquivo permitidos por categoria
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".ogg", ".wav", ".m4a", ".opus"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg", ".mov", ".avi"}

# Tamanhos máximos (MB)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB


def get_upload_config(media_type: str):
    """Retorna configuração de upload baseado no tipo de mídia"""
    configs = {
        "image": {
            "dir": UPLOAD_DIR_IMAGES,
            "extensions": ALLOWED_IMAGE_EXTENSIONS,
            "max_size": MAX_IMAGE_SIZE,
            "url_prefix": "/api/v1/media/images"
        },
        "audio": {
            "dir": UPLOAD_DIR_AUDIO,
            "extensions": ALLOWED_AUDIO_EXTENSIONS,
            "max_size": MAX_AUDIO_SIZE,
            "url_prefix": "/api/v1/media/audio"
        },
        "video": {
            "dir": UPLOAD_DIR_VIDEO,
            "extensions": ALLOWED_VIDEO_EXTENSIONS,
            "max_size": MAX_VIDEO_SIZE,
            "url_prefix": "/api/v1/media/video"
        }
    }
    return configs.get(media_type)


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    media_type: Literal["image", "audio", "video"] = Query(..., description="Tipo de mídia: image, audio ou video")
):
    """
    Upload de mídia (imagem, áudio ou vídeo)
    
    Args:
        file: Arquivo a ser enviado
        media_type: Tipo de mídia (image, audio, video)
    
    Returns:
        dict com url da mídia
    """
    config = get_upload_config(media_type)
    if not config:
        raise HTTPException(status_code=400, detail="Tipo de mídia inválido. Use: image, audio ou video")
    
    # Validar extensão
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in config["extensions"]:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido para {media_type}. Use: {', '.join(config['extensions'])}"
        )
    
    # Ler arquivo
    contents = await file.read()
    
    # Validar tamanho
    if len(contents) > config["max_size"]:
        max_mb = config["max_size"] / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande. Máximo: {max_mb}MB"
        )
    
    # Gerar nome único
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = config["dir"] / unique_filename
    
    # Salvar arquivo
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Retornar URL
    return {
        "filename": unique_filename,
        "url": f"{config['url_prefix']}/{unique_filename}",
        "size": len(contents),
        "type": media_type
    }


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload de imagem (endpoint específico para compatibilidade)
    
    Returns:
        dict com url da imagem
    """
    return await upload_media(file=file, media_type="image")


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload de áudio
    
    Returns:
        dict com url do áudio
    """
    return await upload_media(file=file, media_type="audio")


@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload de vídeo
    
    Returns:
        dict com url do vídeo
    """
    return await upload_media(file=file, media_type="video")


@router.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve uma imagem
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        FileResponse com a imagem
    """
    file_path = UPLOAD_DIR_IMAGES / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Validar que o arquivo está dentro do diretório de uploads (segurança)
    try:
        file_path.resolve().relative_to(UPLOAD_DIR_IMAGES.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return FileResponse(file_path)


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve um arquivo de áudio
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        FileResponse com o áudio
    """
    file_path = UPLOAD_DIR_AUDIO / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Áudio não encontrado")
    
    # Validar que o arquivo está dentro do diretório de uploads (segurança)
    try:
        file_path.resolve().relative_to(UPLOAD_DIR_AUDIO.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return FileResponse(file_path)


@router.get("/video/{filename}")
async def get_video(filename: str):
    """
    Serve um arquivo de vídeo
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        FileResponse com o vídeo
    """
    file_path = UPLOAD_DIR_VIDEO / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    # Validar que o arquivo está dentro do diretório de uploads (segurança)
    try:
        file_path.resolve().relative_to(UPLOAD_DIR_VIDEO.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return FileResponse(file_path, media_type="video/mp4")


# Endpoint genérico para compatibilidade (tenta detectar o tipo)
@router.get("/{filename}")
async def get_media_file(filename: str):
    """
    Serve um arquivo de mídia (tenta detectar o tipo automaticamente)
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        FileResponse com a mídia
    """
    file_ext = Path(filename).suffix.lower()
    
    # Tentar encontrar o arquivo nos diferentes diretórios
    if file_ext in ALLOWED_IMAGE_EXTENSIONS:
        file_path = UPLOAD_DIR_IMAGES / filename
        if file_path.exists():
            try:
                file_path.resolve().relative_to(UPLOAD_DIR_IMAGES.resolve())
                return FileResponse(file_path)
            except ValueError:
                pass
    
    if file_ext in ALLOWED_AUDIO_EXTENSIONS:
        file_path = UPLOAD_DIR_AUDIO / filename
        if file_path.exists():
            try:
                file_path.resolve().relative_to(UPLOAD_DIR_AUDIO.resolve())
                return FileResponse(file_path)
            except ValueError:
                pass
    
    if file_ext in ALLOWED_VIDEO_EXTENSIONS:
        file_path = UPLOAD_DIR_VIDEO / filename
        if file_path.exists():
            try:
                file_path.resolve().relative_to(UPLOAD_DIR_VIDEO.resolve())
                return FileResponse(file_path, media_type="video/mp4")
            except ValueError:
                pass
    
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")


@router.delete("/images/{filename}")
async def delete_image(filename: str):
    """
    Deleta uma imagem
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        dict com status
    """
    file_path = UPLOAD_DIR_IMAGES / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Validar que o arquivo está dentro do diretório de uploads (segurança)
    try:
        file_path.resolve().relative_to(UPLOAD_DIR_IMAGES.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    os.remove(file_path)
    
    return {"status": "ok", "message": "Imagem deletada"}


@router.delete("/audio/{filename}")
async def delete_audio(filename: str):
    """
    Deleta um arquivo de áudio
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        dict com status
    """
    file_path = UPLOAD_DIR_AUDIO / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Áudio não encontrado")
    
    try:
        file_path.resolve().relative_to(UPLOAD_DIR_AUDIO.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    os.remove(file_path)
    
    return {"status": "ok", "message": "Áudio deletado"}


@router.delete("/video/{filename}")
async def delete_video(filename: str):
    """
    Deleta um arquivo de vídeo
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        dict com status
    """
    file_path = UPLOAD_DIR_VIDEO / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    
    try:
        file_path.resolve().relative_to(UPLOAD_DIR_VIDEO.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    os.remove(file_path)
    
    return {"status": "ok", "message": "Vídeo deletado"}

