"""Serviço para envio de mensagens via Telegram Bot API"""

import json
import logging
import re
import unicodedata

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


_TELEGRAM_FALLBACK_TEXT = "\u3164"  # Hangul Filler (invisível, mas não é whitespace/Cf)

# Telegram MarkdownV2 exige escaping de caracteres especiais.
_MDV2_SPECIAL_CHARS_RE = re.compile(r"([_\*\[\]\(\)~`>#+\-=|\{\}\.\!\\])")


def _escape_markdownv2_text(text: str) -> str:
    if not text:
        return ""
    return _MDV2_SPECIAL_CHARS_RE.sub(r"\\\1", text)


def _escape_markdownv2_url(url: str) -> str:
    if not url:
        return ""
    url = str(url).strip().replace(" ", "%20")
    # No MarkdownV2 do Telegram, o URL dentro de (...) precisa escapar pelo menos: \\ e parênteses.
    url = url.replace("\\", "\\\\")
    url = url.replace("(", "\\(").replace(")", "\\)")
    return url


def _convert_simple_html_to_markdown(text: str) -> str:
    """Compat: converte um subconjunto simples de HTML previamente salvo para MarkdownV2.

    Ajuda a não "quebrar" flows já existentes que tinham <b>/<i>/<u>/<s>/<a href>.
    """

    if not text:
        return ""

    # Links primeiro
    text = re.sub(
        r"<a\s+href=\"([^\"]+)\">(.*?)</a>",
        lambda m: f"[{m.group(2)}]({m.group(1)})",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Estilos simples
    replacements = [
        (r"<\s*(b|strong)\s*>", "*"),
        (r"<\s*/\s*(b|strong)\s*>", "*"),
        (r"<\s*(i|em)\s*>", "_"),
        (r"<\s*/\s*(i|em)\s*>", "_"),
        (r"<\s*(u|ins)\s*>", "__"),
        (r"<\s*/\s*(u|ins)\s*>", "__"),
        (r"<\s*(s|strike|del)\s*>", "~"),
        (r"<\s*/\s*(s|strike|del)\s*>", "~"),
    ]
    for pat, rep in replacements:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)

    return text


def _sanitize_telegram_markdownv2(text: str) -> str:
    """Gera MarkdownV2 válido para Telegram a partir de texto livre.

    Estratégia:
    - Converte HTML simples legado em Markdown.
    - Preserva tokens de formatação gerados pelo editor (bold/italic/underline/strike/link).
    - Escapa o restante para evitar erros: "can't parse entities".
    """

    if not text:
        return ""

    text = _convert_simple_html_to_markdown(text)

    token_specs: list[tuple[str, re.Pattern]] = [
        ("link", re.compile(r"\[(?P<label>[^\]]*?)\]\((?P<url>[^\)]*?)\)")),
        ("underline", re.compile(r"__(?P<text>.+?)__", flags=re.DOTALL)),
        ("bold", re.compile(r"\*(?P<text>.+?)\*", flags=re.DOTALL)),
        ("strike", re.compile(r"~(?P<text>.+?)~", flags=re.DOTALL)),
        # Italic por último para reduzir conflitos com underline
        ("italic", re.compile(r"_(?P<text>.+?)_", flags=re.DOTALL)),
    ]

    tokens: list[tuple[str, dict[str, str]]] = []
    parts: list[str] = []
    i = 0
    n = len(text)

    def _next_match(start_idx: int):
        best = None
        for kind, rx in token_specs:
            m = rx.search(text, start_idx)
            if not m:
                continue
            if best is None or m.start() < best[2].start():
                best = (kind, rx, m)
        return best

    while i < n:
        found = _next_match(i)
        if not found:
            parts.append(_escape_markdownv2_text(text[i:]))
            break

        kind, _rx, m = found
        if m.start() > i:
            parts.append(_escape_markdownv2_text(text[i:m.start()]))

        token_id = len(tokens)
        placeholder = f"\u0000TOK{token_id}\u0000"
        parts.append(placeholder)

        tokens.append((kind, m.groupdict()))
        i = m.end()

    out = "".join(parts)

    for token_id, (kind, gd) in enumerate(tokens):
        placeholder = f"\u0000TOK{token_id}\u0000"
        if kind == "link":
            label = _escape_markdownv2_text(gd.get("label") or "")
            url = _escape_markdownv2_url(gd.get("url") or "")
            rendered = f"[{label}]({url})"
        else:
            inner = _escape_markdownv2_text(gd.get("text") or "")
            if kind == "bold":
                rendered = f"*{inner}*"
            elif kind == "italic":
                rendered = f"_{inner}_"
            elif kind == "underline":
                rendered = f"__{inner}__"
            elif kind == "strike":
                rendered = f"~{inner}~"
            else:
                rendered = inner

        out = out.replace(placeholder, rendered)

    return out


