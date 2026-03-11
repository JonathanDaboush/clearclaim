import { clsx } from 'clsx';

type Status =
  | 'draft' | 'under_review' | 'approved' | 'active' | 'disputed' | 'terminated'
  | 'pending_approval' | 'deletion_requested' | 'deleted'
  | 'verified' | 'unverified' | 'pending' | 'failed'
  | 'worker_manager' | 'worker' | 'legal_rep' | 'client' | 'guest'
  | string;

const statusMap: Record<string, { label: string; className: string }> = {
  draft:             { label: 'Draft',              className: 'badge-neutral'   },
  under_review:      { label: 'Under Review',       className: 'badge-pending'   },
  approved:          { label: 'Approved',           className: 'badge-confirmed' },
  active:            { label: 'Active',             className: 'badge-confirmed' },
  disputed:          { label: 'Disputed',           className: 'badge-disputed'  },
  terminated:        { label: 'Terminated',         className: 'badge-neutral'   },
  pending_approval:  { label: 'Pending Approval',   className: 'badge-pending'   },
  deletion_requested:{ label: 'Deletion Requested', className: 'badge-disputed'  },
  deleted:           { label: 'Deleted',            className: 'badge-neutral'   },
  verified:          { label: 'Verified',           className: 'badge-confirmed' },
  unverified:        { label: 'Unverified',         className: 'badge-neutral'   },
  pending:           { label: 'Pending',            className: 'badge-pending'   },
  failed:            { label: 'Failed',             className: 'badge-disputed'  },
  worker_manager:    { label: 'Worker Manager',     className: 'badge-info'      },
  worker:            { label: 'Worker',             className: 'badge-info'      },
  legal_rep:         { label: 'Legal Rep',          className: 'badge-info'      },
  client:            { label: 'Client',             className: 'badge-neutral'   },
  guest:             { label: 'Guest',              className: 'badge-neutral'   },
};

interface Props {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: Props) {
  const entry = statusMap[status] ?? { label: status, className: 'badge-neutral' };
  return (
    <span className={clsx(entry.className, className)}>
      {entry.label}
    </span>
  );
}
