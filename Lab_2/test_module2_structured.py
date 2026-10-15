from enum import Enum
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LogAnalysis(BaseModel):
    severity: SeverityLevel = Field(
        description="Severity level of the incident: LOW, MEDIUM, HIGH, or CRITICAL."
    )
    error_code: int = Field(
        description="Integer HTTP or system error code extracted from the log, or -1 if no error code exists."
    )
    is_compromised: bool = Field(
        description="True if active unauthorized access succeeded or security was bypassed; False otherwise."
    )
    summary: str = Field(
        description="One-sentence technical summary of the event."
    )
    recommended_fix: list[str] = Field(
        description="List of concrete remediation steps to mitigate or fix the issue."
    )


SYSTEM_PROMPT = """You are an expert Security Information and Event Management (SIEM) log analyst.
Parse the incoming raw server log and extract structured security incident telemetry according to these rules:

1. severity:
   - LOW: Routine operations, successful intended logins, low-impact warnings.
   - MEDIUM: Failed login attempts, minor misconfigurations, standard errors.
   - HIGH: Suspicious exploit attempts, privilege escalation attempts, critical system errors.
   - CRITICAL: Active security breaches, successful unauthorized access (e.g. root login bypass), zero-day exploitation.

2. error_code:
   - Extract the numerical system or HTTP error code explicitly referenced in the log (e.g., ErrorCode=401 yields 401).
   - Return -1 if no explicit error code is present in the text.

3. is_compromised:
   - Return true if an unauthorized party successfully gained access, bypassed authentication, or compromised the host.
   - Return false if the attack was blocked, failed, or was a routine authorized operation.

4. summary:
   - Provide a precise, 1-sentence technical overview of the security event.

5. recommended_fix:
   - Provide a non-empty list of concrete technical steps to mitigate the threat."""


def parse_server_log(raw_log: str) -> LogAnalysis:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Analyze the following raw server log:\n{raw_log}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=LogAnalysis,
        ),
    )
    # Validate and deserialize JSON string directly into the Pydantic object
    return LogAnalysis.model_validate_json(response.text)


if __name__ == "__main__":
    sample = (
        "2026-10-15 02:11:44 [ALERT] sshd[9012]: Accepted password for root "
        "from 198.51.100.77 port 44122 ssh2 (ErrorCode=401 bypassed via PAM bug)"
    )
    print(parse_server_log(sample).model_dump_json(indent=2))


# --- Automated Unit Test (Run with: pytest test_module2_structured.py) ---
def test_ssh_breach_log_parsing():
    sample_log = (
        "2026-10-15 02:11:44 [ALERT] sshd[9012]: Accepted password for root "
        "from 198.51.100.77 port 44122 ssh2 (ErrorCode=401 bypassed via PAM bug)"
    )
    result = parse_server_log(sample_log)

    assert result.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    assert result.error_code == 401
    assert result.is_compromised is True
    assert len(result.recommended_fix) >= 1