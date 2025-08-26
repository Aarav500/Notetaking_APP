import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@radix-ui/react-tabs';
import { GitBranch, Network, Cube, Lightbulb, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';
import FlowchartBuilder from './FlowchartBuilder';
import MindMapBuilder from './MindMapBuilder';
import KnowledgeTreeBuilder from './KnowledgeTreeBuilder';

const IdeationTools = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('flowchart');
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Button variant="ghost" size="sm" onClick={onBack} className="mr-2">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Ideation Tools</h1>
        </div>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="grid grid-cols-3 mb-6">
          <TabsTrigger value="flowchart" className="flex items-center justify-center py-2">
            <GitBranch className="h-4 w-4 mr-2" />
            Flowchart
          </TabsTrigger>
          <TabsTrigger value="mindmap" className="flex items-center justify-center py-2">
            <Network className="h-4 w-4 mr-2" />
            Mind Map
          </TabsTrigger>
          <TabsTrigger value="knowledgetree" className="flex items-center justify-center py-2">
            <Cube className="h-4 w-4 mr-2" />
            3D Knowledge Tree
          </TabsTrigger>
        </TabsList>
        
        <div className="flex-1 overflow-auto">
          <TabsContent value="flowchart" className="h-full">
            <FlowchartBuilder />
          </TabsContent>
          
          <TabsContent value="mindmap" className="h-full">
            <MindMapBuilder />
          </TabsContent>
          
          <TabsContent value="knowledgetree" className="h-full">
            <KnowledgeTreeBuilder />
          </TabsContent>
        </div>
      </Tabs>
      
      <div className="mt-6 p-4 border rounded-md bg-muted/20">
        <div className="flex items-start">
          <Lightbulb className="h-5 w-5 mr-2 text-yellow-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium mb-1">Ideation Tips</h3>
            <p className="text-sm text-muted-foreground">
              {activeTab === 'flowchart' && 
                "Flowcharts are perfect for visualizing processes, algorithms, and decision flows. Use them to map out step-by-step procedures."}
              {activeTab === 'mindmap' && 
                "Mind maps help organize ideas around a central concept. They're great for brainstorming and connecting related thoughts."}
              {activeTab === 'knowledgetree' && 
                "3D Knowledge Trees visualize hierarchical relationships in a three-dimensional space, making complex knowledge structures easier to understand."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IdeationTools;