def _ensure_telegram_non_empty_text(text: str | None) -> str:
    """Telegram rejeita textos vazios/whitespace e costuma rejeitar chars só de formatação (ex: ZW*).

    Garante um texto minimamente não-vazio e aceito, preservando a intenção de "apenas botões".
    """

    if text is None:
        return _TELEGRAM_FALLBACK_TEXT

    if not isinstance(text, str):
        text = str(text)

    # Primeiro: vazio/whitespace puro
    if not text.strip():
        return _TELEGRAM_FALLBACK_TEXT

    # Segundo: apenas caracteres de formatação (Unicode category Cf) e whitespace
    has_substantive_char = any(
        (not ch.isspace()) and unicodedata.category(ch) != "Cf" for ch in text
    )
    if not has_substantive_char:
        return _TELEGRAM_FALLBACK_TEXT

    return text


def send_telegram_message(bot_token: str, chat_id: int | str, text: str, reply_markup: dict = None, parse_mode: str = "MarkdownV2") -> dict | None:
    """
    Envia uma mensagem de texto via Telegram Bot API
    
    Args:
        bot_token: Token do bot Telegram
        chat_id: ID do chat de destino
        text: Texto da mensagem
        reply_markup: Markup para botões inline (opcional)
        parse_mode: Modo de parse do Telegram (default: MarkdownV2)
        
    Returns:
        dict com a resposta da API ou None em caso de erro
    """
    settings = get_settings()
    url = f"{settings.TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"

    fixed_text = _ensure_telegram_non_empty_text(text)
    if fixed_text != text:
        logger.info("Texto vazio/format-only detectado; aplicando fallback para Telegram")
    
    if parse_mode == "MarkdownV2":
        safe_text = _sanitize_telegram_markdownv2(fixed_text)
    else:
        safe_text = fixed_text

    payload = {
        "chat_id": chat_id,
        "text": safe_text,
        "parse_mode": parse_mode,
    }
    
    if reply_markup:
        # Com httpx(..., json=payload), o Telegram espera reply_markup como OBJETO JSON.
        # Se vier como string, tenta converter; se falhar, envia como está.
        if isinstance(reply_markup, str):
            try:
                payload["reply_markup"] = json.loads(reply_markup)
            except Exception:
                payload["reply_markup"] = reply_markup
        else:
            payload["reply_markup"] = reply_markup
    
    def _post_send_message(send_payload: dict) -> httpx.Response:
        with httpx.Client() as client:
            return client.post(url, json=send_payload, timeout=10.0)

    try:
        response = _post_send_message(payload)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Mensagem enviada com sucesso para chat_id={chat_id}")
        return result
    except httpx.HTTPStatusError as e:
        status_code = getattr(e.response, "status_code", None)
        response_text = getattr(e.response, "text", "")
        logger.error(
            "Erro HTTP ao enviar mensagem Telegram: %s - %s | payload_text=%r (len=%s)",
            status_code,
            response_text,
            payload.get("text"),
            len(str(payload.get("text") or "")),
        )

        # Garantia final: se o Telegram insistir que o texto está vazio, reenvia com um texto visível minimalista.
        if status_code == 400 and "text must be non-empty" in (response_text or ""):
            retry_payload = dict(payload)
            retry_payload["text"] = "OK"
            try:
                retry_resp = _post_send_message(retry_payload)
                retry_resp.raise_for_status()
                logger.warning(
                    "Retry aplicado (texto='OK') para evitar 400 text must be non-empty | chat_id=%s",
                    chat_id,
                )
                return retry_resp.json()
            except Exception as retry_err:
                logger.error(f"Retry falhou ao enviar mensagem Telegram: {str(retry_err)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem Telegram: {str(e)}")
        return None


