# CloudScale AI — Frequently Asked Questions (FAQ) & Technical Troubleshooting

---

## 1. Where do I find or regenerate my production API Key?
To obtain or manage your organization API credentials:
1. Log in to your CloudScale AI dashboard and navigate to **Workspace Settings > Developers & API Keys**.
2. Click **Create Secret Key**, assign a descriptive name, and specify access scopes (Read/Write/Admin).
3. If an API key is ever compromised, click **Revoke & Regenerate** to invalidate the old token immediately and generate a new key with zero downtime for remaining keys.
4. Complete interactive OpenAPI / Swagger specifications and code examples in Python, TypeScript, Go, and cURL are available at `https://docs.cloudscale.ai/api`.

---

## 2. What should I do if I encounter an HTTP 429 Too Many Requests error?
- CloudScale AI enforces rate limits based on your subscription tier (Starter: 1,000 req/hr; Pro: 25,000 req/hr; Enterprise: 50,000+ req/hr).
- When a rate limit is exceeded, the server returns an `HTTP 429` status code along with standard headers:
  - `Retry-After`: Specifies the number of seconds until your quota window resets.
  - `X-RateLimit-Limit`: Maximum requests allowed in the current hour window.
  - `X-RateLimit-Remaining`: Requests remaining in the current window.
- If your application frequently experiences bursts of high traffic, consider enabling our **API Throughput Booster Add-on** ($50/mo for an additional 25,000 req/hr) or upgrading to Enterprise for dedicated throughput.

---

## 3. How do I invite team members and configure role-based access control (RBAC)?
- Navigate to **Workspace Settings > Team Members** and click **Invite Member**.
- Available permission roles:
  - **Owner:** Full platform control, billing administration, subscription changes, and workspace deletion.
  - **Admin:** Can create projects, invite/remove members, and manage automation rules.
  - **Member:** Can create, edit, and collaborate on assigned projects, tasks, and CRM deals.
  - **Viewer:** Read-only access to assigned dashboards and reports without modification rights.

---

## 4. Can we migrate our existing workflows from Jira, Trello, Asana, or Monday.com?
Yes! CloudScale AI includes an automated **One-Click Migration Wizard**:
1. Go to **Workspace Settings > Integrations & Data Import**.
2. Select your source tool (Jira, Trello, Asana, Linear, or CSV/Excel).
3. Authorize read access, map your custom fields, and click **Start Import**.
4. The migration engine imports tasks, assignees, tags, comments, and attachments within minutes while preserving historical timestamps.

---

## 5. How do I recover Two-Factor Authentication (2FA) or transfer workspace ownership?
- **Password Reset:** Use the "Forgot Password" link on the sign-in screen to receive a secure time-limited reset token via email.
- **2FA Lockout:** If you lose access to your authenticator app, you can use one of the emergency backup codes provided during initial setup. If backup codes are lost, the registered organization owner must contact support for cryptographic identity verification.
- **Ownership Transfer:** Workspace ownership transfers must be initiated by the current Owner from settings or escalated to senior support for corporate verification.

---

## 6. Support Channels & Operating Hours
- **AI Automated Support:** Active **24 hours a day, 7 days a week, 365 days a year**, providing instant technical resolution and intelligent triage.
- **Human Tier-2 Engineering & Billing Specialists:** Available Monday through Friday from 8:00 AM to 8:00 PM EST, and 24/7 on-call for Critical (P0) incidents.
