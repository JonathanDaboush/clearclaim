import { Link } from 'react-router-dom';

const EFFECTIVE_DATE = 'March 13, 2026';
const COMPANY = 'ClearClaim';

export default function ESignatureDisclosurePage() {
  return (
    <div>
      <div className="page-header">
        <nav className="flex items-center gap-1 text-xs text-meta mb-2">
          <Link to="/dashboard" className="hover:text-accent">Dashboard</Link>
          <span className="mx-1">›</span>
          <span className="text-primary">Electronic Signature Disclosure</span>
        </nav>
        <h1 className="page-title">Electronic Signature &amp; Consent Disclosure</h1>
        <p className="page-subtitle">Effective {EFFECTIVE_DATE} — required reading before your first signature</p>
      </div>

      <div className="px-6 pb-12 max-w-3xl space-y-8">
        <div className="legal-notice text-xs">
          Under the <em>Electronic Signatures in Global and National Commerce Act</em> (ESIGN Act,
          15 U.S.C. § 7001) and applicable Canadian electronic commerce legislation, we are required
          to obtain your affirmative consent before providing records electronically and before your
          electronic signature is treated as legally binding.
        </div>

        <Section title="1. Scope of This Disclosure">
          <p>
            This disclosure applies to all agreements, contracts, notices, and communications that
            {' '}{COMPANY} provides or facilitates electronically, including contracts you sign through
            the platform.
          </p>
        </Section>

        <Section title="2. Your Consent">
          <p>
            By checking the consent acknowledgement on the signing screen and completing the
            signing flow (authentication code + confirmation), you:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>
              Consent to conduct this transaction electronically and to receive all related
              records electronically.
            </li>
            <li>
              Confirm that your electronic signature has the same legal effect as a handwritten
              signature under applicable law.
            </li>
            <li>
              Represent that you have reviewed the full text of the document before signing.
            </li>
          </ul>
        </Section>

        <Section title="3. Hardware and Software Requirements">
          <p>
            To access and retain electronic records you will need:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>A modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)</li>
            <li>A stable internet connection</li>
            <li>An email address to receive system notifications</li>
            <li>A TOTP-compatible authenticator application (e.g. Google Authenticator, Authy)</li>
          </ul>
        </Section>

        <Section title="4. How Your Signature Is Recorded">
          <p>
            When you sign a contract on {COMPANY}, the system records:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Your user identity (email address and user ID)</li>
            <li>The exact UTC timestamp of the signature event</li>
            <li>The registered device from which you signed</li>
            <li>The IP address of your connection at the time of signing</li>
            <li>A SHA-256 hash of the contract version you signed, binding your signature irrevocably to that exact document content</li>
            <li>Confirmation that your TOTP authentication code was successfully verified</li>
          </ul>
          <p className="mt-2">
            These records are stored in an append-only, cryptographically chained audit log that
            cannot be altered retroactively.
          </p>
        </Section>

        <Section title="5. Withdrawing Consent">
          <p>
            You may withdraw consent to electronic transactions at any time by contacting
            {' '}{COMPANY} at <span className="font-medium">legal@clearclaim.example.com</span>.
            Withdrawal of consent does not affect the validity of electronic signatures you
            have already provided.
          </p>
          <p className="mt-2">
            After withdrawing consent you will not be able to sign new agreements through the
            platform and may request paper copies of your records.
          </p>
        </Section>

        <Section title="6. Paper Copies">
          <p>
            You have the right to request a paper copy of any electronically signed record. To
            request paper copies, contact us at{' '}
            <span className="font-medium">legal@clearclaim.example.com</span>. A reasonable
            administrative fee may apply.
          </p>
        </Section>

        <Section title="7. Updating Your Contact Information">
          <p>
            It is your responsibility to keep your registered email address current. Update your
            contact information in{' '}
            <Link to="/account" className="text-accent hover:underline">Account Settings</Link>.
          </p>
        </Section>

        <Section title="8. Legal Basis">
          <p>
            This disclosure and the electronic signature process are designed to comply with:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>U.S. ESIGN Act (15 U.S.C. § 7001 <em>et seq.</em>)</li>
            <li>U.S. Uniform Electronic Transactions Act (UETA)</li>
            <li>Canada: <em>Electronic Commerce Act</em>, S.C. 1998, c. 5</li>
            <li>Canada: Ontario <em>Electronic Commerce Act, 2000</em>, S.O. 2000, c. 17</li>
            <li>Canada: <em>Personal Information Protection and Electronic Documents Act</em> (PIPEDA)</li>
          </ul>
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
