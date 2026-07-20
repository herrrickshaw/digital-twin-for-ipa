#!/usr/bin/env python3
"""Email alert for the twin's refresh pipeline -- credential-free by design.

Gmail SMTP creds are NEVER stored here or in n8n: they are read at runtime from
the environment (GMAIL_USER / GMAIL_APP_PASSWORD / MAIL_TO), falling back to the
EnvironmentVariables block of the machine's existing launchd mailer plist
(~/Library/LaunchAgents/com.umashankar.dailybrief.plist) -- the same source the
daily market brief already uses. The secret flows plist -> this process -> smtplib
and never lands in the repo, n8n's credential store, or any log.

Modes:
    --test                      send a test alert and exit
    --if-changes                read refresh output on stdin; send only if it
                                contains CHANGE lines (else exit 0 silently)
    --subject S --body B        explicit send (used by the n8n workflow)

Cron usage (weekly line):
    refresh_twin.py weekly 2>&1 | tee -a state/cron.log | send_twin_alert.py --if-changes
"""
import argparse, datetime, os, plistlib, smtplib, sys
from email.mime.text import MIMEText

PLIST = os.path.expanduser("~/Library/LaunchAgents/com.umashankar.dailybrief.plist")


def creds():
    user = os.environ.get("GMAIL_USER")
    pw = os.environ.get("GMAIL_APP_PASSWORD")
    to = os.environ.get("MAIL_TO")
    if not (user and pw) and os.path.exists(PLIST):
        env = plistlib.load(open(PLIST, "rb")).get("EnvironmentVariables", {})
        user = user or env.get("GMAIL_USER")
        pw = pw or env.get("GMAIL_APP_PASSWORD")
        to = to or env.get("MAIL_TO")
    return user, pw, (to or user)


def send(subject, body):
    user, pw, to = creds()
    if not (user and pw):
        print("send_twin_alert: no credentials available (env or plist) -- not sent", file=sys.stderr)
        return 1
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pw)
        s.sendmail(user, [to], msg.as_string())
    print(f"send_twin_alert: sent '{subject}' to {to}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--if-changes", action="store_true")
    ap.add_argument("--subject")
    ap.add_argument("--body")
    a = ap.parse_args()
    today = datetime.date.today().isoformat()

    if a.test:
        sys.exit(send(f"[digital-twin] test alert {today}",
                      "This is a test of the twin's alert path.\n"
                      "Credentials sourced at runtime from the dailybrief launchd plist -- "
                      "nothing stored in the repo or n8n.\n"))
    if a.if_changes:
        out = sys.stdin.read()
        changes = [l for l in out.splitlines() if l.strip().startswith("CHANGE")]
        if "registration_stopped=False" in out:
            changes.append("CHANGE UNNATI registration appears RESUMED -- verify unnati.dpiit.gov.in immediately")
        if not changes:
            sys.exit(0)
        downs = [l for l in out.splitlines() if l.strip().startswith("DOWN")]
        body = "\n".join(changes) + "\n\nPortals down:\n" + "\n".join(downs) + "\n\n--- raw ---\n" + out[-4000:]
        sys.exit(send(f"[digital-twin] {len(changes)} change(s) detected {today}", body))
    if a.subject:
        sys.exit(send(a.subject, a.body or ""))
    ap.print_help()


if __name__ == "__main__":
    main()
