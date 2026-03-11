import { useState, useCallback, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '@/api/projects';
import { evidenceApi, type EvidenceData } from '@/api/evidence';
import { useAuthStore } from '@/stores/authStore';
import { format } from 'date-fns';
import { toast } from 'react-toastify';

type FilterType = 'all' | 'image' | 'video' | 'document' | 'note';

// ── Evidence Viewer Modal ──────────────────────────────────────────────────────

function EvidenceViewer({ ev, onClose, onPrev, onNext, hasPrev, hasNext, projectName, contractName }: {
  ev: EvidenceData;
  onClose: () => void;
  onPrev: () => void;
  onNext: () => void;
  hasPrev: boolean;
  hasNext: boolean;
  projectName?: string;
  contractName?: string;
}) {
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [copied, setCopied] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [touchStartX, setTouchStartX] = useState<number | null>(null);
  const [pinchStartDist, setPinchStartDist] = useState<number | null>(null);
  const [pinchStartZoom, setPinchStartZoom] = useState(1);

  const isImage = (ev.file_type ?? '').startsWith('image/');
  const isVideo = (ev.file_type ?? '').startsWith('video/');
  const isPdf   = (ev.file_type ?? '') === 'application/pdf' || ev.file_url.toLowerCase().endsWith('.pdf');

  const zoomIn  = () => setZoom((z) => Math.min(z + 0.25, 4));
  const zoomOut = () => { setZoom((z) => Math.max(z - 0.25, 0.5)); setOffset({ x: 0, y: 0 }); };
  const reset   = () => { setZoom(1); setOffset({ x: 0, y: 0 }); };

  const onWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    setZoom((z) => Math.min(Math.max(z - e.deltaY * 0.001, 0.5), 4));
  };

  const onMouseDown = (e: React.MouseEvent) => {
    if (zoom <= 1) return;
    setDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };
  const onMouseMove = (e: React.MouseEvent) => {
    if (!dragging) return;
    setOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };
  const onMouseUp = () => setDragging(false);

  const copyLink = () => {
    navigator.clipboard.writeText(ev.file_url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
    if (e.key === 'ArrowLeft'  && hasPrev) onPrev();
    if (e.key === 'ArrowRight' && hasNext) onNext();
    if (e.key === '+' || e.key === '=') zoomIn();
    if (e.key === '-') zoomOut();
    if (e.key === '0') reset();
  }, [hasPrev, hasNext, onClose, onPrev, onNext]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col bg-black/90"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      // eslint-disable-next-line jsx-a11y/no-autofocus
      autoFocus
      aria-modal="true"
      role="dialog"
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-black/60 text-white text-xs shrink-0">
        <div className="flex items-center gap-2">
          <span className="font-medium truncate max-w-xs">{ev.file_url.split('/').pop()}</span>
          <span className="text-white/50">{ev.file_type}</span>
        </div>
        <div className="flex items-center gap-2">
          {isImage && (
            <>
              <button onClick={zoomOut}  className="p-1.5 rounded hover:bg-white/10" title="Zoom out (-)">−</button>
              <span className="w-12 text-center">{Math.round(zoom * 100)}%</span>
              <button onClick={zoomIn}   className="p-1.5 rounded hover:bg-white/10" title="Zoom in (+)">+</button>
              <button onClick={reset}    className="p-1.5 rounded hover:bg-white/10 text-white/60" title="Reset zoom (0)">1:1</button>
            </>
          )}
          <button onClick={() => setShowShare((s) => !s)} className="p-1.5 rounded hover:bg-white/10" title="Share">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </button>
          <button onClick={onClose} className="p-1.5 rounded hover:bg-white/10" title="Close (Esc)">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Share dropdown */}
      {showShare && (
        <div className="absolute top-12 right-4 z-10 w-64 bg-white rounded-lg shadow-xl border border-border p-4 space-y-2">
          <p className="text-xs font-semibold text-primary mb-1">Share Evidence</p>
          <button
            className="w-full text-left text-sm text-secondary hover:text-primary flex items-center gap-2 py-1"
            onClick={copyLink}
          >
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            {copied ? 'Link copied!' : 'Copy secure link'}
          </button>
          <button
            className="w-full text-left text-sm text-secondary hover:text-primary flex items-center gap-2 py-1"
            onClick={() => {
              const meta = JSON.stringify({
                id: ev.id,
                file_url: ev.file_url,
                file_type: ev.file_type,
                file_hash: ev.file_hash,
                added_by: ev.added_by,
                created_at: ev.created_at,
                contract_id: ev.contract_id,
              }, null, 2);
              const blob = new Blob([meta], { type: 'application/json' });
              const a = document.createElement('a');
              a.href = URL.createObjectURL(blob);
              a.download = 'evidence-' + ev.id + '-metadata.json';
              a.click();
              toast.success('Metadata package downloaded.');
              setShowShare(false);
            }}
          >
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export metadata package
          </button>
          <button
            className="w-full text-left text-sm text-secondary hover:text-primary flex items-center gap-2 py-1"
            onClick={() => {
              const subject = encodeURIComponent('Evidence: ' + (ev.file_url.split('/').pop() ?? ev.id));
              const body = encodeURIComponent(
                'Evidence file: ' + ev.file_url + '\n' +
                'Hash: ' + (ev.file_hash ?? 'N/A') + '\n' +
                'Uploaded by: ' + ev.added_by + '\n' +
                'Timestamp: ' + (ev.created_at ? format(new Date(ev.created_at), 'dd MMM yyyy, HH:mm') : 'N/A') + '\n' +
                'Contract: ' + ev.contract_id
              );
              window.open('mailto:?subject=' + subject + '&body=' + body);
              setShowShare(false);
            }}
          >
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Email with metadata
          </button>
        </div>
      )}

      {/* Media area */}
      <div
        className="flex-1 relative overflow-hidden flex items-center justify-center select-none"
        onWheel={onWheel}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        style={{ cursor: zoom > 1 ? (dragging ? 'grabbing' : 'grab') : 'default' }}
        onDoubleClick={() => zoom === 1 ? setZoom(2) : reset()}
        onTouchStart={(e) => {
          if (e.touches.length === 2) {
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            setPinchStartDist(Math.hypot(dx, dy));
            setPinchStartZoom(zoom);
          } else {
            setTouchStartX(e.touches[0].clientX);
          }
        }}
        onTouchMove={(e) => {
          if (e.touches.length === 2 && pinchStartDist !== null) {
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            const dist = Math.hypot(dx, dy);
            setZoom(Math.min(Math.max(pinchStartZoom * (dist / pinchStartDist), 0.5), 4));
          }
        }}
        onTouchEnd={(e) => {
          if (e.touches.length < 2) setPinchStartDist(null);
          if (touchStartX === null) return;
          const delta = e.changedTouches[0].clientX - touchStartX;
          if (delta > 50 && hasPrev) onPrev();
          else if (delta < -50 && hasNext) onNext();
          setTouchStartX(null);
        }}
      >
        {isImage && (
          <img
            src={ev.file_url}
            alt={ev.file_url.split('/').pop()}
            draggable={false}
            style={{ transform: `scale(${zoom}) translate(${offset.x / zoom}px, ${offset.y / zoom}px)`, transition: dragging ? 'none' : 'transform 0.1s' }}
            className="max-w-full max-h-full object-contain"
          />
        )}
        {isVideo && (
          <video
            src={ev.file_url}
            controls
            className="max-w-full max-h-full"
          >
            <track kind="captions" />
          </video>
        )}
        {!isImage && !isVideo && isPdf && (
          <iframe
            src={ev.file_url}
            title="PDF viewer"
            className="w-full h-full border-0"
          />
        )}
        {!isImage && !isVideo && !isPdf && (
          <div className="text-white/60 text-sm text-center">
            <svg className="w-12 h-12 mx-auto mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>{ev.file_url.split('/').pop()}</p>
            <a href={ev.file_url} target="_blank" rel="noopener noreferrer" className="text-accent underline text-xs mt-2 inline-block">Open file externally</a>
          </div>
        )}
      </div>

      {/* Navigation */}
      {hasPrev && (
        <button
          onClick={onPrev}
          className="absolute left-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 text-white hover:bg-black/70"
          aria-label="Previous evidence"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}
      {hasNext && (
        <button
          onClick={onNext}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 text-white hover:bg-black/70"
          aria-label="Next evidence"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      )}

      {/* Metadata bar */}
      <div className="shrink-0 bg-black/70 text-white/70 text-xs px-4 py-2 flex flex-wrap gap-4">
        <span><span className="text-white/40">Uploader:</span> {ev.added_by}</span>
        <span><span className="text-white/40">Timestamp:</span> {ev.created_at ? format(new Date(ev.created_at), 'dd MMM yyyy, HH:mm') : '—'}</span>
        {ev.file_hash && <span><span className="text-white/40">Hash:</span> <span className="font-mono">{ev.file_hash.slice(0, 24)}…</span></span>}
        {ev.file_size && <span><span className="text-white/40">Size:</span> {(ev.file_size / 1024).toFixed(1)} KB</span>}
        {projectName && <span><span className="text-white/40">Project:</span> {projectName}</span>}
        {contractName
          ? <span><span className="text-white/40">Contract:</span> {contractName}</span>
          : <span><span className="text-white/40">Contract:</span> <span className="font-mono">{ev.contract_id.slice(0, 16)}…</span></span>}
        <span className="text-white/40 ml-auto">← → navigate · swipe · pinch/scroll/+− zoom · 0 reset · Esc close</span>
      </div>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────────

export default function EvidencePage() {
  const { session } = useAuthStore();
  const [search,         setSearch]         = useState('');
  const [typeFilter,     setTypeFilter]     = useState<FilterType>('all');
  const [dateFrom,       setDateFrom]       = useState('');
  const [dateTo,         setDateTo]         = useState('');
  const [projectFilter,  setProjectFilter]  = useState('');
  const [contractFilter, setContractFilter] = useState('');
  const [viewerIdx,      setViewerIdx]      = useState<number | null>(null);
  const [selected,       setSelected]       = useState<Set<string>>(new Set());

  const toggleSelect = (id: string) => setSelected((s) => {
    const next = new Set(s);
    if (next.has(id)) next.delete(id); else next.add(id);
    return next;
  });

  const selectAll = (items: EvidenceData[]) =>
    setSelected(new Set(items.map((e) => e.id)));

  const clearSelection = () => setSelected(new Set());

  const exportPackage = (items: EvidenceData[]) => {
    const pkg = {
      exported_at: new Date().toISOString(),
      item_count: items.length,
      items: items.map((ev) => ({
        id: ev.id,
        file_url: ev.file_url,
        file_type: ev.file_type,
        file_size: ev.file_size,
        file_hash: ev.file_hash,
        added_by: ev.added_by,
        created_at: ev.created_at,
        contract_id: ev.contract_id,
        status: ev.status,
      })),
    };
    const blob = new Blob([JSON.stringify(pkg, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'clearclaim-evidence-package-' + Date.now() + '.json';
    a.click();
    toast.success(items.length + ' item' + (items.length !== 1 ? 's' : '') + ' exported.');
    clearSelection();
  };

  const { data: projects = [] } = useQuery({
    queryKey: ['user-projects', session?.user_id],
    queryFn: () => projectsApi.getUserProjects(session!.user_id),
    enabled: !!session?.user_id,
  });

  const { data: contracts = [] } = useQuery({
    queryKey: ['all-contracts', projects.map((p) => p.id)],
    queryFn: async () => {
      const all = await Promise.all(projects.map((p) => projectsApi.getProjectContracts(p.id)));
      return all.flat();
    },
    enabled: projects.length > 0,
  });

  const { data: allEvidence = [], isLoading } = useQuery({
    queryKey: ['all-evidence', contracts.map((c) => c.id)],
    queryFn: async () => {
      const all = await Promise.all(contracts.map((c) => evidenceApi.getContractEvidence(c.id)));
      return all.flat();
    },
    enabled: contracts.length > 0,
  });

  const FILE_TYPE_MAP: Record<FilterType, string[]> = {
    all:      [],
    image:    ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    video:    ['video/mp4', 'video/webm'],
    document: ['application/pdf', 'text/plain', 'application/msword'],
    note:     ['text/plain', 'text/markdown'],
  };

  const filtered = allEvidence.filter((ev: EvidenceData) => {
    const matchesType =
      typeFilter === 'all' ||
      FILE_TYPE_MAP[typeFilter].some((t) => (ev.file_type ?? '').startsWith(t.split('/')[0]));
    const searchLower = search.toLowerCase();
    const matchesSearch =
      !searchLower ||
      ev.added_by.toLowerCase().includes(searchLower) ||
      ev.file_url.toLowerCase().includes(searchLower) ||
      (ev.file_type ?? '').toLowerCase().includes(searchLower);
    const evDate = ev.created_at ? new Date(ev.created_at) : null;
    const matchesDateFrom = !dateFrom || (evDate !== null && evDate >= new Date(dateFrom));
    const matchesDateTo   = !dateTo   || (evDate !== null && evDate <= new Date(dateTo + 'T23:59:59'));
    const contract = (contracts as { id: string; project_id: string }[]).find((c) => c.id === ev.contract_id);
    const matchesProject  = !projectFilter  || contract?.project_id === projectFilter;
    const matchesContract = !contractFilter || ev.contract_id === contractFilter;
    return matchesType && matchesSearch && matchesDateFrom && matchesDateTo && matchesProject && matchesContract;
  });

  const typeLabels: { id: FilterType; label: string }[] = [
    { id: 'all',      label: 'All'       },
    { id: 'image',    label: 'Photos'    },
    { id: 'video',    label: 'Videos'    },
    { id: 'document', label: 'Documents' },
    { id: 'note',     label: 'Notes'     },
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Evidence Library</h1>
        <p className="page-subtitle">
          All evidence across your projects &mdash; timestamped, hashed, and immutable.
        </p>
      </div>

      <div className="px-6 pb-10 space-y-4">
        <div className="flex flex-wrap gap-3 items-center">
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="form-input max-w-xs"
            placeholder="Search by uploader, file name, type..."
          />
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="form-input w-36"
            title="Date from"
          />
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="form-input w-36"
            title="Date to"
          />
          <select
            value={projectFilter}
            onChange={(e) => { setProjectFilter(e.target.value); setContractFilter(''); }}
            className="form-input max-w-[180px]"
          >
            <option value="">All projects</option>
            {(projects as { id: string; name: string }[]).map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <select
            value={contractFilter}
            onChange={(e) => setContractFilter(e.target.value)}
            className="form-input max-w-[180px]"
          >
            <option value="">All contracts</option>
            {(contracts as { id: string; project_id: string; name?: string }[])
              .filter((c) => !projectFilter || c.project_id === projectFilter)
              .map((c) => (
                <option key={c.id} value={c.id}>{c.name || c.id.slice(0, 12) + '…'}</option>
              ))}
          </select>
          <div className="flex gap-1">
            {typeLabels.map((t) => (
              <button
                key={t.id}
                onClick={() => setTypeFilter(t.id)}
                className={"px-3 py-1.5 rounded text-xs font-medium border transition-colors " + (typeFilter === t.id ? "bg-accent text-white border-accent" : "bg-card text-secondary border-border hover:bg-section")}
              >
                {t.label}
              </button>
            ))}
          </div>
          {filtered.length > 0 && (
            <button
              onClick={() => selected.size === filtered.length ? clearSelection() : selectAll(filtered)}
              className="px-3 py-1.5 rounded text-xs font-medium border border-border bg-card text-secondary hover:bg-section transition-colors"
            >
              {selected.size === filtered.length ? 'Deselect All' : 'Select All'}
            </button>
          )}
        </div>

        {/* Bulk action bar */}
        {selected.size > 0 && (
          <div className="flex items-center gap-3 px-4 py-2.5 bg-accent/10 border border-accent/30 rounded-lg text-sm">
            <span className="text-accent font-medium">{selected.size} item{selected.size !== 1 ? 's' : ''} selected</span>
            <button
              className="ml-auto px-3 py-1 rounded bg-accent text-white text-xs font-medium hover:bg-accent-hover"
              onClick={() => {
                const items = filtered.filter((ev: EvidenceData) => selected.has(ev.id));
                exportPackage(items);
              }}
            >
              Export Package
            </button>
            <button
              className="text-xs text-secondary hover:text-primary"
              onClick={clearSelection}
            >
              Cancel
            </button>
          </div>
        )}

        {isLoading && <p className="text-sm text-meta py-6">Loading evidence...</p>}

        {!isLoading && allEvidence.length === 0 && (
          <div className="card p-10 text-center">
            <p className="text-sm text-secondary">No evidence uploaded yet.</p>
            <p className="text-xs text-meta mt-1">Open a project and navigate to the Evidence tab to start uploading.</p>
          </div>
        )}

        {!isLoading && allEvidence.length > 0 && filtered.length === 0 && (
          <p className="text-sm text-secondary py-4">No evidence matches your search or filter.</p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((ev: EvidenceData, idx) => (
            <div
              key={ev.id}
              className={"card cursor-pointer transition-colors " + (selected.has(ev.id) ? "border-accent ring-1 ring-accent" : "hover:border-accent")}
              onClick={() => { if (selected.size > 0) { toggleSelect(ev.id); } else { setViewerIdx(idx); } }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && (selected.size > 0 ? toggleSelect(ev.id) : setViewerIdx(idx))}
              aria-label={"View evidence: " + (ev.file_url.split('/').pop() ?? ev.id)}
              aria-pressed={selected.has(ev.id)}
            >
              <div className="card-header py-3 flex items-center gap-2">
                <button
                  className={"w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors mr-1 " + (selected.has(ev.id) ? "bg-accent border-accent" : "border-border hover:border-accent")}
                  onClick={(e) => { e.stopPropagation(); toggleSelect(ev.id); }}
                  aria-label={(selected.has(ev.id) ? 'Deselect' : 'Select') + ' evidence'}
                  title={(selected.has(ev.id) ? 'Deselect' : 'Select') + ' for export'}
                >
                  {selected.has(ev.id) && (
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
                <div className="w-7 h-7 rounded bg-accent-light flex items-center justify-center shrink-0">
                  <FileIcon type={ev.file_type} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-primary truncate">{ev.file_url.split('/').pop() ?? ev.id}</p>
                  <p className="text-xs text-meta truncate">{ev.file_type || 'Unknown type'}</p>
                </div>
                <span className={"text-xs px-1.5 py-0.5 rounded font-medium shrink-0 " + (ev.status === 'active' ? "bg-green-50 text-confirmed" : "bg-yellow-50 text-pending")}>
                  {ev.status}
                </span>
              </div>
              <div className="card-body space-y-1.5 text-xs text-secondary">
                <p><span className="text-meta">Uploaded by:</span> <span className="font-mono text-primary">{ev.added_by}</span></p>
                <p><span className="text-meta">Timestamp:</span> {ev.created_at ? format(new Date(ev.created_at), 'dd MMM yyyy, HH:mm') : '—'}</p>
                {ev.file_size && <p><span className="text-meta">Size:</span> {(ev.file_size / 1024).toFixed(1)} KB</p>}
                {ev.file_hash && <p className="truncate"><span className="text-meta">Hash:</span> <span className="font-mono">{ev.file_hash.slice(0, 20)}...</span></p>}
                <p className="truncate"><span className="text-meta">Contract:</span> <span className="font-mono">{ev.contract_id.slice(0, 16)}...</span></p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Evidence Viewer Modal */}
      {viewerIdx !== null && filtered[viewerIdx] && (
        <EvidenceViewer
          ev={filtered[viewerIdx]}
          onClose={() => setViewerIdx(null)}
          onPrev={() => setViewerIdx((i) => (i !== null && i > 0 ? i - 1 : i))}
          onNext={() => setViewerIdx((i) => (i !== null && i < filtered.length - 1 ? i + 1 : i))}
          hasPrev={viewerIdx > 0}
          hasNext={viewerIdx < filtered.length - 1}
          projectName={
            (projects as { id: string; name: string }[]).find(
              (p) => p.id === (contracts as { id: string; project_id: string }[]).find(
                (c) => c.id === filtered[viewerIdx].contract_id
              )?.project_id
            )?.name
          }
          contractName={
            (contracts as { id: string; name?: string }[]).find(
              (c) => c.id === filtered[viewerIdx].contract_id
            )?.name
          }
        />
      )}
    </div>
  );
}

function FileIcon({ type }: { type?: string }) {
  const t = type ?? '';
  if (t.startsWith('image/')) {
    return (
      <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    );
  }
  if (t.startsWith('video/')) {
    return (
      <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.277A1 1 0 0121 8.677V15.32a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
    );
  }
  return (
    <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}
