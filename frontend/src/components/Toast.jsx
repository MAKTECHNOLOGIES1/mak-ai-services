import React from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';
import './Toast.css';

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  const typeClass = toast.type === 'error' ? 'toast-error' : toast.type === 'info' ? 'toast-info' : 'toast-success';

  return (
    <div className={`mak-toast-container ${typeClass}`}>
      {toast.type === 'error' ? <AlertCircle size={18} /> : toast.type === 'info' ? <Info size={18} /> : <CheckCircle2 size={18} />}
      <span>{toast.message}</span>
      {onClose && (
        <button
          onClick={onClose}
          className="mak-toast-close"
          title="Dismiss"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}