def send_telegram_photo(bot_token: str, chat_id: int | str, photo_url: str, caption: str = "") -> dict | None:
    """
    Envia uma foto via Telegram Bot API
    
    Suporta:
    - URL pública (http://..., https://...)
    - Arquivo local (/api/v1/media/...) - faz upload direto
    
    Args:
        bot_token: Token do bot Telegram
        chat_id: ID do chat de destino
        photo_url: URL da foto ou path local
        caption: Legenda da foto (opcional)
        
    Returns:
        dict com a resposta da API ou None em caso de erro
    """
    settings = get_settings()
    url = f"{settings.TELEGRAM_API_BASE}/bot{bot_token}/sendPhoto"
    
    # Verificar se é URL local (localhost ou /api/v1/media/...)
    is_local = (
        'localhost' in photo_url or 
        '127.0.0.1' in photo_url or 
        photo_url.startswith('/api/v1/media/')
    )
    
    if is_local:
        # Extrair filename do path
        filename = photo_url.split('/')[-1]
        file_path = f"uploads/images/{filename}"
        
        logger.info(f"Arquivo local detectado. Fazendo upload direto: {file_path}")
        
        # Enviar arquivo via multipart/form-data
        try:
            import os
            if not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado: {file_path}")
                return None
            
            with open(file_path, 'rb') as photo_file:
                files = {'photo': (filename, photo_file, 'image/png')}
                data = {'chat_id': chat_id}
                
                if caption:
                    data['caption'] = _sanitize_telegram_markdownv2(caption)
                    data['parse_mode'] = 'MarkdownV2'
                
                with httpx.Client() as client:
                    response = client.post(url, files=files, data=data, timeout=30.0)
                    response.raise_for_status()
                    result = response.json()
                    logger.info(f"Foto enviada com sucesso (upload direto) para chat_id={chat_id}")
                    return result
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {file_path}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar foto Telegram (upload): {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao enviar foto Telegram (upload): {str(e)}")
            return None
    else:
        # URL pública - enviar via JSON
        payload = {
            "chat_id": chat_id,
            "photo": photo_url
        }
        
        if caption:
            payload["caption"] = _sanitize_telegram_markdownv2(caption)
            payload["parse_mode"] = "MarkdownV2"
        
        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                logger.info(f"Foto enviada com sucesso (URL) para chat_id={chat_id}")
                return result
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar foto Telegram: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao enviar foto Telegram: {str(e)}")
            return None


def send_telegram_audio(bot_token: str, chat_id: int | str, audio_url: str, title: str = "") -> dict | None:
    """
    Envia um áudio via Telegram Bot API
    
    Suporta:
    - URL pública (http://..., https://...)
    - Arquivo local (/api/v1/media/...) - faz upload direto
    
    Args:
        bot_token: Token do bot Telegram
        chat_id: ID do chat de destino
        audio_url: URL do áudio ou path local
        title: Título do áudio (opcional)
        
    Returns:
        dict com a resposta da API ou None em caso de erro
    """
    settings = get_settings()
    url = f"{settings.TELEGRAM_API_BASE}/bot{bot_token}/sendAudio"
    
    # Verificar se é URL local (localhost ou /api/v1/media/...)
    is_local = (
        'localhost' in audio_url or 
        '127.0.0.1' in audio_url or 
        audio_url.startswith('/api/v1/media/')
    )
    
    if is_local:
        # Extrair filename do path
        filename = audio_url.split('/')[-1]
        file_path = f"uploads/audio/{filename}"  # Corrigido: audio (sem 's')
        
        logger.info(f"Arquivo de áudio local detectado. Fazendo upload direto: {file_path}")
        
        # Enviar arquivo via multipart/form-data
        try:
            import os
            if not os.path.exists(file_path):
                logger.error(f"Arquivo de áudio não encontrado: {file_path}")
                return None
            
            with open(file_path, 'rb') as audio_file:
                files = {'audio': (filename, audio_file, 'audio/mpeg')}
                data = {'chat_id': chat_id}
                
                if title:
                    data['title'] = title
                
                with httpx.Client() as client:
                    response = client.post(url, files=files, data=data, timeout=30.0)
                    response.raise_for_status()
                    result = response.json()
                    logger.info(f"Áudio enviado com sucesso (upload direto) para chat_id={chat_id}")
                    return result
        except FileNotFoundError:
            logger.error(f"Arquivo de áudio não encontrado: {file_path}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar áudio Telegram (upload): {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao enviar áudio Telegram (upload): {str(e)}")
            return None
    else:
        # URL pública - enviar via JSON
        payload = {
            "chat_id": chat_id,
            "audio": audio_url
        }
        
        if title:
            payload["title"] = title

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=20.0)
                response.raise_for_status()
                logger.info(f"Áudio enviado com sucesso (URL) para chat_id={chat_id}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar áudio Telegram: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao enviar áudio Telegram: {str(e)}")
            return None


