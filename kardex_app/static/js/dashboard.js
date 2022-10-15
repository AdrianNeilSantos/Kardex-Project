window.onload = async () => {
  await fetchDataset();

  generateCharts();
};

const vizSlider = tns({
  container: '.viz-slider',
  items: 4,
  slideBy: 'page',
  center: true,
  mouseDrag: true,
  swipeAngle: false,
  controls: false,
  nav: false,
  loop: false,
  speed: 400
});

let dataset = [];
const fetchDataset = async () => {
  await axios
    .get('https://raw.githubusercontent.com/freeCodeCamp/ProjectReferenceData/master/GDP-data.json')
    .then((res) => {
      dataset = res.data;
    })
    .catch((err) => console.log(err));
};

const generateCharts = () => {
  const vizHolders = document.querySelectorAll('.viz-holder');
  vizHolders.forEach((vizHolder) => {
    vizHolder.innerHTML = '';
    console.log('vizHolder', vizHolder.id)
    generateChart(vizHolder.id);
  });
};

const formatQtr = (str) => {
  const splt = str.split('-');
   if (splt[1] === '01') {
     return `${splt[0]} Q1`;
   } else if (splt[1] === '04') {
     return `${splt[0]} Q2`;
   } else if (splt[1] === '07') {
     return `${splt[0]} Q3`;
   } else if (splt[1] === '10') {
     return `${splt[0]} Q4`;
   }
}

const generateChart = (targetId) => {
  console.log('data', Object.keys(d3))
  const w = 0.25 * 1.0334 * window.innerWidth - 16;
  const h = 0.7778 * w;
  const padding = w/10;

  const xScale = d3
    .scaleTime()
    .domain([
      d3.min(dataset.data, (d) => new Date(d[0])),
      d3.max(dataset.data, (d) => new Date(d[0]))
    ])
    .range([padding, w - padding]);
  const yScale = d3.scaleLinear()
    .domain([
      0,
      d3.max(dataset.data, (d) => d[1])
    ])
    .range([h - padding, padding]);

  const overlay = d3
    .select(`#${targetId}`)
    .append('div')
    .attr('id', `tooltip${targetId}`)
    .style('opacity', 0);

  const svg = d3
    .select(`#${targetId}`)
    .append('svg')
    .attr('width', w)
    .attr('height', h)
    .attr('class', 'chart-svg');

  svg
    .append('text')
    .attr('x', ((w - (padding * 2)) / 3))
    .attr('y', Math.max(padding / 2, 32))
    .attr('id', 'title')
    .attr('class', 'fs-2')
    .text('United States GDP');

  svg
    .selectAll('rect')
    .data(dataset.data)
    .enter()
    .append('rect')
    .attr('x', (d) => xScale(new Date(d[0])))
    .attr('y', (d) => yScale(d[1]))
    .attr('width', (w - padding) / dataset.data.length)
    .attr('height', (d) => h - yScale(d[1]) - padding)
    .attr('data-date', (d) => d[0])
    .attr('data-gdp', (d) => d[1])
    .attr('class', 'bar')
    .attr('fill', '#5C8A74')
    .on('mouseover', (e, d) => {
      overlay
        .transition()
        .duration(200)
        .style('opacity', 0.9);

      overlay
        .html(`${formatQtr(d[0])}<br>$${d[1]} Billion`)
        .attr('data-date', d[0])
        .style('left', `${e.pageX + 48}px`)
        .style('top', `${e.pageY - 80}px`);
    })
    .on('mouseout', (d) => {
      overlay
        .transition()
        .duration(500)
        .style('opacity', 0);
    });

  const xAxis = d3.axisBottom(xScale);
  const yAxis = d3.axisLeft(yScale);

  svg
    .append('g')
    .attr('transform', `translate(0, ${h - padding})`)
    .attr('id', 'x-axis')
    .call(xAxis);
  
  svg
    .append('g')
    .attr('transform', `translate(${padding}, 0)`)
    .attr('id', 'y-axis')
    .call(yAxis);
};
