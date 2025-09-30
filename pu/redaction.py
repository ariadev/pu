import re


def redact_text(text: str) -> str:
    redacted = text
    redacted = re.sub(r"sk-[A-Za-z0-9]{20,}", "sk-***", redacted)
    redacted = re.sub(r"(?i)bearer\s+[A-Za-z0-9._-]+", "Bearer ***", redacted)
    redacted = re.sub(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+", "***.***.***", redacted)
    redacted = re.sub(r"AKIA[0-9A-Z]{16}", "AKIA****************", redacted)
    redacted = re.sub(r"(?i)aws_secret_access_key\s*[:=]\s*\S+", "aws_secret_access_key=***", redacted)
    redacted = re.sub(r"(?i)\b([A-Z0-9_]*(PASSWORD|SECRET|TOKEN|API_KEY))\s*[:=]\s*\S+", r"\1=***", redacted)
    redacted = re.sub(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----", "<REDACTED-PRIVATE-KEY>", redacted)
    return redacted


