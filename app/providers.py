import base64
import json
import re
import time
from pathlib import Path

import httpx

from app.config import settings
from app.schemas import ImageMetadata


def local_metadata(path, fallback=None):
    if fallback and fallback.get("subject") not in (None, "", "unknown"):
        return ImageMetadata(
            subject=fallback["subject"],
            category=fallback.get("category", "unknown"),
            attributes=fallback.get("attributes", []),
            caption=fallback.get("caption") or f'{fallback["subject"]} in a natural environment',
            confidence=float(fallback.get("confidence", 0.85)),
        )
    name = Path(path).stem.replace("-", " ").replace("_", " ")
    return ImageMetadata(
        subject=name or "unknown",
        category="unknown",
        attributes=[],
        caption=f"Image file named {name}",
        confidence=0.35,
    )


def _parse_metadata(content):
    if isinstance(content, list):
        content = "\n".join(
            item.get("text", "") for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Vision provider returned empty content.")

    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        return ImageMetadata.model_validate_json(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("Vision provider did not return a JSON object.")
        return ImageMetadata.model_validate_json(text[start:end + 1])


async def _classify_openrouter(path, start):
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    p = Path(path)
    if not p.exists():
        raise RuntimeError(f"OpenRouter requires a local image path: {path}")

    suffix = p.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(suffix)
    if not mime:
        raise RuntimeError(f"Unsupported image format for OpenRouter: {suffix}")

    encoded = base64.b64encode(p.read_bytes()).decode("ascii")
    prompt = (
        "Analyze the supplied image for a content-image relevance system. "
        "Return only a JSON object with keys subject, category, attributes, "
        "caption, confidence. attributes must be an array of strings; "
        "confidence must be between 0 and 1. Be conservative and do not "
        "infer identities or details that are not visibly supported."
    )
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}},
    ]

    model = settings.openrouter_model.strip() or "openrouter/free"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.1,
        "max_tokens": 500,
    }

    # Optional explicit fallback model IDs, comma-separated in .env.
    # Keep this empty by default: openrouter/free already selects among
    # currently available free models compatible with image input.
    fallbacks = [
        value.strip()
        for value in settings.openrouter_fallback_models.split(",")
        if value.strip()
    ]
    if fallbacks:
        payload["models"] = fallbacks

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "X-OpenRouter-Title": "FlyRank Image Relevance Engine",
    }

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        body = response.json()

    message = body["choices"][0]["message"]
    meta = _parse_metadata(message.get("content"))
    used_model = body.get("model") or model
    elapsed = int((time.perf_counter() - start) * 1000)
    return meta, "openrouter", used_model, 0.0, elapsed


async def classify_image(path, fallback=None):
    start = time.perf_counter()
    provider = settings.vision_provider.lower().strip()

    if provider == "openrouter":
        try:
            return await _classify_openrouter(path, start)
        except Exception as exc:
            # Hosted failure should not make the local demo unusable.
            meta = local_metadata(path, fallback)
            elapsed = int((time.perf_counter() - start) * 1000)
            return meta, "local-fallback", f"openrouter-failed:{type(exc).__name__}", 0.0, elapsed

    if provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("VISION_PROVIDER=gemini requires GEMINI_API_KEY in .env")
        p = Path(path)
        if not p.exists():
            raise RuntimeError(f"Gemini requires a local image path: {path}")
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        encoded = base64.b64encode(p.read_bytes()).decode("ascii")
        prompt = (
            "Inspect image. Return JSON keys subject, category, attributes, "
            "caption, confidence (0..1). Be conservative."
        )
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
        )
        payload = {
            "contents": [{"parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime, "data": encoded}},
            ]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        meta = ImageMetadata.model_validate_json(text)
        elapsed = int((time.perf_counter() - start) * 1000)
        return meta, "gemini", settings.gemini_model, settings.estimated_vision_call_cost_usd, elapsed

    if provider == "ollama":
        p = Path(path)
        if not p.exists():
            raise RuntimeError(f"Ollama requires a local image path: {path}")
        encoded = base64.b64encode(p.read_bytes()).decode("ascii")
        prompt = (
            'Return JSON: {"subject":"...","category":"...","attributes":[],'
            '"caption":"...","confidence":0.0}. Confidence 0..1; be conservative.'
        )
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/generate",
                json={
                    "model": settings.ollama_vision_model,
                    "prompt": prompt,
                    "images": [encoded],
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
            meta = ImageMetadata.model_validate_json(response.json()["response"])
        elapsed = int((time.perf_counter() - start) * 1000)
        return meta, "ollama", settings.ollama_vision_model, 0.0, elapsed

    meta = local_metadata(path, fallback)
    elapsed = int((time.perf_counter() - start) * 1000)
    return meta, "local-demo", "metadata-fallback", 0.0, elapsed
