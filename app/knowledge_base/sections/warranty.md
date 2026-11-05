# CloudScale AI — Service Level Agreement (SLA), Security & Uptime Guarantee

CloudScale AI is engineered to deliver high-availability, mission-critical infrastructure with enterprise-grade security and transparency.

---

## 1. 99.95% Uptime Commitment & SLA Credit Framework
- **Service Uptime Guarantee:** CloudScale AI commits to providing **99.9% monthly uptime for Pro tier** and **99.95% monthly uptime for Enterprise tier** across all platform core services and public APIs.
- **Financially Backed SLA Credits:**
  - If monthly uptime falls between **99.0% and 99.9%**: 10% of that month’s subscription fee is refunded as service credit.
  - If monthly uptime falls between **95.0% and 98.9%**: 25% service credit is granted.
  - If monthly uptime drops below **95.0%**: 50% service credit is granted.
- **Real-Time Transparency:** Live uptime metrics and incident history are publicly monitored 24/7 at `https://status.cloudscale.ai`.

---

## 2. Enterprise Security Architecture & Compliance
1. **End-to-End Encryption:**
   - **Data at Rest:** All tenant databases, document vaults, and attachments are encrypted using military-grade **AES-256**.
   - **Data in Transit:** All incoming and outgoing network traffic enforces **TLS 1.3** and HTTPS / WSS with strict HSTS headers.
2. **Automated Geo-Redundant Backups:**
   - Complete encrypted snapshots of all workspace databases are performed automatically **every 6 hours**.
   - Backups are mirrored across isolated multi-region cloud data centers with automated point-in-time recovery (PITR) up to 30 days.
3. **Compliance & Certifications:**
   - SOC-2 Type II certified.
   - GDPR and CCPA compliant with automated data processing addendums (DPA).
   - Strict multi-tenant isolation ensuring that tenant datasets are cryptographically and logically segregated.

---

## 3. Incident Severity Levels & Support Response SLAs
- **Severity 0 (P0 - Critical Outage / Platform Down):** Initial human specialist response within **30 minutes**, 24/7/365, with continuous updates until full recovery.
- **Severity 1 (P1 - High Impact / Degraded Feature):** Initial response within **2 business hours**.
- **Severity 2 (P2 - General Support & Inquiries):** Initial response within **4 to 8 business hours**.
- The AI Customer Support Agent operates **24/7/365** to resolve inquiries, triage tickets, and immediately escalate critical blockers.
