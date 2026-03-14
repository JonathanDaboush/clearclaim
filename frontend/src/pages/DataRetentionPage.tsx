import { Link } from 'react-router-dom';

const EFFECTIVE_DATE = 'March 13, 2026';
const COMPANY = 'ClearClaim';

export default function DataRetentionPage() {
  return (
    <div>
      <div className="page-header">
        <nav className="flex items-center gap-1 text-xs text-meta mb-2">
          <Link to="/dashboard" className="hover:text-accent">Dashboard</Link>
          <span className="mx-1">›</span>
          <span className="text-primary">Data Retention Policy</span>
        </nav>
        <h1 className="page-title">Data Retention Policy</h1>
        <p className="page-subtitle">Effective {EFFECTIVE_DATE}</p>
      </div>

      <div className="px-6 pb-12 max-w-3xl space-y-8">
        <div className="legal-notice text-xs">
          This policy describes how long {COMPANY} retains different categories of data, why we
          retain it, and how you can request deletion. Our retention periods are designed to meet
          applicable legal obligations, including those under PIPEDA, and to preserve the legal
          integrity of signed agreements and evidence.
        </div>

        <Section title="1. Retention Periods by Category">
          <table className="w-full text-xs mt-2 border-collapse">
            <thead>
              <tr className="bg-section text-secondary uppercase tracking-wide">
                <th className="text-left px-3 py-2 border border-border font-medium">Data Category</th>
                <th className="text-left px-3 py-2 border border-border font-medium">Retention Period</th>
                <th className="text-left px-3 py-2 border border-border font-medium">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {[
                ['Signed contract records', '7 years from last event', 'Commercial document retention standard; limitation periods'],
                ['Audit log entries', '7 years (append-only, never deleted)', 'Legal defensibility; tamper-evidence'],
                ['Electronic signatures', '7 years from signature date', 'ESIGN Act / PIPEDA compliance'],
                ['Evidence files', '7 years from upload (or contract closure)', 'Dispute resolution window'],
                ['User account data', 'Duration of account + 2 years', 'Legal obligation; fraud prevention'],
                ['Authentication logs', '2 years', 'Security monitoring; incident response'],
                ['Billing records', '7 years', 'Tax and accounting requirements'],
                ['Session tokens', '15 minutes (access) / 7 days (refresh)', 'Security best practice'],
                ['Password reset tokens', '1 hour from issuance', 'Security'],
                ['Idempotency keys', '24 hours from issuance', 'Replay protection'],
              ].map(([cat, period, reason]) => (
                <tr key={cat} className="hover:bg-section transition-colors">
                  <td className="px-3 py-2 border border-border font-medium text-primary">{cat}</td>
                  <td className="px-3 py-2 border border-border text-secondary">{period}</td>
                  <td className="px-3 py-2 border border-border text-secondary">{reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>

        <Section title="2. Audit Log Immutability">
          <p>
            Audit log entries are stored in an append-only database table protected by
            PostgreSQL-level rules that prevent UPDATE and DELETE operations on any row.
            Each entry includes a SHA-256 hash chained from the previous entry, forming
            a tamper-evident chain. This design ensures that no party — including {COMPANY}
            administrators — can alter the historical record of events.
          </p>
          <p className="mt-2">
            Because of this immutability requirement, audit logs are <strong>never deleted</strong>,
            even upon account deletion. They are retained for the periods specified above and then
            anonymised by replacing user identifiers with a pseudonymous token.
          </p>
        </Section>

        <Section title="3. Evidence Immutability">
          <p>
            Evidence files cannot be replaced or silently altered after upload. The SHA-256 hash
            of every file is stored at upload time and re-verified on access. A database constraint
            ensures the hash column is always present and non-null.
          </p>
          <p className="mt-2">
            Deletion of evidence requires a formal request that is recorded in the audit log and
            approved by all parties to the associated contract. Even after approval, the metadata
            record (hash, uploader, timestamp) is retained for the full evidence retention period.
          </p>
        </Section>

        <Section title="4. Right to Erasure (PIPEDA / GDPR Equivalents)">
          <p>
            You may request deletion of your personal data by submitting a request in{' '}
            <Link to="/privacy" className="text-accent hover:underline">Privacy &amp; Data Settings</Link>.
            We will process requests within 30 days.
          </p>
          <p className="mt-2">
            Erasure will be applied to all data categories except:
          </p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li>Audit log entries within their mandatory retention window (anonymised instead)</li>
            <li>Signed contract records where another party retains a legal interest</li>
            <li>Data required to fulfil ongoing legal or regulatory obligations</li>
          </ul>
        </Section>

        <Section title="5. Data Storage Location">
          <p>
            All data is stored within the jurisdiction specified in your subscription agreement.
            By default, data is stored in Canada. If your organisation requires data residency
            in a specific jurisdiction, contact{' '}
            <span className="font-medium">privacy@clearclaim.example.com</span>.
          </p>
        </Section>

        <Section title="6. Backup Policy">
          <p>
            Database backups are taken daily and retained on the following schedule:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Daily backups — retained for 7 days</li>
            <li>Weekly backups — retained for 4 weeks</li>
            <li>Monthly backups — retained for 3 months</li>
          </ul>
          <p className="mt-2">
            Backups are encrypted at rest and stored separately from the primary database.
            Backup integrity is verified weekly.
          </p>
        </Section>

        <Section title="7. Contact">
          <p>
            Data protection inquiries:{' '}
            <span className="font-medium">privacy@clearclaim.example.com</span>
          </p>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="text-base font-semibold text-primary mb-2">{title}</h2>
      <div className="text-sm text-secondary leading-relaxed space-y-1">{children}</div>
    </section>
  );
}
