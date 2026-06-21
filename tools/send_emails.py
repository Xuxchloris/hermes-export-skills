"""SMTP 开发信发送工具（带人工确认开关）。

设计原则（与项目合规边界一致）：
- 默认 dry-run：只预览要发什么，绝不发送。
- 真正发送必须显式加 --send，且默认逐封交互确认；--yes 可跳过确认。
- SMTP 凭证只从环境变量读取，不写进任何文件或命令行。
- 自动补退订行（unsubscribe），缺收件人邮箱的行自动跳过。
- 每次运行写一份发送日志 JSON，便于审计。

输入表格（CSV / XLSX）需包含列：to_email, subject, body
可选列：to_name, cc

用法：
  # 1. 先配环境变量（不要写进文件）
  export SMTP_HOST="smtp.example.com"
  export SMTP_PORT="587"
  export SMTP_USER="you@example.com"
  export SMTP_PASS="你的密码或授权码"
  export SMTP_FROM="you@example.com"        # 可选，默认用 SMTP_USER

  # 2. 预览（不发，强烈建议先跑这步）
  python3 tools/send_emails.py --input data/emails/send_list.csv

  # 3. 真发，逐封确认
  python3 tools/send_emails.py --input data/emails/send_list.csv --send

  # 4. 真发，不逐封确认（仅在已审核过名单时使用）
  python3 tools/send_emails.py --input data/emails/send_list.csv --send --yes
"""
from __future__ import annotations

import argparse
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from trade_utils import read_table, write_json


UNSUBSCRIBE_LINE = (
    "\n\n---\nIf you prefer not to receive further emails, "
    "reply with \"unsubscribe\" and we will remove you from our list."
)


def load_smtp_config() -> dict[str, Any]:
    """从环境变量读取 SMTP 配置，缺关键项时报错。"""
    host = os.environ.get("SMTP_HOST", "").strip()
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASS", "")
    missing = [name for name, value in (("SMTP_HOST", host), ("SMTP_USER", user), ("SMTP_PASS", password)) if not value]
    if missing:
        raise SystemExit(f"缺少 SMTP 环境变量: {', '.join(missing)}。请先 export 后再用 --send。")
    return {
        "host": host,
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": user,
        "password": password,
        "sender": os.environ.get("SMTP_FROM", "").strip() or user,
        "use_ssl": os.environ.get("SMTP_SSL", "").strip().lower() in {"1", "true", "yes"},
    }


def ensure_unsubscribe(body: str) -> str:
    """合规要求：每封开发信都要有退订方式。"""
    if "unsubscribe" in body.lower():
        return body
    return body + UNSUBSCRIBE_LINE


def build_message(sender: str, row: dict[str, Any]) -> EmailMessage:
    message = EmailMessage()
    to_name = str(row.get("to_name", "") or "").strip()
    to_email = str(row.get("to_email", "") or "").strip()
    message["From"] = sender
    message["To"] = f"{to_name} <{to_email}>" if to_name else to_email
    if row.get("cc"):
        message["Cc"] = str(row["cc"]).strip()
    message["Subject"] = str(row.get("subject", "") or "").strip()
    message.set_content(ensure_unsubscribe(str(row.get("body", "") or "")))
    return message


def validate_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """分出可发送行和需跳过行（缺邮箱/主题/正文）。"""
    sendable: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for row in rows:
        to_email = str(row.get("to_email", "") or "").strip()
        subject = str(row.get("subject", "") or "").strip()
        body = str(row.get("body", "") or "").strip()
        if "@" not in to_email:
            skipped.append({**row, "skip_reason": "missing or invalid to_email"})
        elif not subject or not body:
            skipped.append({**row, "skip_reason": "missing subject or body"})
        else:
            sendable.append(row)
    return sendable, skipped


def preview(sendable: list[dict[str, Any]], skipped: list[dict[str, Any]]) -> None:
    print(f"\n可发送 {len(sendable)} 封，跳过 {len(skipped)} 封。\n")
    for index, row in enumerate(sendable, 1):
        print(f"[{index}] 收件人: {row.get('to_email')}  主题: {row.get('subject')}")
    for row in skipped:
        print(f"[跳过] {row.get('to_email', '(无邮箱)')} — {row.get('skip_reason')}")


def confirm(prompt: str) -> bool:
    try:
        answer = input(prompt).strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes", "是"}


def open_smtp(config: dict[str, Any]) -> smtplib.SMTP:
    context = ssl.create_default_context()
    if config["use_ssl"]:
        server: smtplib.SMTP = smtplib.SMTP_SSL(config["host"], config["port"], context=context, timeout=30)
    else:
        server = smtplib.SMTP(config["host"], config["port"], timeout=30)
        server.starttls(context=context)
    server.login(config["user"], config["password"])
    return server


def send_all(sendable: list[dict[str, Any]], config: dict[str, Any], ask_each: bool) -> list[dict[str, Any]]:
    log: list[dict[str, Any]] = []
    server = open_smtp(config)
    try:
        for index, row in enumerate(sendable, 1):
            to_email = str(row.get("to_email")).strip()
            if ask_each and not confirm(f"[{index}/{len(sendable)}] 发送给 {to_email}？(y/N) "):
                log.append({"to_email": to_email, "status": "skipped_by_user"})
                continue
            message = build_message(config["sender"], row)
            try:
                server.send_message(message)
                status = "sent"
                print(f"  已发送 → {to_email}")
            except Exception as error:  # noqa: BLE001 - record per-row failure, keep going.
                status = f"failed: {error}"
                print(f"  发送失败 → {to_email}: {error}")
            log.append({"to_email": to_email, "subject": message["Subject"], "status": status})
    finally:
        server.quit()
    return log


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send outreach emails with a human-confirmation gate")
    parser.add_argument("--input", type=Path, required=True, help="CSV/XLSX with to_email, subject, body columns")
    parser.add_argument("--send", action="store_true", help="实际发送；不加则只预览（dry-run）")
    parser.add_argument("--yes", action="store_true", help="发送时不逐封确认（仅在名单已审核时使用）")
    parser.add_argument("--log", type=Path, default=Path("exports/send_log.json"), help="发送日志输出路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_table(args.input)
    sendable, skipped = validate_rows(rows)
    preview(sendable, skipped)

    if not args.send:
        print("\n[DRY-RUN] 未发送任何邮件。确认无误后加 --send 真正发送。")
        return 0

    if not sendable:
        print("\n没有可发送的邮件。")
        return 0

    config = load_smtp_config()
    if not args.yes and not confirm(f"\n即将通过 {config['host']} 发送 {len(sendable)} 封邮件，继续？(y/N) "):
        print("已取消。")
        return 0

    log = send_all(sendable, config, ask_each=not args.yes)
    log_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": str(args.input),
        "sent": sum(1 for item in log if item["status"] == "sent"),
        "results": log,
        "skipped": skipped,
    }
    write_json(args.log, log_record)
    print(f"\n完成。已发送 {log_record['sent']} 封，日志: {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




