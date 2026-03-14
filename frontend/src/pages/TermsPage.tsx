import { Link } from 'react-router-dom';

const EFFECTIVE_DATE = 'March 13, 2026';
const COMPANY = 'ClearClaim';

export default function TermsPage() {
  return (
    <div>
      <div className="page-header">
        <nav className="flex items-center gap-1 text-xs text-meta mb-2">
          <Link to="/dashboard" className="hover:text-accent">Dashboard</Link>
          <span className="mx-1">›</span>
          <span className="text-primary">Terms of Service</span>
        </nav>
        <h1 className="page-title">Terms of Service</h1>
        <p className="page-subtitle">Effective {EFFECTIVE_DATE}</p>
      </div>

      <div className="px-6 pb-12 max-w-3xl space-y-8">
        <div className="legal-notice text-xs">
          Please read these Terms carefully. By creating an account or using {COMPANY} you agree to
          be bound by these Terms. If you do not agree, do not use the service.
        </div>

        <Section title="1. Service Description">
          <p>
            {COMPANY} provides a digital platform for creating, managing, and signing agreements
            between parties, and for uploading and preserving evidence associated with those
            agreements. The platform creates chronological, cryptographically chained records of
            all events.
          </p>
        </Section>

        <Section title="2. Eligibility">
          <p>
            You must be at least 18 years old and have the legal capacity to enter into binding
            agreements under applicable law. By using {COMPANY} you represent and warrant that you
            meet these requirements.
          </p>
        </Section>

        <Section title="3. Electronic Signatures">
          <p>
            Signatures created through {COMPANY} are intended to constitute legally binding
            electronic signatures under:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>
              The <em>Electronic Signatures in Global and National Commerce Act</em> (ESIGN Act),
              15 U.S.C. § 7001 <em>et seq.</em> (United States)
            </li>
            <li>
              The <em>Uniform Electronic Transactions Act</em> (UETA), as enacted in applicable
              U.S. states
            </li>
            <li>
              The <em>Electronic Commerce Act</em>, S.C. 1998, c. 5 (Canada, federal)
            </li>
            <li>
              Applicable provincial electronic commerce legislation, including Ontario's
              <em> Electronic Commerce Act, 2000</em>
            </li>
          </ul>
          <p className="mt-2">
            You acknowledge that your use of the platform to sign a document constitutes
            your intent to be legally bound by that document.
          </p>
        </Section>

        <Section title="4. Identity Verification">
          <p>
            Optional identity verification is provided through a third-party provider. Verified
            status increases the legal assurance of signatures but is not required to use the
            platform. {COMPANY} does not store government-issued identity documents.
          </p>
        </Section>

        <Section title="5. Evidence Upload">
          <p>
            Evidence submitted through the platform is timestamped, hashed, and recorded in an
            append-only audit log. You represent that you have the right to upload any evidence
            you submit and that it does not violate any third-party rights or applicable law.
          </p>
          <p className="mt-2">
            Evidence cannot be replaced or altered after upload. Deletion requests are recorded
            formally and require approval from all project parties in accordance with the platform's
            data retention policy.
          </p>
        </Section>

        <Section title="6. User Responsibilities">
          <ul className="list-disc list-inside space-y-1">
            <li>Maintain the confidentiality of your authenticator credential and password.</li>
            <li>Notify {COMPANY} immediately of any unauthorized access to your account.</li>
            <li>Do not upload unlawful content, malware, or material that infringes third-party rights.</li>
            <li>Ensure the devices you register belong to you or are under your lawful control.</li>
          </ul>
        </Section>

        <Section title="7. Acceptable Use">
          <p>
            You may not use {COMPANY} to create fraudulent agreements, suppress evidence, coerce
            signatures, or for any purpose that violates applicable law or the rights of others.
            {COMPANY} reserves the right to suspend or terminate accounts involved in such activity.
          </p>
        </Section>

        <Section title="8. Data Retention">
          <p>
            Audit logs and signed contract records are retained for a minimum of seven (7) years
            from the date of the last event on a contract, in accordance with standard commercial
            documentation retention guidelines. See our{' '}
            <Link to="/legal/data-retention" className="text-accent hover:underline">
              Data Retention Policy
            </Link>{' '}
            for full details.
          </p>
        </Section>

        <Section title="9. Limitation of Liability">
          <p>
            To the fullest extent permitted by applicable law, {COMPANY} is not liable for any
            indirect, incidental, special, consequential, or punitive damages arising from your use
            of the service, including but not limited to the enforceability of any agreement you
            create on the platform. {COMPANY} strongly recommends consulting qualified legal counsel
            before executing legally significant agreements.
          </p>
        </Section>

        <Section title="10. Governing Law">
          <p>
            These Terms are governed by the laws of the Province of Ontario, Canada, without regard
            to conflict of law principles. You consent to the exclusive jurisdiction of the courts
            of Ontario for any dispute arising from these Terms or your use of {COMPANY}.
          </p>
        </Section>

        <Section title="11. Changes to These Terms">
          <p>
            {COMPANY} may update these Terms from time to time. Material changes will be communicated
            by in-app notification at least 30 days before the effective date. Continued use of the
            service after the effective date constitutes acceptance of the revised Terms.
          </p>
        </Section>

        <Section title="12. Contact">
          <p>
            Legal inquiries: <span className="font-medium">legal@clearclaim.example.com</span>
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
