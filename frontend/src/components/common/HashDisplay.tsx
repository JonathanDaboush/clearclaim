/** Displays a cryptographic hash in a copy-friendly, visually truncated format. */
interface Props {
  hash: string;
  label?: string;
}

export function HashDisplay({ hash, label }: Props) {
  const copy = () => navigator.clipboard.writeText(hash);

  return (
    <div>
      {label && <p className="text-xs text-slate-500 mb-1 font-medium uppercase tracking-wide">{label}</p>}
      <div className="flex items-center gap-2">
        <span className="record-box flex-1 truncate">
          {hash}
        </span>
        <button
          onClick={copy}
          title="Copy full hash"
          className="btn-ghost p-1.5 rounded text-meta hover:text-accent"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
