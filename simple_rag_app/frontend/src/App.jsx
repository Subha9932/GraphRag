import React, { useState, useRef, useEffect } from 'react';
import {
    Send, Github, Loader2, MessageSquare, Share2,
    LayoutDashboard, Database, Activity, GitBranch,
    Cpu, Globe, Terminal, UploadCloud, Folder, Copy, Check
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import GraphView from './GraphView';

// Custom Code Block Component with Copy Functionality
const CodeBlock = ({ node, inline, className, children, ...props }) => {
    const match = /language-(\w+)/.exec(className || '');
    const codeText = String(children).replace(/\n$/, '');
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(codeText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return !inline && match ? (
        <div style={{ position: 'relative', marginTop: '1rem', marginBottom: '1rem' }}>
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                background: '#022c22', padding: '0.2rem 0.8rem',
                borderTopLeftRadius: '8px', borderTopRightRadius: '8px',
                border: '1px solid var(--border-color)', borderBottom: 'none',
                fontSize: '0.75rem', color: '#9cc2c0', fontFamily: 'Outfit, sans-serif'
            }}>
                <span>{match[1].toUpperCase()}</span>
                <button onClick={handleCopy} className="copy-btn" style={{ position: 'static', margin: 0 }}>
                    {copied ? <Check size={12} color="#34d399" /> : <Copy size={12} />}
                    {copied ? "Copied" : "Copy"}
                </button>
            </div>
            <code className={className} {...props} style={{
                display: 'block', padding: '1rem', background: '#011417',
                borderBottomLeftRadius: '8px', borderBottomRightRadius: '8px',
                border: '1px solid var(--border-color)', overflowX: 'auto',
                margin: 0
            }}>
                {children}
            </code>
        </div>
    ) : (
        <code className={className} {...props} style={{
            background: 'rgba(52, 211, 153, 0.1)', padding: '0.1rem 0.3rem', borderRadius: '4px',
            color: '#34d399', fontSize: '0.85em'
        }}>
            {children}
        </code>
    );
};

