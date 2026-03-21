import { useState } from 'react';
import { motion } from 'framer-motion';
import { COMPLAINTS } from '../../data/mockData';
import { AlertCircle, CheckCircle, Clock, Send, ChevronDown } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const statusCfg = { Open: 'badge-blue', 'In Progress': 'badge-gold', Resolved: 'badge-green', Closed: 'badge-gray' };

export default function ComplaintsPage() {
  const [complaints, setComplaints] = useState(COMPLAINTS);
  const [filter, setFilter] = useState('All');
  const [selected, setSelected] = useState(null);
  const [response, setResponse] = useState('');

  const filtered = complaints.filter(c => filter === 'All' || c.status === filter);

  const updateStatus = (id, status) => setComplaints(complaints.map(c => c.id === id ? { ...c, status } : c));

  const sendResponse = (id) => {
    if (!response.trim()) return;
    setComplaints(complaints.map(c => c.id === id ? { ...c, adminResponse: response, status: 'In Progress' } : c));
    setResponse('');
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}><h1 className="page-title">Complaint Resolution</h1><p className="page-subtitle">Review and resolve student complaints</p></motion.div>

      <motion.div variants={item} className="flex gap-2 flex-wrap">
        {['All', 'Open', 'In Progress', 'Resolved'].map(s => (
          <button key={s} onClick={() => setFilter(s)} className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${filter === s ? 'bg-brand-500 text-white' : 'bg-gray-100 dark:bg-dark-surface text-gray-600 dark:text-gray-400'}`}>
            {s} {s !== 'All' && `(${complaints.filter(c => c.status === s).length})`}
          </button>
        ))}
      </motion.div>

      <div className="grid lg:grid-cols-5 gap-6">
        {/* List */}
        <motion.div variants={container} className="lg:col-span-2 space-y-3">
          {filtered.map(c => (
            <motion.div key={c.id} variants={item} onClick={() => setSelected(c)} className={`glass-card p-4 cursor-pointer transition-all ${selected?.id === c.id ? 'ring-2 ring-brand-500' : 'hover:shadow-card-hover'}`}>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white flex-1 truncate">{c.title}</h3>
                <span className={statusCfg[c.status]}>{c.status}</span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{c.description}</p>
              <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                <span>{c.userName}</span>
                <span className={c.priority === 'High' ? 'badge-red' : 'badge-gray'}>{c.priority}</span>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Detail Panel */}
        <motion.div variants={item} className="lg:col-span-3 glass-card p-6">
          {selected ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white mb-1">{selected.title}</h2>
                <div className="flex items-center gap-2">
                  <span className={statusCfg[selected.status]}>{selected.status}</span>
                  <span className={selected.priority === 'High' ? 'badge-red' : 'badge-gray'}>{selected.priority}</span>
                  <span className="badge-purple">{selected.category}</span>
                </div>
              </div>
              <div><p className="text-sm text-gray-700 dark:text-gray-300">{selected.description}</p>
                <p className="text-xs text-gray-400 mt-2">Submitted by {selected.userName} on {new Date(selected.createdAt).toLocaleDateString()}</p>
              </div>
              {selected.adminResponse && (
                <div className="p-3 bg-emerald-50 dark:bg-emerald-900/10 rounded-xl border border-emerald-200 dark:border-emerald-800/30">
                  <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 mb-1">Your Response</p>
                  <p className="text-sm text-emerald-600 dark:text-emerald-300">{selected.adminResponse}</p>
                </div>
              )}
              <div className="border-t border-gray-100 dark:border-dark-border/50 pt-4">
                <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">Update Status</p>
                <div className="flex gap-2 mb-4">
                  {['Open', 'In Progress', 'Resolved'].map(s => (
                    <button key={s} onClick={() => updateStatus(selected.id, s)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${selected.status === s ? 'bg-brand-500 text-white' : 'bg-gray-100 dark:bg-dark-surface text-gray-600 dark:text-gray-400'}`}>{s}</button>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input type="text" value={response} onChange={e => setResponse(e.target.value)} placeholder="Type admin response..." className="input-field flex-1" />
                  <button onClick={() => sendResponse(selected.id)} className="btn-primary flex items-center gap-1"><Send className="w-4 h-4" /> Send</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-center">
              <div><AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" /><p className="text-gray-500">Select a complaint to view details</p></div>
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}
