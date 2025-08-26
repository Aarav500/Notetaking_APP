import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Network, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

// Mock data for knowledge graph
const mockNodes = [
  { id: 1, label: 'Machine Learning', group: 'ai', size: 25 },
  { id: 2, label: 'Neural Networks', group: 'ai', size: 20 },
  { id: 3, label: 'Deep Learning', group: 'ai', size: 18 },
  { id: 4, label: 'Computer Vision', group: 'ai', size: 15 },
  { id: 5, label: 'NLP', group: 'ai', size: 15 },
  { id: 6, label: 'React', group: 'web', size: 22 },
  { id: 7, label: 'JavaScript', group: 'web', size: 20 },
  { id: 8, label: 'Hooks', group: 'web', size: 15 },
  { id: 9, label: 'Data Structures', group: 'cs', size: 18 },
  { id: 10, label: 'Algorithms', group: 'cs', size: 18 },
];

const mockEdges = [
  { source: 1, target: 2, strength: 0.8 },
  { source: 1, target: 3, strength: 0.7 },
  { source: 2, target: 3, strength: 0.9 },
  { source: 2, target: 4, strength: 0.6 },
  { source: 3, target: 5, strength: 0.5 },
  { source: 6, target: 7, strength: 0.8 },
  { source: 6, target: 8, strength: 0.9 },
  { source: 7, target: 8, strength: 0.7 },
  { source: 9, target: 10, strength: 0.8 },
  { source: 1, target: 9, strength: 0.3 },
];

// Color mapping for node groups
const groupColors = {
  ai: '#3b82f6', // blue
  web: '#8b5cf6', // purple
  cs: '#10b981', // green
  default: '#6b7280', // gray
};

export default function KnowledgeGraphPreview({ className }) {
  const canvasRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [isAnimating, setIsAnimating] = useState(true);
  const [nodes, setNodes] = useState(mockNodes);
  const [edges, setEdges] = useState(mockEdges);
  
  // Initialize node positions
  useEffect(() => {
    // Set random initial positions
    setNodes(nodes.map(node => ({
      ...node,
      x: Math.random() * 300 + 50,
      y: Math.random() * 200 + 50,
      vx: 0,
      vy: 0,
    })));
  }, []);
  
  // Animation loop for force-directed graph
  useEffect(() => {
    if (!canvasRef.current || !isAnimating) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    let animationFrameId;
    
    // Force-directed graph simulation
    const simulate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, width, height);
      
      // Draw edges
      edges.forEach(edge => {
        const source = nodes.find(n => n.id === edge.source);
        const target = nodes.find(n => n.id === edge.target);
        
        if (source && target) {
          ctx.beginPath();
          ctx.moveTo(source.x, source.y);
          ctx.lineTo(target.x, target.y);
          ctx.strokeStyle = `rgba(156, 163, 175, ${edge.strength})`;
          ctx.lineWidth = edge.strength * 2;
          ctx.stroke();
        }
      });
      
      // Apply forces
      const updatedNodes = [...nodes];
      
      // Repulsive force between nodes
      for (let i = 0; i < updatedNodes.length; i++) {
        for (let j = i + 1; j < updatedNodes.length; j++) {
          const nodeA = updatedNodes[i];
          const nodeB = updatedNodes[j];
          
          const dx = nodeB.x - nodeA.x;
          const dy = nodeB.y - nodeA.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance > 0 && distance < 150) {
            const repulsiveForce = 1 / distance;
            const forceX = dx / distance * repulsiveForce;
            const forceY = dy / distance * repulsiveForce;
            
            nodeA.vx -= forceX;
            nodeA.vy -= forceY;
            nodeB.vx += forceX;
            nodeB.vy += forceY;
          }
        }
      }
      
      // Attractive force along edges
      edges.forEach(edge => {
        const source = updatedNodes.find(n => n.id === edge.source);
        const target = updatedNodes.find(n => n.id === edge.target);
        
        if (source && target) {
          const dx = target.x - source.x;
          const dy = target.y - source.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance > 0) {
            const attractiveForce = (distance - 100) * 0.01 * edge.strength;
            const forceX = dx / distance * attractiveForce;
            const forceY = dy / distance * attractiveForce;
            
            source.vx += forceX;
            source.vy += forceY;
            target.vx -= forceX;
            target.vy -= forceY;
          }
        }
      });
      
      // Center force
      updatedNodes.forEach(node => {
        const dx = width / 2 - node.x;
        const dy = height / 2 - node.y;
        node.vx += dx * 0.001;
        node.vy += dy * 0.001;
        
        // Damping
        node.vx *= 0.9;
        node.vy *= 0.9;
        
        // Update position
        node.x += node.vx;
        node.y += node.vy;
        
        // Boundary constraints
        node.x = Math.max(node.size, Math.min(width - node.size, node.x));
        node.y = Math.max(node.size, Math.min(height - node.size, node.y));
      });
      
      // Draw nodes
      updatedNodes.forEach(node => {
        const isHovered = hoveredNode && hoveredNode.id === node.id;
        
        ctx.beginPath();
        ctx.arc(node.x, node.y, isHovered ? node.size * 1.2 : node.size, 0, Math.PI * 2);
        ctx.fillStyle = groupColors[node.group] || groupColors.default;
        ctx.fill();
        
        if (isHovered) {
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 2;
          ctx.stroke();
        }
        
        // Draw label for larger nodes or hovered node
        if (node.size >= 18 || isHovered) {
          ctx.font = isHovered ? 'bold 12px Inter, sans-serif' : '12px Inter, sans-serif';
          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(node.label, node.x, node.y);
        }
      });
      
      setNodes(updatedNodes);
      
      animationFrameId = requestAnimationFrame(simulate);
    };
    
    simulate();
    
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [nodes, edges, isAnimating, hoveredNode]);
  
  // Handle mouse interactions
  const handleMouseMove = (e) => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Check if mouse is over a node
    const hoveredNode = nodes.find(node => {
      const dx = node.x - x;
      const dy = node.y - y;
      return Math.sqrt(dx * dx + dy * dy) <= node.size;
    });
    
    setHoveredNode(hoveredNode);
    
    // Change cursor style
    canvas.style.cursor = hoveredNode ? 'pointer' : 'default';
  };
  
  const handleClick = () => {
    if (hoveredNode) {
      // In a real app, navigate to the node's detail page
      console.log(`Clicked on node: ${hoveredNode.label}`);
    }
  };
  
  return (
    <div className={`relative rounded-lg border border-border overflow-hidden ${className}`}>
      <div className="absolute top-0 left-0 p-3 flex items-center justify-between w-full bg-card/80 backdrop-blur-sm z-10">
        <div className="flex items-center gap-2">
          <Network className="h-5 w-5 text-primary" />
          <h3 className="font-medium">Knowledge Graph</h3>
        </div>
        <Button variant="ghost" size="sm" className="h-8 px-2">
          <ExternalLink className="h-4 w-4" />
        </Button>
      </div>
      
      <canvas
        ref={canvasRef}
        width={400}
        height={300}
        className="w-full h-full bg-card/30"
        onMouseMove={handleMouseMove}
        onClick={handleClick}
      />
      
      <div className="absolute bottom-0 left-0 p-3 w-full bg-card/80 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">
              {nodes.length} topics • {edges.length} connections
            </span>
          </div>
          <div className="flex gap-2">
            {Object.entries(groupColors).map(([group, color]) => (
              <div key={group} className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs text-muted-foreground capitalize">{group}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}