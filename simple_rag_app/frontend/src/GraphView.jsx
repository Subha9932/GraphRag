import React, { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Loader2 } from 'lucide-react';

const GraphView = () => {
    const [data, setData] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const graphRef = useRef();

    useEffect(() => {
        fetchGraphData();
    }, []);

    const fetchGraphData = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/graph');
            if (!response.ok) {
                throw new Error('Failed to load graph data');
            }
            const graphData = await response.json();

            if (!graphData.nodes || !graphData.links) {
                throw new Error('Invalid data format');
            }

            setData(graphData);
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!loading && data.nodes.length > 0 && graphRef.current) {
            setTimeout(() => {
                graphRef.current.zoomToFit(400);
            }, 500);
        }
    }, [loading, data]);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', color: '#94a3b8' }}>
                <Loader2 className="animate-spin" size={40} color="#3b82f6" />
                <span style={{ marginLeft: '10px', color: '#e2e8f0', fontWeight: '500' }}>Loading Knowledge Graph...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ color: '#ef4444', textAlign: 'center', padding: '2rem' }}>
                <h3>Error Loading Graph</h3>
                <p>{error}</p>
                <button onClick={fetchGraphData} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#334155', border: 'none', color: 'white', borderRadius: '4px' }}>Retry</button>
            </div>
        );
    }

    return (
        <div style={{ height: '700px', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', overflow: 'hidden', position: 'relative' }}>
            <div style={{ position: 'absolute', top: 15, left: 15, zIndex: 10, color: '#94a3b8', fontSize: '0.85rem', fontWeight: '500', pointerEvents: 'none', background: 'rgba(0,0,0,0.5)', padding: '4px 8px', borderRadius: '4px' }}>
                Scroll to zoom • Drag to pan • Click node to focus
            </div>
            <ForceGraph2D
                ref={graphRef}
                graphData={data}
                nodeLabel="description"
                nodeAutoColorBy="type"
                backgroundColor="rgba(0,0,0,0)" // Transparent to let container bg show

                // STANDARD LINK STYLES
                linkWidth={1.5}
                linkColor={() => '#475569'}
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}

                // Custom Node Rendering
                nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 12 / globalScale;

                    // Outer Glow
                    ctx.beginPath();
                    ctx.fillStyle = node.color || '#3b82f6';
                    ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = node.color;
                    ctx.fill();
                    ctx.shadowBlur = 0; // Reset

                    // Node body
                    ctx.beginPath();
                    ctx.fillStyle = node.color || '#3b82f6';
                    ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false);
                    ctx.fill();

                    // Text Label (Always visible for main nodes, or on zoom)
                    if (globalScale > 1.2) {
                        ctx.font = `${fontSize}px Inter, Sans-Serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = '#e2e8f0'; // Light text
                        ctx.fillText(label, node.x, node.y + 10);
                    }
                }}
            />
        </div>
    );
};

export default GraphView;
