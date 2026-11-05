import React, { useState, useEffect } from 'react'
import {
  Inbox,
  MessageSquare,
  CheckCircle2,
  AlertTriangle,
  Clock,
  RefreshCw,
  Search,
  BookOpen,
  Sliders,
  Mail,
  ShieldCheck,
  Send,
  User,
  Bot,
  ExternalLink,
  ChevronRight,
  X,
  Database,
  Sparkles,
  Save,
  Check
} from 'lucide-react'

interface Stats {
  total_events: number
  total_tickets: number
  open_tickets: number
  escalated_tickets: number
  closed_tickets: number
}

interface EventItem {
  id: string
  gmail_message_id: string
  thread_id: string
  status: string
  error: string | null
  created_at: string
}

interface TicketItem {
  id: string
  thread_id: string
  customer_email: string
  subject: string
  status: string
  category: string
  created_at: string
  updated_at: string
}

interface MessageItem {
  id: string
  direction: 'inbound' | 'outbound'
  sender: string
  recipient: string
  body: string
  created_at: string
}

interface KBArticle {
  id: string
  slug: string
  title: string
  content?: string
  updated_at: string
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'tickets' | 'events' | 'kb' | 'system'>('tickets')
  const [stats, setStats] = useState<Stats | null>(null)
  const [tickets, setTickets] = useState<TicketItem[]>([])
  const [events, setEvents] = useState<EventItem[]>([])
  const [kbList, setKbList] = useState<KBArticle[]>([])
  const [selectedKB, setSelectedKB] = useState<KBArticle | null>(null)
  const [kbContent, setKbContent] = useState<string>('')
  const [kbSaving, setKbSaving] = useState(false)
  const [isPolling, setIsPolling] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [saveSuccess, setSaveSuccess] = useState(false)

  // Selected Ticket for Modal View
  const [activeTicket, setActiveTicket] = useState<TicketItem | null>(null)
  const [ticketMessages, setTicketMessages] = useState<MessageItem[]>([])
  const [loadingThread, setLoadingThread] = useState(false)

  const fetchData = async () => {
    try {
      const [resStats, resTickets, resEvents, resKB] = await Promise.all([
        fetch('/api/stats').then(r => r.json()),
        fetch('/api/tickets').then(r => r.json()),
        fetch('/api/events').then(r => r.json()),
        fetch('/api/kb').then(r => r.json())
      ])
      setStats(resStats)
      setTickets(resTickets || [])
      setEvents(resEvents || [])
      setKbList(resKB || [])
      if (resKB && resKB.length > 0 && !selectedKB) {
        loadKBArticle(resKB[0].slug)
      }
    } catch (err) {
      console.error('Failed to fetch data:', err)
    }
  }

  useEffect(() => {
    fetchData()
    const timer = setInterval(fetchData, 8000)
    return () => clearInterval(timer)
  }, [])

  const triggerPollNow = async () => {
    setIsPolling(true)
    try {
      await fetch('/api/poll-now', { method: 'POST' })
      setTimeout(() => {
        fetchData()
        setIsPolling(false)
      }, 3000)
    } catch (err) {
      setIsPolling(false)
    }
  }

