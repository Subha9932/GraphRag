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
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', color: '#000000' }}>
                <Loader2 className="animate-spin" size={40} color="#a855f7" />
                <span style={{ marginLeft: '10px', color: '#000000', fontWeight: 'bold' }}>Loading Knowledge Graph...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ color: '#dc2626', textAlign: 'center', padding: '2rem' }}>
                <h3>Error Loading Graph</h3>
                <p>{error}</p>
                <button onClick={fetchGraphData} style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}>Retry</button>
            </div>
        );
    }

    return (
        <div style={{ height: '700px', border: '1px solid #cbd5e1', borderRadius: '8px', overflow: 'hidden', background: '#ffffff', position: 'relative' }}>
            <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 10, color: '#000000', fontSize: '0.9rem', fontWeight: 'bold', pointerEvents: 'none', textShadow: '0 0 2px white' }}>
                Scroll to zoom • Drag to pan • Click node to focus
            </div>
            <ForceGraph2D
                ref={graphRef}
                graphData={data}
                nodeLabel="description"
                nodeAutoColorBy="type"

                // STANDARD LINK STYLES (No custom canvas object)
                linkWidth={2}
                linkColor={() => '#000000'} // Force black
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}

                // Custom Node Rendering
                nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 14 / globalScale;

                    // Outer Glow
                    ctx.beginPath();
                    ctx.fillStyle = node.color || '#a855f7';
                    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = node.color;
                    ctx.fill();
                    ctx.shadowBlur = 0; // Reset

                    // Node body
                    ctx.beginPath();
                    ctx.fillStyle = node.color || '#a855f7';
                    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                    ctx.fill();

                    // Border (Black)
                    ctx.strokeStyle = '#000000';
                    ctx.lineWidth = 1 / globalScale;
                    ctx.stroke();

                    // Text Label
                    ctx.font = `bold ${fontSize}px Sans-Serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#000000';
                    ctx.fillText(label, node.x, node.y + 10);
                }}
                nodeCanvasObjectMode={() => 'replace'}
            />
        </div>
    );
};

export default GraphView;
