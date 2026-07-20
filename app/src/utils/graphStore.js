import { apiService } from '../services/api'

export async function sendToGraph(label, iconName = 'Box', color = '#3B82F6', notes = '', targetFilename = null) {
  try {
    let activeGraphFile = targetFilename;
    let graphData = { nodes: [], edges: [], nextNodeId: 1 };

    if (!activeGraphFile) {
      const newName = `investigation_${Date.now()}`;
      activeGraphFile = newName + '.json';
    } else {
      try {
        const { data } = await apiService.loadGraph(activeGraphFile);
        graphData = data;
      } catch (e) {
        // file might not exist
      }
    }

    if (!graphData.nodes) graphData.nodes = [];
    if (!graphData.edges) graphData.edges = [];
    let currentId = parseInt(graphData.nextNodeId) || 1;
    
    const newNode = {
      id: `node_${currentId}`,
      type: 'custom',
      position: { x: Math.random() * 200 + 100, y: Math.random() * 200 + 100 },
      data: { label, iconName, color, notes }
    };

    graphData.nextNodeId = currentId + 1;
    graphData.nodes.push(newNode);

    await apiService.saveGraph(activeGraphFile, graphData);
    
    // Custom event for listeners
    window.dispatchEvent(new CustomEvent('graph-updated'))

  } catch (e) {
    console.error("Failed to send to graph", e);
  }
}

export async function sendMultipleToGraph(newNodes, newEdges, targetFilename = null) {
  try {
    let activeGraphFile = targetFilename;
    let graphData = { nodes: [], edges: [], nextNodeId: 1 };

    if (!activeGraphFile) {
      const newName = `investigation_${Date.now()}`;
      activeGraphFile = newName + '.json';
    } else {
      try {
        const { data } = await apiService.loadGraph(activeGraphFile);
        graphData = data;
      } catch(e) {}
    }

    if (!graphData.nodes) graphData.nodes = [];
    if (!graphData.edges) graphData.edges = [];
    
    graphData.nodes.push(...newNodes);
    graphData.edges.push(...newEdges);

    // Update nextNodeId to avoid conflicts (rough estimation)
    graphData.nextNodeId = graphData.nodes.length + 1;

    await apiService.saveGraph(activeGraphFile, graphData);
    
    window.dispatchEvent(new CustomEvent('graph-updated'))
  } catch (e) {
    console.error("Failed to send multiple to graph", e);
  }
}
