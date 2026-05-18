# DNS records

## DMARC

### Current Setup (Monitoring)
Create this TXT record at your DNS provider:

Name:

```text
_dmarc
```

Value:

```text
v=DMARC1; p=none; rua=mailto:dmarc@syncstream.app
```

This enables DMARC monitoring for `syncstream.app` without rejecting or quarantining mail while deliverability is being validated.

### Upgrade Path

Once you have verified email deliverability is working (check Resend dashboard for bounce/complaint rates), upgrade DMARC policy in this order:

**Phase 1 - Quarantine (after 2-4 weeks of clean sending):**
```text
v=DMARC1; p=quarantine; rua=mailto:dmarc@syncstream.app
```
This tells receiving servers to send suspicious mail to spam rather than rejecting it.

**Phase 2 - Reject (after 4+ weeks of clean sending):**
```text
v=DMARC1; p=reject; rua=mailto:dmarc@syncstream.app
```
This fully rejects unauthenticated mail. Only do this when confident SPF/DKIM are properly configured.

### Verifying DNS Records

Use these tools to verify your DNS records are live:
- **SPF Check:** https://mxtoolbox.com/spf.aspx
- **DKIM Check:** https://mxtoolbox.com/dkim.aspx
- **DMARC Check:** https://mxtoolbox.com/dmarc.aspx
- **Full DNS Check:** https://dnschecker.org/

### Required DNS Records for Email

| Record Type | Name | Value | Purpose |
|-------------|------|-------|---------|
| SPF | @ or mail | `v=spf1 include:resend.com ~all` | Authorizes Resend to send mail for your domain |
| DKIM | (managed by Resend) | Resend provides this via DNS after domain verification | Digitally signs your emails |
| DMARC | _dmarc | `v=DMARC1; p=none; rua=mailto:dmarc@syncstream.app` | Aggregate reports on email authentication |
