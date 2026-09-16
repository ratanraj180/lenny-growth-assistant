import { useState, useEffect, useRef } from 'react';
import { api } from './api';
import type { Session, Message, SessionWithMessages } from './api';
import { MessageSquare, Plus, Send, PenTool, LayoutTemplate, Loader2, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<SessionWithMessages | null>(null);
  const [input, setInput] = useState('');
  const [provider, setProvider] = useState('ollama');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [artifact, setArtifact] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);

  const loadSessions = async () => {
    try {
      const data = await api.getSessions();
      setSessions(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleNewSession = async () => {
    try {
      const session = await api.createSession('New Conversation');
      setSessions([session, ...sessions]);
      setCurrentSession({ ...session, messages: [] });
      setArtifact(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const selectSession = async (id: string) => {
    try {
      const session = await api.getSession(id);
      setCurrentSession(session);
      setArtifact(null);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const sendMessage = async (skill?: string) => {
    if (!input.trim() || !currentSession) return;
    const userMsg = input;
    setInput('');
    setLoading(true);
    setError(null);

    // Optimistic update
    const optimisticMsg: Message = { id: Date.now().toString(), role: 'user', content: userMsg };
    setCurrentSession(prev => prev ? { ...prev, messages: [...prev.messages, optimisticMsg] } : prev);

    try {
      const responseMsg = await api.sendMessage(currentSession.id, userMsg, provider, skill);
      
      // Extract artifact if present
      const artifactMatch = responseMsg.content.match(/```artifact\n([\s\S]*?)```/);
      if (artifactMatch) {
        setArtifact(artifactMatch[1]);
        responseMsg.content = responseMsg.content.replace(/```artifact\n[\s\S]*?```/, '> *Generated an artifact. See the Artifact Viewer panel.*');
      }

      setCurrentSession(prev => prev ? { ...prev, messages: [...prev.messages, responseMsg] } : prev);
      
      if (currentSession.messages.length === 0) {
        loadSessions(); // refresh title if it was updated
      }
    } catch (err: any) {
      setError(err.message || "Failed to communicate with the agent.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100 font-sans text-slate-800">
      {/* Sidebar */}
      <div className="w-72 bg-white/80 backdrop-blur-xl border-r border-slate-200/60 flex flex-col shadow-sm z-10 relative">
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-indigo-600 to-purple-600 p-2.5 rounded-xl shadow-lg shadow-indigo-200">
              <LayoutTemplate className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-700 to-purple-700">Lenny Growth</h1>
              <p className="text-xs text-slate-500 font-medium tracking-wide uppercase mt-0.5">Assistant</p>
            </div>
          </div>
        </div>
        <div className="p-4">
          <button 
            onClick={handleNewSession}
            className="w-full flex items-center justify-center gap-2 bg-slate-900 text-white font-medium rounded-xl px-4 py-3 hover:bg-slate-800 hover:shadow-md transition-all active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" /> New Chat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
          <div className="px-3 pb-2 pt-1">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Recent Conversations</h3>
          </div>
          {sessions.map(s => (
            <button
              key={s.id}
              onClick={() => selectSession(s.id)}
              className={`w-full text-left px-4 py-3 flex items-center gap-3 rounded-xl transition-all ${
                currentSession?.id === s.id 
                  ? 'bg-indigo-50 text-indigo-700 font-medium shadow-sm border border-indigo-100/50' 
                  : 'text-slate-600 hover:bg-slate-50 border border-transparent'
              }`}
            >
              <MessageSquare className={`w-4 h-4 ${currentSession?.id === s.id ? 'text-indigo-500' : 'text-slate-400'}`} />
              <span className="truncate text-sm">{s.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className={`flex flex-col flex-1 bg-white/50 relative ${artifact ? 'max-w-3xl border-r border-slate-200' : ''}`}>
        
        {/* Header */}
        <div className="h-16 border-b border-slate-200/60 bg-white/80 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
          <h2 className="font-semibold text-slate-700 text-lg">{currentSession ? currentSession.title : ''}</h2>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm bg-slate-100/80 p-1.5 rounded-lg border border-slate-200">
              <span className="text-slate-500 font-medium px-2">Model</span>
              <select 
                value={provider}
                onChange={e => setProvider(e.target.value)}
                className="border-none rounded-md px-3 py-1 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700 font-medium cursor-pointer"
              >
                <option value="ollama">Ollama (Local)</option>
                <option value="claude">Claude 3 (Cloud)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto px-4 py-8 sm:px-8 bg-transparent">
          {!currentSession && (
            <div className="h-full flex flex-col items-center justify-center text-slate-400">
              <div className="w-24 h-24 mb-6 bg-slate-100 rounded-full flex items-center justify-center shadow-inner">
                <LayoutTemplate className="w-10 h-10 text-slate-300" />
              </div>
              <h2 className="text-2xl font-semibold text-slate-700 mb-2">Welcome to Lenny Growth</h2>
              <p className="max-w-md text-center leading-relaxed">Ask any questions about product, growth, or startups based on Lenny Rachitsky's podcast and newsletter.</p>
            </div>
          )}
          
          {error && (
            <div className="mb-8 bg-red-50/80 backdrop-blur-sm text-red-600 p-4 rounded-2xl flex items-start gap-3 border border-red-100 shadow-sm max-w-3xl mx-auto">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-red-500" />
              <p className="text-sm font-medium leading-relaxed">{error}</p>
            </div>
          )}

          <div className="max-w-3xl mx-auto w-full space-y-8">
            {currentSession?.messages.map((msg, i) => (
              <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 shrink-0 flex items-center justify-center shadow-md mt-1">
                    <LayoutTemplate className="w-4 h-4 text-white" />
                  </div>
                )}
                
                <div className={`max-w-[85%] rounded-3xl px-6 py-4 shadow-sm ${
                  msg.role === 'user' 
                    ? 'bg-indigo-600 text-white rounded-tr-sm' 
                    : 'bg-white border border-slate-100 rounded-tl-sm text-slate-700'
                }`}>
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm prose-slate max-w-none prose-p:leading-relaxed prose-headings:text-slate-800 prose-a:text-indigo-600 hover:prose-a:text-indigo-700">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="leading-relaxed">{msg.content}</p>
                  )}
                  
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-5 pt-4 border-t border-slate-100 text-xs text-slate-500">
                      <p className="font-semibold text-slate-400 mb-2 uppercase tracking-wide">Sources Context</p>
                      <ul className="list-none space-y-1.5">
                        {msg.sources.map(s => (
                          <li key={s.id} className="flex items-start gap-2">
                            <span className="text-indigo-400 font-medium">[{s.id}]</span>
                            <span className="leading-snug">{s.title}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex gap-4 justify-start">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 shrink-0 flex items-center justify-center shadow-md mt-1">
                  <LayoutTemplate className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white border border-slate-100 rounded-3xl rounded-tl-sm px-6 py-5 shadow-sm flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
                  <span className="text-slate-500 text-sm font-medium">Analyzing transcripts...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        </div>

        {/* Input Area */}
        {currentSession && (
          <div className="p-6 bg-transparent">
            <div className="max-w-3xl mx-auto relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
              <div className="relative bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden flex flex-col">
                <textarea
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder="Ask a question about growth, product-market fit, or startups..."
                  className="w-full pl-6 pr-4 pt-5 pb-16 focus:outline-none resize-none text-slate-700 bg-transparent placeholder-slate-400"
                  rows={2}
                  disabled={loading}
                />
                
                <div className="absolute bottom-3 left-4 right-3 flex items-center justify-between">
                  <button 
                    onClick={() => sendMessage('ship30')}
                    disabled={loading || !input.trim()}
                    title="Generate Ship 30 for 30 Essay"
                    className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-purple-600 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors disabled:opacity-50 disabled:hover:bg-purple-50 border border-purple-100"
                  >
                    <PenTool className="w-3.5 h-3.5" />
                    Ship 30 Essay
                  </button>
                  
                  <button 
                    onClick={() => sendMessage()}
                    disabled={loading || !input.trim()}
                    className="p-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:hover:bg-indigo-600 active:scale-95"
                  >
                    <Send className="w-4 h-4 translate-x-px -translate-y-px" />
                  </button>
                </div>
              </div>
            </div>
            <p className="text-center text-xs text-slate-400 mt-4">AI can make mistakes. Everything is grounded in Lenny's newsletter data.</p>
          </div>
        )}
      </div>

      {/* Artifact Viewer Panel */}
      {artifact && (
        <div className="w-[500px] shrink-0 bg-white flex flex-col shadow-2xl z-20 border-l border-slate-200">
          <div className="h-16 border-b border-slate-100 flex items-center px-6 bg-slate-50/50">
            <h2 className="font-semibold text-slate-800 flex items-center gap-2">
              <div className="p-1.5 bg-purple-100 text-purple-600 rounded-lg">
                <PenTool className="w-4 h-4" />
              </div>
              Generated Artifact
            </h2>
            <button onClick={() => setArtifact(null)} className="ml-auto text-sm font-medium text-slate-500 hover:text-slate-800 bg-white border shadow-sm px-3 py-1 rounded-md transition-colors">Close</button>
          </div>
          <div className="flex-1 p-8 overflow-y-auto bg-slate-50">
            <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm prose prose-slate prose-headings:font-bold prose-h1:text-2xl prose-a:text-indigo-600 hover:prose-a:text-indigo-700 max-w-none">
              <ReactMarkdown>{artifact}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
