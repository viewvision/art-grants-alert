"""SSL 인증서 체인 오류(certificate verify failed) 진단용 헬퍼.

실제 데이터 요청의 검증 방식(verify=True)은 그대로 두고, 요청이 SSL 오류로
실패했을 때만 openssl로 서버가 실제로 어떤 인증서 체인을 보내는지 확인해
경고 메시지에 덧붙인다. 원인(중간 인증서 누락 등)을 다음 실행 로그에서
바로 확인하기 위한 목적이며, 실제 fetch의 보안 검증 자체를 약화시키지 않는다.
"""
import subprocess


def diagnose(host: str, port: int = 443) -> str:
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", f"{host}:{port}", "-servername", host, "-showcerts"],
            input="",
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout + result.stderr
        cert_count = output.count("BEGIN CERTIFICATE")
        verify_lines = [line for line in output.splitlines() if "Verify return code" in line]
        subject_lines = [line for line in output.splitlines() if line.startswith("subject=") or line.startswith("issuer=")]
        summary = f"서버가 보낸 인증서 개수={cert_count}"
        if verify_lines:
            summary += f", {verify_lines[0].strip()}"
        if subject_lines:
            summary += ", " + " | ".join(subject_lines[:4])
        return summary
    except Exception as diag_e:
        return f"진단 실패: {diag_e}"
