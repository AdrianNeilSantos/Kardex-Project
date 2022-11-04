window.onload = async () => {
  await fetchDataset();

  generateCharts();
};

window.onresize = () => {
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

const removeChildren = (targetId) => {
  const target = document.querySelector(`#${targetId}`);
  let child = target.firstElementChild;
  while (child) {
    target.removeChild(child);
    child = target.firstElementChild;
  }
}

const generateCharts = () => {
  const vizHolders = document.querySelectorAll('.viz-holder');
  vizHolders.forEach((vizHolder) => {
    removeChildren(vizHolder.id);
    generateChart(vizHolder.id, dataset);
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

const generateChart = (targetId, chartData) => {
  let w, h;
  if (targetId.toLowerCase().includes('modal')) {
    if (window.innerWidth <= window.innerHeight) {
      w = window.innerWidth - 96 - 130 - 64;
      h = w;
    } else {
      h = window.innerHeight - 96 - 130 - 64;
      w = h;
    }
  } else {
    w = 0.25 * 1.0334 * window.innerWidth - 16;
    h = 0.7778 * w;
  }
  const padding = w/10;

  const xScale = d3
    .scaleTime()
    .domain([
      d3.min(chartData.data, (d) => new Date(d[0])),
      d3.max(chartData.data, (d) => new Date(d[0]))
    ])
    .range([padding, w - padding]);
  const yScale = d3.scaleLinear()
    .domain([
      0,
      d3.max(chartData.data, (d) => d[1])
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
    .style('transform', () => {
      if (targetId.toLowerCase().includes('modal')) {
        return `translate(-${w/4}px, 0)`;
      } else {
        return '';
      }
    })
    .attr('class', 'chart-svg');

  svg
    .append('text')
    .attr('x', w / 2)
    .attr('y', padding)
    .attr('id', 'title')
    .attr('text-anchor', 'middle')
    .style('font-size', window.innerWidth / 1440 * 24)
    .text('United States GDP');

  svg
    .selectAll('rect')
    .data(chartData.data)
    .enter()
    .append('rect')
    .attr('x', (d) => xScale(new Date(d[0])))
    .attr('y', (d) => yScale(d[1]))
    .attr('width', (w - padding) / chartData.data.length)
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

      const modal = document.querySelector('.modal-content').getBoundingClientRect();
      overlay
        .html(`${formatQtr(d[0])}<br>$${d[1]} Billion`)
        .attr('data-date', d[0])
        .style('left', () => {
          console.log(targetId, targetId.toLowerCase().includes('modal'))
          return targetId.toLowerCase().includes('modal')
            ? `${e.pageX - modal.left + 48}px`
            : `${e.pageX + 48}px`;
        })
        .style('top', () => {
          return targetId.toLowerCase().includes('modal')
            ? `${e.pageY - modal.top - 80}px`
            : `${e.pageY - 80}px`;
        });
    })
    .on('mouseout', (d) => {
      overlay
        .transition()
        .duration(500)
        .style('opacity', 0);
    })
    .on('click', () => {
      removeChildren('modalViz');
      generateChart('modalViz', chartData);

      const vizModal = new bootstrap.Modal(document.querySelector('#vizModal'));
      vizModal.show();

      document.querySelector('.modal-title').textContent = 'United States GDP';
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

const pageInputs = document.querySelectorAll('.page-input');
const prevBtns = Array.from(document.querySelectorAll('.prev-btn'));
const nextBtns = Array.from(document.querySelectorAll('.next-btn'));
const refreshBtns = Array.from(document.querySelectorAll('.refresh-btn'));

let currKardexs = [];
let kardexTotal = 0;
const kardexContainerTemplate = document.querySelector('.kardex-container');
const kardexGroupContainer = document.querySelector('.kardex-group-container');
const generateSmallKardexs = () => {
  console.log(currKardexs);

  const kardexContainers = currKardexs.map((kardex) => {
    const kardexContainer = kardexContainerTemplate.cloneNode(true);
    kardexContainer.classList.remove('d-none');

    const smallKardex = kardexContainer.querySelector('.small-kardex');
    smallKardex.classList.remove('d-none');

    const smallKardexStripes = smallKardex.querySelector('.small-kardex-stripes');

    const smallKardexText = smallKardex.querySelector('.small-kardex-text');
    if (kardex.name) {
      const nameLine = document.createElement('b');
      nameLine.textContent = kardex.name;
      smallKardexText.append(nameLine, document.createElement('br'));
    }

    if (kardex.sex && kardex.age) {
      const sexAgeLine = document.createElement('span');
      sexAgeLine.textContent = `${kardex.sex}, ${kardex.age} years old`;
      smallKardexText.append(sexAgeLine, document.createElement('br'));
    }

    const dateLine = document.createElement('span');
    if (kardex.date_time) { 
      dateLine.textContent = kardex.date_time;
    } else {
      dateLine.textContent = kardex.date_added;
    }
    smallKardexText.append(dateLine, document.createElement('br'));

    if (kardex.hospital_num) {
      const hospitalNumLine = document.createElement('span');
      hospitalNumLine.textContent = `Hospital Number: ${kardex.hospital_num}`;
      smallKardexText.append(hospitalNumLine, document.createElement('br'));
    }

    smallKardexText.append(document.createElement('br'));
    if (kardex.extra_fields.includes('Transfer in, Transfer out, or Transfer to another Hospital')) {
      const transferLine = document.createElement('span');
      transferLine.textContent = `For ${kardex.extra_field_values[kardex.extra_fields.indexOf('Transfer in, Transfer out, or Transfer to another Hospital')]}`;
      smallKardexText.append(transferLine, document.createElement('br'));
    }

    if (kardex.laboratory_work_ups) {
      const labWorkUpsLine = document.createElement('span');
      labWorkUpsLine.textContent = `Scheduled For: ${kardex.laboratory_work_ups}`;
      smallKardexText.append(labWorkUpsLine, document.createElement('br'));
    }
    
    const editedByTitle = document.createElement('span');
    editedByTitle.textContent = 'Edited By:';

    const editHistoryLines = kardex.edited_by.map((edited_by) => {
      const editHistoryLine = document.createElement('span');

      const editedByLine = document.createElement('span');
      editedByLine.textContent = `  ${edited_by}`;
      editedByLine.classList.add('cut-text');

      const editedAtLine = document.createElement('span');
      editedAtLine.textContent = `  ${kardex.edited_at[kardex.edited_by.indexOf(edited_by)]}`;

      editHistoryLine.append(editedByLine, editedAtLine, document.createElement('br'));
      return editHistoryLine;
    });
    smallKardexText.append(editedByTitle, document.createElement('br'), ...editHistoryLines);

    const viewLink = smallKardex.querySelector('.view-link');
    viewLink.href = `/view-kardex/${kardex.id}`;

    const updateLink = smallKardex.querySelector('.update-link');
    updateLink.href = `/update-kardex/${kardex.id}`;

    return kardexContainer;
  });

  kardexGroupContainer.append(...kardexContainers);
};

const getKardexPage = async (page) => {
  await axios
    .get(`/api/v1/kardex/paginated/?limit=100&offset=${(page - 1) * 100}`)
    .then((res) => {
      currKardexs = res.data.results;
      kardexTotal = res.data.count;

      generateSmallKardexs();
    })
    .catch((err) => {
      console.log(err);
    });
};
// initialize dashboard with first 100 Kardexs
getKardexPage(1);

const handlePageInputChange = (e) => {
  const currVal = e.target.value;
  const page = currVal <= 0
    ? 1
    : currVal;
  pageInputs.forEach((el) => el.value = page);
  getKardexPage(page);
};
pageInputs.forEach((el) => el.addEventListener('change', handlePageInputChange));

const handlePrevBtnClick = () => {
  const currPage = pageInputs[0].value <= 0
    ? 1
    : pageInputs[0].value;
  const page = currPage - 1;
  pageInputs.forEach((el) => el.value = page);
  getKardexPage(page);
};

let maxPage = ~~(kardexTotal / 100);
const handleNextBtnClick = () => {
  const currPage = pageInputs[0].value > maxPage
    ? maxPage
    : pageInputs[0].value;
  const page = currPage + 1;
  pageInputs.forEach((el) => el.value = page);
  getKardexPage(page);
};
