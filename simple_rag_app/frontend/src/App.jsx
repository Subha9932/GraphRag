import React, { useState, useRef, useEffect } from 'react';
import { Send, Github, Loader2, MessageSquare, Share2 } from 'lucide-react';
import GraphView from './GraphView';

function App() {
    const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'graph'

    // Ingestion State
    const [repoUrl, setRepoUrl] = useState('');
    const [ingestStatus, setIngestStatus] = useState({ message: '', type: '' });
    const [isIngesting, setIsIngesting] = useState(false);

    // Chat State
    const [messages, setMessages] = useState([
        { id: 1, text: 'Hello! Once you\'ve ingested a repository, ask me anything about the codebase.', sender: 'bot' }
    ]);
    const [inputQuery, setInputQuery] = useState('');
    const [isThinking, setIsThinking] = useState(false);

    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (activeTab === 'chat') {
            scrollToBottom();
        }
    }, [messages, isThinking, activeTab]);

    const handleIngest = async () => {
        if (!repoUrl.trim()) {
            setIngestStatus({ message: 'Please enter a GitHub URL.', type: 'error' });
            return;
        }

        setIsIngesting(true);
        setIngestStatus({ message: 'Cloning and Indexing... This may take several minutes.', type: 'info' });

        try {
            const response = await fetch('http://localhost:8000/api/ingest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repo_url: repoUrl })
            });

            const data = await response.json();

            if (response.ok) {
                setIngestStatus({ message: data.message || 'Ingestion Successful!', type: 'success' });
                setMessages(prev => [...prev, {
                    id: Date.now(),
                    text: 'Ingestion complete! I have indexed the codebase. Ask me anything or switch to Graph view.',
                    sender: 'bot'
                }]);
            } else {
                setIngestStatus({ message: 'Error: ' + (data.detail || 'Ingestion failed'), type: 'error' });
            }
        } catch (error) {
            setIngestStatus({ message: 'Network Error: ' + error.message, type: 'error' });
        } finally {
            setIsIngesting(false);
        }
    };

    const handleReset = async () => {
        if (!confirm("Are you sure you want to delete all ingested data? This cannot be undone.")) return;

        try {
            const response = await fetch('http://localhost:8000/api/reset', { method: 'POST' });
            if (response.ok) {
                setIngestStatus({ message: 'All data cleared.', type: 'success' });
                setMessages([{ id: 1, text: 'Data cleared. Ready to ingest a new repository.', sender: 'bot' }]);
                setRepoUrl('');
            } else {
                setIngestStatus({ message: 'Failed to clear data.', type: 'error' });
            }
        } catch (error) {
            setIngestStatus({ message: 'Error: ' + error.message, type: 'error' });
        }
    };

    const handleSendQuery = async () => {
        if (!inputQuery.trim()) return;

        const userMsg = { id: Date.now(), text: inputQuery, sender: 'user' };
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

            if (response.ok) {
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    text: data.response,
                    sender: 'bot'
                }]);
            } else {
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    text: "Sorry, I encountered an error providing an answer.",
                    sender: 'bot'
                }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: "Network Error: " + error.message,
                sender: 'bot'
            }]);
        } finally {
            setIsThinking(false);
        }
    };

    return (
        <>
            <div className="background-orb orb-1"></div>
            <div className="background-orb orb-2"></div>

            <div className="container">
                <header>
                    <h1>GraphRAG <span className="highlight">Explorer</span></h1>
                    <p>Ingest GitHub repositories & chat with the knowledge graph.</p>
                </header>

                <main>
                    {/* Ingestion Section */}
                    <section className="glass-panel">
                        <h2>1. Ingest Repository</h2>
                        <div className="input-group">
                            <input
                                type="text"
                                placeholder="https://github.com/username/repo"
                                value={repoUrl}
                                onChange={(e) => setRepoUrl(e.target.value)}
                                disabled={isIngesting}
                            />
                            <button onClick={handleIngest} disabled={isIngesting}>
                                {isIngesting ? <Loader2 className="animate-spin" /> : <Github size={20} />}
                                {isIngesting ? '' : 'Ingest & Index'}
                            </button>
                        </div>

                        <div style={{ marginTop: '1rem', textAlign: 'right' }}>
                            <button
                                onClick={handleReset}
                                disabled={isIngesting}
                                style={{ background: '#ef4444', fontSize: '0.8rem', padding: '0.5rem', marginLeft: 'auto' }}
                            >
                                Clear All Data
                            </button>
                        </div>
                    </section>

                    {/* Interaction Section */}
                    <section className="glass-panel">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h2>2. Explore</h2>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button
                                    onClick={() => setActiveTab('chat')}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        background: activeTab === 'chat' ? 'var(--primary-gradient)' : '#e2e8f0',
                                        color: activeTab === 'chat' ? 'white' : '#000000',
                                        border: '1px solid',
                                        borderColor: activeTab === 'chat' ? 'transparent' : '#cbd5e1'
                                    }}
                                >
                                    <MessageSquare size={16} style={{ marginRight: '5px' }} /> Chat
                                </button>
                                <button
                                    onClick={() => setActiveTab('graph')}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        background: activeTab === 'graph' ? 'var(--primary-gradient)' : '#e2e8f0',
                                        color: activeTab === 'graph' ? 'white' : '#000000',
                                        border: '1px solid',
                                        borderColor: activeTab === 'graph' ? 'transparent' : '#cbd5e1'
                                    }}
                                >
                                    <Share2 size={16} style={{ marginRight: '5px' }} /> Graph
                                </button>
                            </div>
                        </div>

                        {activeTab === 'chat' ? (
                            <>
                                <div className="chat-window">
                                    {messages.map((msg) => (
                                        <div key={msg.id} className={`message ${msg.sender}`}>
                                            <div className="bubble">
                                                {msg.sender === 'bot'
                                                    ? msg.text.split('\n').map((line, i) => <div key={i}>{line || <br />}</div>)
                                                    : msg.text}
                                            </div>
                                        </div>
                                    ))}
                                    {isThinking && (
                                        <div className="message bot">
                                            <div className="bubble loading">Thinking...</div>
                                        </div>
                                    )}
                                    <div ref={chatEndRef} />
                                </div>
                                <div className="input-group">
                                    <input
                                        type="text"
                                        placeholder="Ask a question..."
                                        value={inputQuery}
                                        onChange={(e) => setInputQuery(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSendQuery()}
                                        disabled={isThinking}
                                    />
                                    <button onClick={handleSendQuery} disabled={isThinking}>
                                        <Send size={20} />
                                        Send
                                    </button>
                                </div>
                            </>
                        ) : (
                            <GraphView />
                        )}
                    </section>
                </main>
            </div>
        </>
    )
}

export default App;