def send_telegram_video(bot_token: str, chat_id: int | str, video_url: str, caption: str = "") -> dict | None:
    """
    Envia um vídeo via Telegram Bot API
    
    Suporta:
    - URL pública (http://..., https://...)
    - Arquivo local (/api/v1/media/...) - faz upload direto
    
    Args:
        bot_token: Token do bot Telegram
        chat_id: ID do chat de destino
        video_url: URL do vídeo ou path local
        caption: Legenda do vídeo (opcional)
        
    Returns:
        dict com a resposta da API ou None em caso de erro
    """
    settings = get_settings()
    url = f"{settings.TELEGRAM_API_BASE}/bot{bot_token}/sendVideo"
    
    # Verificar se é URL local (localhost ou /api/v1/media/...)
    is_local = (
        'localhost' in video_url or 
        '127.0.0.1' in video_url or 
        video_url.startswith('/api/v1/media/')
    )
    
    if is_local:
        # Extrair filename do path
        filename = video_url.split('/')[-1]
        file_path = f"uploads/video/{filename}"  # Corrigido: video (sem 's')
        
        logger.info(f"Arquivo de vídeo local detectado. Fazendo upload direto: {file_path}")
        
        # Enviar arquivo via multipart/form-data
        try:
            import os
            if not os.path.exists(file_path):
                logger.error(f"Arquivo de vídeo não encontrado: {file_path}")
                return None
            
            with open(file_path, 'rb') as video_file:
                files = {'video': (filename, video_file, 'video/mp4')}
                data = {'chat_id': chat_id}
                
                if caption:
                    data['caption'] = _sanitize_telegram_markdownv2(caption)
                    data['parse_mode'] = 'MarkdownV2'
                
                with httpx.Client() as client:
                    response = client.post(url, files=files, data=data, timeout=60.0)
                    response.raise_for_status()
                    result = response.json()
                    logger.info(f"Vídeo enviado com sucesso (upload direto) para chat_id={chat_id}")
                    return result
        except FileNotFoundError:
            logger.error(f"Arquivo de vídeo não encontrado: {file_path}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar vídeo Telegram (upload): {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao enviar vídeo Telegram (upload): {str(e)}")
            return None
    else:
        # URL pública - enviar via JSON
        payload = {
            "chat_id": chat_id,
            "video": video_url
        }
        
        if caption:
            payload["caption"] = _sanitize_telegram_markdownv2(caption)
            payload["parse_mode"] = "MarkdownV2"

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=20.0)
                response.raise_for_status()
                logger.info(f"Vídeo enviado com sucesso (URL) para chat_id={chat_id}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar vídeo Telegram: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao enviar vídeo Telegram: {str(e)}")
            return None