function App() {
    const [activeTab, setActiveTab] = useState('chat');
    const [ingestMode, setIngestMode] = useState('github');
    const [repoUrl, setRepoUrl] = useState('');
    const [selectedFiles, setSelectedFiles] = useState(null);
    const [ingestStatus, setIngestStatus] = useState(null);
    const [isIngesting, setIsIngesting] = useState(false);

    // Drag & Drop State
    const [isDragActive, setIsDragActive] = useState(false);

    // Chat & Thinking State
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: 'Myridius Cortex Online. \nHow can I assist you with your project analysis today?',
            sender: 'bot',
            timestamp: new Date().toLocaleTimeString()
        }
    ]);
    const [inputQuery, setInputQuery] = useState('');
    const [isThinking, setIsThinking] = useState(false);
    const [thinkingStep, setThinkingStep] = useState(0);
    const thinkingSteps = [
        "Analyzing collective genius vectors...",
        "Navigating digital graph nodes...",
        "Synthesizing strategic insights...",
        "Optimizing innovation pathways...",
        "Finalizing output..."
    ];

    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isThinking, thinkingStep]);

    // Simulate thinking steps
    useEffect(() => {
        let interval;
        if (isThinking) {
            setThinkingStep(0);
            interval = setInterval(() => {
                setThinkingStep(prev => (prev < thinkingSteps.length - 1 ? prev + 1 : prev));
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isThinking]);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFiles(e.target.files);
            setIngestStatus({ message: `Selected ${e.target.files.length} files. Ready to index.`, type: 'info' });
        }
    };

    // Drag & Drop Handlers
    const handleDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            // Note: Standard Drag & Drop of a folder in Chrome/Edge populates e.dataTransfer.files 
            // but strictly speaking, webkitdirectory on input is more robust for folders. 
            // We will accept what's dropped. Use the input for deep folder structures if drop fails.
            setSelectedFiles(files);
            setIngestStatus({ message: `Received ${files.length} items from drop.`, type: 'info' });
        }
    };

    const handleIngest = async () => {
        setIsIngesting(true);
        setIngestStatus({ message: 'Initializing knowledge graph construction...', type: 'info' });

        try {
            let response;
            if (ingestMode === 'github') {
                if (!repoUrl.trim()) {
                    setIngestStatus({ message: 'Error: Repository URL required', type: 'error' });
                    setIsIngesting(false);
                    return;
                }
                response = await fetch('http://localhost:8000/api/ingest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ repo_url: repoUrl })
                });
            } else {
                if (!selectedFiles || selectedFiles.length === 0) {
                    setIngestStatus({ message: 'Error: No source files detected', type: 'error' });
                    setIsIngesting(false);
                    return;
                }
                const formData = new FormData();
                for (let i = 0; i < selectedFiles.length; i++) {
                    const file = selectedFiles[i];
                    if (file.webkitRelativePath.includes("node_modules") || file.webkitRelativePath.includes(".git")) continue;
                    formData.append('files', file);
                }
                response = await fetch('http://localhost:8000/api/ingest/upload', {
                    method: 'POST',
                    body: formData
                });
            }

            const data = await response.json();
            if (response.ok) {
                setIngestStatus({ message: 'Graph Construction Complete.', type: 'success' });
                setMessages(prev => [...prev, {
                    id: Date.now(),
                    text: `**System Update**\n\nIngested ${data.processed_files || 'codebase'} nodes into the collective intelligence graph. Ready for analysis.`,
                    sender: 'bot',
                    timestamp: new Date().toLocaleTimeString()
                }]);
            } else {
                setIngestStatus({ message: `Construction Failed: ${data.detail}`, type: 'error' });
            }
        } catch (error) {
            setIngestStatus({ message: `Connection Error: ${error.message}`, type: 'error' });
        } finally {
            setIsIngesting(false);
        }
    };

    const handleSendQuery = async () => {
        if (!inputQuery.trim()) return;

        const userMsg = {
            id: Date.now(),
            text: inputQuery,
            sender: 'user',
            timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, userMsg]);
        setInputQuery('');
        setIsThinking(true);

        try {
            const response = await fetch('http://localhost:8000/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMsg.text })
            });

            const data = await response.json();

            setTimeout(() => {
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    text: response.ok ? data.response : "Error retrieving knowledge.",
                    sender: 'bot',
                    timestamp: new Date().toLocaleTimeString(),
                    // We don't save steps anymore as per new UI request, just the result
                }]);
                setIsThinking(false);
            }, 800);

        } catch (error) {
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: `Connection Error: ${error.message}`,
                sender: 'bot',
                timestamp: new Date().toLocaleTimeString()
            }]);
            setIsThinking(false);
        }
    };

    return (
        <div className="app-container">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="brand" style={{ justifyContent: 'center', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                    <img src="/logo.png" alt="Myridius" className="brand-logo" style={{ height: '45px', width: 'auto' }} />
                </div>

                <div className="sidebar-section">
                    <h3>Source Ingestion</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                                className={`view-btn ${ingestMode === 'github' ? 'active' : ''}`}
                                onClick={() => setIngestMode('github')}
                                style={{ flex: 1, justifyContent: 'center', borderRadius: '8px' }}
                            >
                                <Github size={18} /> GitHub
                            </button>
                            <button
                                className={`view-btn ${ingestMode === 'folder' ? 'active' : ''}`}
                                onClick={() => setIngestMode('folder')}
                                style={{ flex: 1, justifyContent: 'center', borderRadius: '8px' }}
                            >
                                <Folder size={18} /> Local
                            </button>
                        </div>

                        {ingestMode === 'github' ? (
                            <input
                                className="input-box"
                                type="text"
                                placeholder="https://github.com/org/repo"
                                value={repoUrl}
                                onChange={(e) => setRepoUrl(e.target.value)}
                            />
                        ) : (
                            <div
                                className={`drop-zone ${isDragActive ? 'drag-active' : ''}`}
                                onDragEnter={handleDragEnter}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                            >
                                <UploadCloud size={32} color={isDragActive ? '#34d399' : '#9cc2c0'} style={{ marginBottom: '0.5rem' }} />
                                <p style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
                                    {selectedFiles ? `${selectedFiles.length} files selected` : "Drag files/folder here"}
                                </p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>or click to browse</p>
                                <input
                                    type="file"
                                    webkitdirectory=""
                                    directory=""
                                    multiple
                                    onChange={handleFileChange}
                                />
                            </div>
                        )}

                        <button className="primary-btn" onClick={handleIngest} disabled={isIngesting}>
                            {isIngesting ? <Loader2 className="animate-spin" size={18} /> : <GitBranch size={18} />}
                            {isIngesting ? 'BUILD GRAPH' : 'INDEX DATA'}
                        </button>

                        {ingestStatus && (
                            <div className={`status-message ${ingestStatus.type === 'error' ? 'status-error' : (ingestStatus.type === 'success' ? 'status-success' : 'status-info')}`}>
                                {ingestStatus.message}
                            </div>
                        )}
                    </div>
                </div>

                <div className="sidebar-section">
                    <h3>Interface Mode</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <button
                            className={`view-btn ${activeTab === 'chat' ? 'active' : ''}`}
                            onClick={() => setActiveTab('chat')}
                        >
                            <LayoutDashboard size={18} /> Strategy Chat
                        </button>
                        <button
                            className={`view-btn ${activeTab === 'graph' ? 'active' : ''}`}
                            onClick={() => setActiveTab('graph')}
                        >
                            <Share2 size={18} /> Knowledge Graph
                        </button>
                    </div>
                </div>

                <div style={{ marginTop: 'auto' }}>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center', color: 'var(--text-secondary)', fontSize: '0.75rem', opacity: 0.75 }}>
                        <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#34d399', boxShadow: '0 0 10px #34d399' }}></div>
                        COLLECTIVE GENIUS: ACTIVE
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <header className="header-bar">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', opacity: 0.8 }}>
                        <Globe size={18} color="#34d399" />
                        <span style={{ fontWeight: 500, fontSize: '0.9rem', letterSpacing: '1px', textTransform: 'uppercase' }}>Ecosystem: Connected</span>
                    </div>
                </header>

                {activeTab === 'chat' ? (
                    <>
                        <div className="chat-container">
                            {messages.map((msg) => (
                                <div key={msg.id} className={`message ${msg.sender}`}>
                                    <div className={`avatar ${msg.sender}`}>
                                        {msg.sender === 'bot' ? <Cpu size={20} color="#022c22" /> : <div style={{ fontSize: '12px', fontWeight: 'bold' }}>USR</div>}
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxWidth: '80%' }}>
                                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginLeft: '4px', letterSpacing: '0.5px' }}>
                                            {msg.sender === 'bot' ? 'MYRIDIUS' : 'USER'} • {msg.timestamp}
                                        </div>
                                        <div className="bubble">
                                            <ReactMarkdown
                                                remarkPlugins={[remarkGfm]}
                                                components={{
                                                    code: CodeBlock
                                                }}
                                            >
                                                {msg.text}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {isThinking && (
                                <div className="message bot">
                                    <div className="avatar bot">
                                        <Loader2 size={20} className="animate-spin" color="#022c22" />
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxWidth: '80%' }}>
                                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginLeft: '4px' }}>
                                            MYRIDIUS • INNOVATING
                                        </div>
                                        <div className="thinking-process">
                                            <div className="thinking-header">
                                                <Terminal size={14} /> CORE.PROCESS
                                            </div>
                                            <div className="thinking-steps">
                                                {/* Single Line Display as requested */}
                                                <div className="step active">
                                                    {thinkingSteps[thinkingStep]}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        <div className="input-area">
                            <div className="input-wrapper">
                                <input
                                    className="query-input"
                                    type="text"
                                    placeholder="Input query for strategic analysis..."
                                    value={inputQuery}
                                    onChange={(e) => setInputQuery(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendQuery()}
                                    disabled={isThinking}
                                />
                                <button className="send-btn" onClick={handleSendQuery} disabled={isThinking || !inputQuery.trim()}>
                                    <Send size={20} />
                                </button>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="graph-container">
                        <GraphView />
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
