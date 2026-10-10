"""知源问病 · 模型客户端（可选）

用标准库 urllib，不引第三方依赖。任何 OpenAI 兼容接口都能接
（智谱、DeepSeek、Kimi、本地 Ollama、vLLM 均可）。

不配 api_key 时整个系统照常工作——只是少了模型的自然语言润色，
辨证、方药、穴位、推拿、安全全部由规则引擎产出。
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

PROMPT = ""   # 文件加载后由 load_prompt() 覆盖


class LLMClient:
    def __init__(self, cfg: dict) -> None:
        self.base = (cfg.get("base_url") or "").rstrip("/")
        self.key = cfg.get("api_key") or ""
        self.model = cfg.get("model") or ""
        self.temperature = cfg.get("temperature", 0.3)
        self.timeout = cfg.get("timeout", 60)

    def enabled(self) -> bool:
        return bool(self.base and self.key and self.model)

    def chat(self, user_prompt: str, history: list[dict] | None = None) -> str:
        """调用模型。失败时返回降级提示，不抛异常打断问诊。"""
        if not self.enabled():
            return "（未配置模型 API，以下内容全部来自本地规则引擎）"
        msgs = [{"role": "system", "content": PROMPT}]
        for h in (history or [])[-6:]:
            if h.get("role") in ("user", "assistant"):
                msgs.append(h)
        msgs.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model,
            "messages": msgs,
            "temperature": self.temperature,
            "stream": False,
        }
        req = urllib.request.Request(
            f"{self.base}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            return raw["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            return f"⚠️ 模型调用失败（HTTP {e.code}）：{e.read().decode('utf-8', 'ignore')[:200]}"
        except Exception as e:                       # noqa: BLE001
            return f"⚠️ 模型调用失败：{e}"


def load_prompt() -> str:
    """主提示词放在 prompts/system.md，改那里不用改代码。"""
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "prompts" / "system.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return "你是中医执业医师，按四诊合参辨证论治。"


PROMPT = load_prompt()