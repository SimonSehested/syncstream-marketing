# DNS records

## DMARC

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
