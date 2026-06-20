# Access Control Policy (ACP-211)

## Section 1 — Principle of least privilege

Every user account is granted the minimum access required to perform its role and no
more. Access requests must be approved by the data owner before they are provisioned.

## Section 2 — Multi-factor authentication

Multi-factor authentication is required for all access to systems that hold customer
PII. A single password is never sufficient on its own. Access from outside the corporate
network additionally requires a managed device that passes a posture check.

## Section 3 — Access review

Access rights must be reviewed every ninety days. The data owner confirms each account
still needs its access; any account that fails review has its access revoked within five
business days.

## Section 4 — Privileged accounts

Administrative and privileged accounts are issued only to named individuals, never
shared. Every action taken by a privileged account is written to an append-only audit log
that the account holder cannot modify or delete.