  const openTicketThread = async (ticket: TicketItem) => {
    setActiveTicket(ticket)
    setLoadingThread(true)
    try {
      const res = await fetch(`/api/tickets/${ticket.id}`).then(r => r.json())
      setTicketMessages(res.messages || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingThread(false)
    }
  }

  const updateTicketStatus = async (ticketId: string, newStatus: string) => {
    try {
      await fetch(`/api/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      })
      if (activeTicket && activeTicket.id === ticketId) {
        setActiveTicket({ ...activeTicket, status: newStatus })
      }
      fetchData()
    } catch (err) {
      console.error(err)
    }
  }

  const loadKBArticle = async (slug: string) => {
    try {
      const res = await fetch(`/api/kb/${slug}`).then(r => r.json())
      const article = kbList.find(k => k.slug === slug)
      if (article) {
        setSelectedKB(article)
        setKbContent(res.content)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const saveKBArticle = async () => {
    if (!selectedKB) return
    setKbSaving(true)
    try {
      await fetch(`/api/kb/${selectedKB.slug}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: selectedKB.title, content: kbContent })
      })
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err) {
      alert('Failed to save knowledge base article.')
    } finally {
      setKbSaving(false)
    }
  }

  const filteredTickets = tickets.filter(t => {
    const matchesStatus = statusFilter === 'all' || t.status === statusFilter
    const matchesSearch =
      t.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.customer_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.category.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesStatus && matchesSearch
  })

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex font-['Plus_Jakarta_Sans',sans-serif] selection:bg-cyan-500/20 selection:text-cyan-200">
      {/* SIDEBAR NAVIGATION (LTR) */}
      <aside className="w-64 border-r border-slate-800/80 bg-[#0c101a] flex flex-col justify-between shrink-0">
        <div>
          {/* Brand Header */}
          <div className="p-6 border-b border-slate-800/60 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-base tracking-tight text-white flex items-center gap-2">
                CloudScale AI
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                  v2.0
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Autonomous Support Platform</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1.5">
            <button
              onClick={() => setActiveTab('tickets')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                activeTab === 'tickets'
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <MessageSquare className="w-4 h-4" />
                <span>Tickets & Conversations</span>
              </div>
              {tickets.length > 0 && (
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                  {tickets.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('events')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                activeTab === 'events'
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <Inbox className="w-4 h-4" />
                <span>Event Stream & Audit</span>
              </div>
              {events.length > 0 && (
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                  {events.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('kb')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                activeTab === 'kb'
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <BookOpen className="w-4 h-4" />
                <span>AI Knowledge Base</span>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
                {kbList.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('system')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                activeTab === 'system'
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4" />
                <span>System Architecture</span>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            </button>
          </nav>
        </div>

        {/* Poller Monitor Status */}
        <div className="p-4 border-t border-slate-800/60 bg-[#090d16]">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-slate-400 flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]"></span>
              Gmail Poller Active
            </span>
            <span className="text-slate-500 font-mono text-[11px]">Interval: 30s</span>
          </div>
          <div className="text-[11px] text-slate-400 truncate bg-slate-900/80 px-2 py-1.5 rounded border border-slate-800 font-mono" title="support@cloudscale.ai">
            📬 support@cloudscale.ai
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800/80 px-8 flex items-center justify-between bg-[#090d16]/80 backdrop-blur sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-base font-bold text-white tracking-tight">
              {activeTab === 'tickets' && 'Customer Inquiries & Autonomous Triage'}
              {activeTab === 'events' && 'Raw Inbound Message Pipeline & Defensive Filters'}
              {activeTab === 'kb' && 'Grounded Knowledge Base & SLA Documentation'}
              {activeTab === 'system' && 'Infrastructure Topology & API Health'}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={triggerPollNow}
              disabled={isPolling}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-cyan-600/20 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isPolling ? 'animate-spin' : ''}`} />
              <span>{isPolling ? 'Polling Gmail...' : 'Poll Inbox Now'}</span>
            </button>
          </div>
        </header>

        <div className="p-8 max-w-7xl w-full mx-auto space-y-6">
          {/* KPI METRIC CARDS */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card 1 */}
            <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-5 relative overflow-hidden group hover:border-slate-700/80 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Inbound Events</span>
                <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
                  <Inbox className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 text-2xl font-bold font-mono text-white tracking-tight">
                {stats?.total_events ?? '...'}
              </div>
              <div className="mt-1 text-xs text-slate-500">Processed by defensive guardrails</div>
            </div>

            {/* Card 2 */}
            <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-5 relative overflow-hidden group hover:border-slate-700/80 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Tickets</span>
                <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                  <MessageSquare className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 text-2xl font-bold font-mono text-white tracking-tight">
                {stats?.total_tickets ?? '...'}
              </div>
              <div className="mt-1 text-xs text-slate-500">Validated customer conversations</div>
            </div>

            {/* Card 3 */}
            <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-5 relative overflow-hidden group hover:border-slate-700/80 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Autonomous Replies</span>
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 text-2xl font-bold font-mono text-emerald-400 tracking-tight">
                {stats?.closed_tickets ?? '...'}
              </div>
              <div className="mt-1 text-xs text-slate-500">High-confidence resolution (KB-grounded)</div>
            </div>

            {/* Card 4 */}
            <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-5 relative overflow-hidden group hover:border-slate-700/80 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Human Escalations</span>
                <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center">
                  <AlertTriangle className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 text-2xl font-bold font-mono text-rose-400 tracking-tight">
                {stats?.escalated_tickets ?? '...'}
              </div>
              <div className="mt-1 text-xs text-slate-500">Routed for billing, refunds or P0 outage</div>
            </div>
          </div>

          {/* TAB 1: TICKETS VIEW */}
          {activeTab === 'tickets' && (
            <div className="space-y-4">
              {/* Filter & Search Bar */}
              <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 bg-[#0f1422] p-3 rounded-2xl border border-slate-800/80">
                <div className="flex items-center gap-1.5 overflow-x-auto">
                  {[
                    { id: 'all', label: 'All Tickets' },
                    { id: 'open', label: 'Open' },
                    { id: 'escalated', label: '⚠️ Escalated' },
                    { id: 'closed', label: '✓ Autonomous Resolved' }
                  ].map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setStatusFilter(tab.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        statusFilter === tab.id
                          ? 'bg-slate-800 text-white shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Search by subject, email, or category..."
                    className="w-full sm:w-72 bg-slate-900/90 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              {/* Tickets Table */}
              <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl overflow-hidden shadow-xl">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                      <th className="py-3 px-4">Subject</th>
                      <th className="py-3 px-4">Customer Email</th>
                      <th className="py-3 px-4">AI Category</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">Received At</th>
                      <th className="py-3 px-4 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredTickets.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-16 text-center text-slate-500">
                          <MessageSquare className="w-8 h-8 text-slate-600 mx-auto mb-2 opacity-50" />
                          <p className="text-sm font-semibold">No inquiries found in this category.</p>
                          <p className="text-xs text-slate-600 mt-1">Inbound emails to Gmail will trigger instant real-time AI triage.</p>
                        </td>
                      </tr>
                    ) : (
                      filteredTickets.map(t => (
                        <tr key={t.id} className="hover:bg-slate-800/30 transition-colors group">
                          <td className="py-3.5 px-4 font-semibold text-slate-200">
                            {t.subject}
                          </td>
                          <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                            {t.customer_email}
                          </td>
                          <td className="py-3.5 px-4">
                            <span className="px-2 py-0.5 rounded-md bg-slate-800/80 border border-slate-700/60 text-cyan-300 text-[11px] font-mono">
                              {t.category}
                            </span>
                          </td>
                          <td className="py-3.5 px-4">
                            {t.status === 'closed' && (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                Resolved by AI
                              </span>
                            )}
                            {t.status === 'escalated' && (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-rose-950/80 text-rose-400 border border-rose-800/60">
                                <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"></span>
                                Escalated to Human
                              </span>
                            )}
                            {t.status !== 'closed' && t.status !== 'escalated' && (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-950/80 text-amber-400 border border-amber-800/60">
                                <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                                Open
                              </span>
                            )}
                          </td>
                          <td className="py-3.5 px-4 text-slate-500 font-mono text-[11px]">
                            {new Date(t.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                          </td>
                          <td className="py-3.5 px-4 text-center">
                            <button
                              onClick={() => openTicketThread(t)}
                              className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors"
                            >
                              View Thread
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 2: EVENTS AUDIT LOG */}
          {activeTab === 'events' && (
            <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl overflow-hidden shadow-xl">
              <div className="p-4 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">Gmail Inbound Processing Event Stream</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Live verification of defensive guardrails, deduplication idempotency, and database event logging.
                  </p>
                </div>
              </div>
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                    <th className="py-3 px-4">Message ID (Gmail)</th>
                    <th className="py-3 px-4">Processing Status</th>
                    <th className="py-3 px-4">Details / Skip Reason</th>
                    <th className="py-3 px-4">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {events.map(ev => (
                    <tr key={ev.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-4 text-slate-400">{ev.gmail_message_id}</td>
                      <td className="py-3 px-4">
                        {ev.status === 'processed' ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                            PROCESSED
                          </span>
                        ) : ev.status === 'skipped' ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                            SKIPPED
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800">
                            FAILED
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-sans text-slate-300">
                        {ev.error || 'Successfully routed and delivered to AI Agent'}
                      </td>
                      <td className="py-3 px-4 text-slate-500 text-[11px]">
                        {new Date(ev.created_at).toLocaleTimeString('en-US')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: KNOWLEDGE BASE EDITOR */}
          {activeTab === 'kb' && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-start">
              {/* Sections List */}
              <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-3 space-y-1">
                <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Knowledge Base Articles
                </div>
                {kbList.map(item => (
                  <button
                    key={item.slug}
                    onClick={() => loadKBArticle(item.slug)}
                    className={`w-full text-left p-3 rounded-xl text-xs transition-all ${
                      selectedKB?.slug === item.slug
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                    }`}
                  >
                    <div className="font-semibold text-slate-200">{item.title}</div>
                    <div className="font-mono text-[10px] text-slate-500 mt-0.5">slug: {item.slug}</div>
                  </button>
                ))}
              </div>

              {/* Live Editor */}
              <div className="md:col-span-3 bg-[#0f1422] border border-slate-800/80 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <span>{selectedKB?.title}</span>
                      <span className="text-xs font-mono font-normal text-slate-400 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                        {selectedKB?.slug}
                      </span>
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">
                      The AI Support Agent reads this document in real-time via tool calls to ground all customer answers.
                    </p>
                  </div>

                  <button
                    onClick={saveKBArticle}
                    disabled={kbSaving}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                      saveSuccess
                        ? 'bg-emerald-600 text-white'
                        : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-600/20'
                    }`}
                  >
                    {saveSuccess ? (
                      <>
                        <Check className="w-3.5 h-3.5" />
                        <span>Saved to Database</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-3.5 h-3.5" />
                        <span>{kbSaving ? 'Saving...' : 'Save to Supabase'}</span>
                      </>
                    )}
                  </button>
                </div>

                <textarea
                  value={kbContent}
                  onChange={e => setKbContent(e.target.value)}
                  rows={20}
                  className="w-full bg-[#080b13] border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-200 leading-relaxed focus:outline-none focus:border-cyan-500 transition-colors resize-y"
                  placeholder="Edit article Markdown content here..."
                />
              </div>
            </div>
          )}

          {/* TAB 4: SYSTEM TOPOLOGY */}
          {activeTab === 'system' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-6 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                  <Database className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Supabase PostgreSQL 17</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Enterprise relational backend hosted in US-West-2. Houses tickets, messages, events, and dynamic knowledge base sections.
                </p>
                <div className="pt-2 text-xs text-emerald-400 font-mono flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  Active & Verified (SSL TLS 1.3)
                </div>
              </div>

              <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-6 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Google Gemini Models</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Pydantic AI orchestrator running gemini-3.1-flash-lite with automated tool calling and structured Pydantic schema validation.
                </p>
                <div className="pt-2 text-xs text-cyan-400 font-mono flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  Active & Grounded
                </div>
              </div>

              <div className="bg-[#0f1422] border border-slate-800/80 rounded-2xl p-6 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
                  <Mail className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-white">Gmail REST API Client</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Automated background poller worker with idempotent message tracking and custom label management to eliminate infinite loops.
                </p>
                <div className="pt-2 text-xs text-blue-400 font-mono flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                  OAuth2 Token Valid
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* TICKET THREAD MODAL (LTR SLIDE-OVER) */}
      {activeTicket && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0f1422] border border-slate-800 w-full max-w-2xl rounded-2xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/40">
              <div>
                <h3 className="font-bold text-base text-white">{activeTicket.subject}</h3>
                <div className="text-xs text-slate-400 font-mono mt-0.5 flex items-center gap-2">
                  <span>From: {activeTicket.customer_email}</span>
                  <span>•</span>
                  <span>Category: {activeTicket.category}</span>
                </div>
              </div>
              <button
                onClick={() => setActiveTicket(null)}
                className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Conversation Flow */}
            <div className="p-6 overflow-y-auto flex-1 space-y-4">
              {loadingThread ? (
                <div className="text-center py-12 text-slate-500 text-xs">Loading conversation history...</div>
              ) : ticketMessages.length === 0 ? (
                <div className="text-center py-12 text-slate-500 text-xs">No messages recorded for this ticket.</div>
              ) : (
                ticketMessages.map(m => (
                  <div
                    key={m.id}
                    className={`flex gap-3 max-w-[90%] ${
                      m.direction === 'outbound' ? 'ml-auto flex-row-reverse' : 'mr-auto'
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs ${
                        m.direction === 'outbound'
                          ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {m.direction === 'outbound' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                    </div>

                    <div
                      className={`rounded-2xl p-4 text-xs leading-relaxed ${
                        m.direction === 'outbound'
                          ? 'bg-slate-900 border border-cyan-500/30 text-slate-100 shadow-sm'
                          : 'bg-slate-800/80 border border-slate-700/60 text-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[10px] text-slate-400 mb-2 border-b border-slate-700/40 pb-1.5">
                        <span className="font-semibold">
                          {m.direction === 'outbound' ? '🤖 CloudScale AI Agent' : '👤 Customer Inquiry'}
                        </span>
                        <span className="font-mono">
                          {new Date(m.created_at).toLocaleTimeString('en-US')}
                        </span>
                      </div>
                      <div className="whitespace-pre-wrap">{m.body}</div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Modal Actions */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => updateTicketStatus(activeTicket.id, 'closed')}
                  className="px-3 py-1.5 rounded-lg bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-600/30 text-xs font-semibold transition-colors"
                >
                  Mark as Resolved
                </button>
                <button
                  onClick={() => updateTicketStatus(activeTicket.id, 'escalated')}
                  className="px-3 py-1.5 rounded-lg bg-rose-600/20 text-rose-400 border border-rose-500/30 hover:bg-rose-600/30 text-xs font-semibold transition-colors"
                >
                  Escalate to Human
                </button>
              </div>

              <button
                onClick={() => setActiveTicket(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