def send_telegram_video_note(bot_token: str, chat_id: int | str, video_url: str) -> dict | None:
    """
    Envia um vídeo bolinha (video note) via Telegram Bot API
    
    IMPORTANTE: Video notes devem ser:
    - Vídeos circulares/redondos
    - Proporção 1:1 (quadrado)
    - Duração <= 1 minuto
    - Máximo 640px de largura/altura
    - Video notes APENAS aceitam upload de arquivo (não URL)
    
    Args:
        bot_token: Token do bot Telegram
        chat_id: ID do chat de destino
        video_url: Path do arquivo local (/api/v1/media/...)
        
    Returns:
        dict com a resposta da API ou None em caso de erro
    """
    settings = get_settings()
    url = f"{settings.TELEGRAM_API_BASE}/bot{bot_token}/sendVideoNote"
    
    print(f"🔵 [VIDEO NOTE] Iniciando envio de vídeo bolinha")
    print(f"   📎 URL recebida: {video_url}")
    
    # Extrair filename do path (suporta URLs locais e paths)
    if '/api/v1/media/video/' in video_url or '/api/v1/media/audios/' in video_url:
        filename = video_url.split('/')[-1].split('?')[0]
        print(f"   📄 Filename extraído: {filename}")
    elif video_url.startswith('http'):
        print(f"❌ [VIDEO NOTE] Video notes não suportam URLs externas: {video_url}")
        logger.error(f"❌ [VIDEO NOTE] Video notes não suportam URLs externas: {video_url}")
        return None
    else:
        filename = video_url
        print(f"   📄 Filename direto: {filename}")
    
    file_path = f"uploads/video/{filename}"
    print(f"   📁 Path completo: {file_path}")
    
    try:
        import os
        if not os.path.exists(file_path):
            print(f"❌ [VIDEO NOTE] Arquivo não encontrado: {file_path}")
            logger.error(f"❌ [VIDEO NOTE] Arquivo não encontrado: {file_path}")
            return None
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(file_path)
        print(f"📊 [VIDEO NOTE] Tamanho: {file_size / (1024*1024):.2f} MB")
        
        # Validar dimensões do vídeo (deve ser quadrado para video_note)
        try:
            import cv2
            video = cv2.VideoCapture(file_path)
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = int(video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS))
            video.release()
            
            print(f"📐 [VIDEO NOTE] Dimensões: {width}x{height}")
            print(f"⏱️  [VIDEO NOTE] Duração: {duration}s")
            
            # Avisar se não for quadrado
            if width != height:
                print(f"⚠️  [VIDEO NOTE] AVISO: Vídeo não é quadrado ({width}x{height})")
                print(f"   O Telegram pode enviar como vídeo normal em vez de bolinha.")
                print(f"   Para garantir vídeo bolinha, use vídeo quadrado (ex: 480x480, 640x640)")
            
            # Avisar se exceder 640px
            if width > 640 or height > 640:
                print(f"⚠️  [VIDEO NOTE] AVISO: Dimensões maiores que 640px")
                print(f"   Recomendado: máximo 640x640")
                
            # Avisar se duração > 60s
            if duration > 60:
                print(f"⚠️  [VIDEO NOTE] AVISO: Duração maior que 1 minuto ({duration}s)")
                print(f"   Recomendado: máximo 60 segundos")
        except Exception as e:
            print(f"⚠️  [VIDEO NOTE] Não foi possível validar dimensões: {str(e)}")
            print(f"   Continuando o envio mesmo assim...")
        
        # Abrir arquivo e enviar
        print(f"📤 [VIDEO NOTE] Enviando para Telegram...")
        
        with open(file_path, 'rb') as video_file:
            files = {'video_note': (filename, video_file, 'video/mp4')}
            data = {'chat_id': str(chat_id)}
            
            with httpx.Client() as client:
                response = client.post(url, files=files, data=data, timeout=60.0)
                
                print(f"📥 [VIDEO NOTE] Status: {response.status_code}")
                
                response.raise_for_status()
                result = response.json()
                
                # Verificar se o Telegram realmente enviou como video_note
                if result.get('ok') and 'result' in result:
                    message_result = result['result']
                    if 'video_note' in message_result:
                        print(f"✅ [VIDEO NOTE] SUCESSO! Enviado como VÍDEO BOLINHA! 🎬⭕")
                    elif 'video' in message_result:
                        print(f"⚠️  [VIDEO NOTE] Telegram enviou como VÍDEO NORMAL (não bolinha)")
                        print(f"   Motivo: Vídeo não é quadrado. Use proporção 1:1 para vídeo bolinha.")
                    else:
                        print(f"✅ [VIDEO NOTE] Enviado!")
                
                logger.info(f"✅ [VIDEO NOTE] Vídeo enviado com sucesso!")
                return result
                
    except FileNotFoundError:
        print(f"❌ [VIDEO NOTE] Arquivo não encontrado: {file_path}")
        logger.error(f"❌ [VIDEO NOTE] Arquivo não encontrado: {file_path}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"❌ [VIDEO NOTE] Erro HTTP {e.response.status_code}")
        print(f"📄 [VIDEO NOTE] Resposta: {e.response.text}")
        logger.error(f"❌ [VIDEO NOTE] Erro HTTP {e.response.status_code}")
        return None
    except Exception as e:
        print(f"❌ [VIDEO NOTE] Erro: {str(e)}")
        logger.error(f"❌ [VIDEO NOTE] Erro: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None



