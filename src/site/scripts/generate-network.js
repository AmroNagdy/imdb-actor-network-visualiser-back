// https://observablehq.com/@d3/force-directed-graph
// https://github.com/d3/d3-force

const height = 600;
const width = 600;

// Data.
const data = {
  "nodes": [
    { "id": "Amro", "group": 1 },
    { "id": "Ava", "group": 1 },
    { "id": "Harriet", "group": 2 }
  ],
  "links": [
    { "source": "Amro", "target": "Ava", "weight": 10 },
    { "source": "Amro", "target": "Harriet", "weight": 4 }
  ]
};

const getColour = group => {
  const colours = d3.schemeCategory10;

  return colours[group] % colours.length;
};

const drag = simulation => {
  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  };

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  };

  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  };

  return d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended);
};

const links = data.links.map(link => Object.create(link));
const nodes = data.nodes.map(node => Object.create(node));

const svg = d3.select("#imdb-actor-network")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id))
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
 .attr("stroke", "#999")
 .attr("stroke-opacity", 0.6)
 .selectAll("line")
 .data(links)
 .join("line")
 .attr("stroke-width", d => Math.sqrt(d.weight));

const node = svg.append("g")
  .attr("stroke", "#fff")
  .attr("stroke-width", 1.5)
  .selectAll("circle")
  .data(nodes)
  .join("circle")
  .attr("r", 5)
  .attr("fill", d => getColour(d.group))
  .call(drag(simulation));

node.append("title")
  .text(d => d.id);

simulation.on("tick", () => {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);
});
