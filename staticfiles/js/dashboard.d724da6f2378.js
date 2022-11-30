/* global _, axios, bootstrap, d3, moment, tns */

window.onload = async () => {
  await fetchDataset();

  generateCharts();
};

window.onresize = () => {
  generateCharts();
};

const vizSlider = tns({ // eslint-disable-line
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

const removeChildren = (targetAttr) => {
  const target = document.querySelector(`#${targetAttr}`)
    || document.querySelector(`.${targetAttr}`);
  if (!target || !target.firstElementChild)
    return;
  
  let child = target.firstElementChild;
  while (child) {
    target.removeChild(child);
    child = target.firstElementChild;
  }
};

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
};

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
          console.log(targetId, targetId.toLowerCase().includes('modal'));
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
    .on('mouseout', () => {
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

let currKardexs = [];
let currNurses = [];
let kardexTotal = 0;
const kardexContainerTemplate = document.querySelector('.kardex-container');
const kardexGroupContainer = document.querySelector('.kardex-group-container');
const generateSmallKardexs = () => {
  const kardexContainers = currKardexs.map((kardex) => {
    const kardexContainer = kardexContainerTemplate.cloneNode(true);
    kardexContainer.classList.remove('d-none');

    const smallKardex = kardexContainer.querySelector('.small-kardex');
    smallKardex.classList.remove('d-none');

    const smallKardexText = smallKardex.querySelector('.small-kardex-text');
    if (kardex.first_name || kardex.last_name) {
      const nameLine = document.createElement('b');
      nameLine.textContent = `${ kardex.last_name || '' }, ${ kardex.first_name || '' }`;
      smallKardexText.append(nameLine, document.createElement('br'));
    }

    if (kardex.sex && kardex.age) {
      const sexAgeLine = document.createElement('span');
      sexAgeLine.textContent = `${kardex.sex}, ${kardex.age} years old`;
      smallKardexText.append(sexAgeLine, document.createElement('br'));
    }

    const dateLine = document.createElement('span');
    if (kardex.date_time) { 
      dateLine.textContent = moment(kardex.date_time).format('MMMM Do YYYY, h:mm A');
    } else {
      dateLine.textContent = moment(kardex.date_added).format('MMMM Do YYYY, h:mm A');
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

    const editHistoryLines = kardex.edited_by.map((edited_by, i) => {
      const editHistoryLine = document.createElement('span');

      const editedByLine = document.createElement('span');
      const currNurse = currNurses.find(nurse => nurse.id === Number(edited_by));
      editedByLine.textContent = `  ${currNurse.last_name}, ${currNurse.first_name}`;
      editedByLine.classList.add('cut-text', 'ms-3', 'me-1');

      const editedAtLine = document.createElement('span');
      editedAtLine.textContent = `(${moment(kardex.edited_at[i]).format('MMMM Do YYYY, h:mm A')})`;

      editHistoryLine.append(editedByLine, editedAtLine, document.createElement('br'));
      return editHistoryLine;
    });
    smallKardexText.append(editedByTitle, document.createElement('br'), ...editHistoryLines);

    const viewLink = smallKardex.querySelector('.view-link');
    viewLink.href = `/view-kardex/${kardex.id}`;

    const updateLink = smallKardex.querySelector('.update-link');
    updateLink.href = `/update-kardex/${kardex.id}`;

    const kardexIdSpan = smallKardex.querySelector('.kardex-id-span');
    kardexIdSpan.textContent = kardex.id;
    kardexIdSpan.classList.add('d-none');

    return kardexContainer;
  });

  kardexGroupContainer.append(...kardexContainers);
};

const getNursePage = async (page) => {
  await axios
    .get(`/api/v1/nurse/paginated/?limit=100&offset=${(page - 1) * 100}`)
    .then((res) => {
      currNurses = res.data.results;
    })
    .catch((err) => {
      console.log(err);
    });
};

let firstAPICall = true;
let kardexNameFilter = '';
let kardexMinDateFilter = '';
let kardexMaxDateFilter = '';
const getKardexPage = async (page) => {
  await axios
    .get(`/api/v1/kardex/paginated/?name=${ kardexNameFilter }&min-date=${ kardexMinDateFilter }&max-date=${ kardexMaxDateFilter }&limit=100&offset=${(page - 1) * 100}`)
    .then((res) => {
      currKardexs = res.data.results
        .map((kardex) => {
          kardex.edited_at = kardex.edited_at.reverse();
          return kardex;
        });
      kardexTotal = res.data.count;

      generateSmallKardexs();

      if (!firstAPICall) {
        // filterKardexs('forceFilterKardexs');
        sortKardexs();
      }
      firstAPICall = false;
    })
    .catch((err) => {
      console.log(err);
    });
};

const prevBtns = Array.from(document.querySelectorAll('.prev-btn'));
const nextBtns = Array.from(document.querySelectorAll('.next-btn'));
const refreshBtns = Array.from(document.querySelectorAll('.refresh-btn'));
const kardexCounterSpans = document.querySelectorAll('.kardex-counter-span');
let freezePageControllers = false;
const getRelevantData = async (page) => {
  freezePageControllers = true;
  kardexGroupContainer.style.minHeight = '282px';
  removeChildren('kardex-group-container');

  await getNursePage(page);
  await getKardexPage(page);
  kardexGroupContainer.style.minHeight = currKardexs.length ? '' : '282px';
  freezePageControllers = false;

  const offset = (page - 1) * 100;
  const pages = ~~(kardexTotal / 100) + 1;
  kardexCounterSpans.forEach((el) => {
    el.textContent = `Showing ${kardexTotal ? offset + 1 : 0}-${offset + currKardexs.length} out of ${kardexTotal} Kardex accessible to you across ${ pages } ${ pages === 1 ? 'page' : 'pages' }`;
  });
};
// initialize dashboard with kardex and nurse info for 1st 100 kardexs
getRelevantData(1);

let maxPage = ~~(kardexTotal / 100) + 1;
const pageInputs = document.querySelectorAll('.page-input');
const handlePageInputChange = (e) => {
  if (freezePageControllers)
    return;
  
  const currVal = e.target.value;
  const page = currVal <= 0
    ? 1
    : currVal > maxPage
      ? maxPage
      : currVal;
  pageInputs.forEach((el) => el.value = page);
  getRelevantData(page);
};
pageInputs.forEach((el) => el.addEventListener('change', handlePageInputChange));

const handlePrevBtnClick = () => {
  if (freezePageControllers)
    return;

  const page = pageInputs[0].value - 1 <= 0
    ? 1
    : pageInputs[0].value - 1;
  pageInputs.forEach((el) => el.value = page);
  getRelevantData(page);
};
prevBtns.forEach((el) => el.addEventListener('click', handlePrevBtnClick));

const handleNextBtnClick = () => {
  if (freezePageControllers)
    return;

  const page = pageInputs[0].value + 1 > maxPage
    ? maxPage
    : pageInputs[0].value + 1;
  pageInputs.forEach((el) => el.value = page);
  getRelevantData(page);
};
nextBtns.forEach((el) => el.addEventListener('click', handleNextBtnClick));

const handleRefreshBtnClick = () => {
  if (freezePageControllers)
    return;

  getRelevantData(pageInputs[0].value);
};
refreshBtns.forEach((el) => el.addEventListener('click', handleRefreshBtnClick));

const searchDashboardInput = document.querySelector('#searchDashboardInput');
const searchDashboardBtn = document.querySelector('#searchDashboardBtn');
// const handleDashboardSearch = () => {
//   const searchVal = searchDashboardInput.value;
//   const filteredKardexs = currKardexs.filter((kardex) => {
//     return kardex.name.toLowerCase().includes(searchVal.toLowerCase());
//   });
//   return filteredKardexs;
// };

const dateRangeMinInput = document.querySelector('#dateRangeMinInput');
const dateRangeMaxInput = document.querySelector('#dateRangeMaxInput');
// const filterKardexByDate = () => {
//   const dateFormat = 'YYYY-MM-DD';
//   const minDate = dateRangeMinInput.value
//     ? moment(dateRangeMinInput.value, dateFormat)
//     : moment('0001-01-01', dateFormat);
//   const maxDate = dateRangeMaxInput.value
//     ? moment(new Date(dateRangeMaxInput.value), dateFormat)
//     : moment(new Date(), dateFormat);
//   const filteredKardexs = currKardexs.filter((kardex) => {
//     const kardexDate = moment(kardex.date_time || kardex.date_added, dateFormat);
//     return kardexDate.isBetween(minDate, maxDate);
//   });

//   return filteredKardexs;
// };

// const filterKardexs = (e) => {
//   if (e !== 'forceFilterKardexs' && e.target.id !== 'searchDashboardBtn' && e.key !== 'Enter')
//     return;

//   const filteredKardexsByName = handleDashboardSearch() || currKardexs;
//   const filteredKardexsByDate = filterKardexByDate() || currKardexs;
  
//   const filteredKardexs = currKardexs.filter((kardex) => {
//     return filteredKardexsByName.includes(kardex) && filteredKardexsByDate.includes(kardex);
//   });

//   kardexGroupContainer.querySelectorAll('.kardex-container').forEach((el) => {
//     const kardexId = el.querySelector('.kardex-id-span').textContent;
//     if (filteredKardexs.map((kardex) => kardex.id.toString()).includes(kardexId))
//       el.classList.remove('d-none');
//     else
//       el.classList.add('d-none');
//   });
// };

const filterKardexs = (e) => {
  if (e !== 'forceFilterKardexs' && e.target.id !== 'searchDashboardBtn' && e.key !== 'Enter')
    return;

  kardexNameFilter = searchDashboardInput.value;
  kardexMinDateFilter = dateRangeMinInput.value;
  kardexMaxDateFilter = dateRangeMaxInput.value;

  getRelevantData(pageInputs[0].value);
};

searchDashboardInput.addEventListener('keydown', filterKardexs);
searchDashboardBtn.addEventListener('click', filterKardexs);
dateRangeMinInput.addEventListener('keydown', filterKardexs);
dateRangeMaxInput.addEventListener('keydown', filterKardexs);

const sortKardexSelect = document.querySelector('#sortKardexSelect');
const sortKardexs = () => {
  const sortVal = sortKardexSelect.value;
  switch (sortVal) {
    case '0':
      currKardexs = _.orderBy(currKardexs, ['name'], ['asc']);
      break;
    case '1':
      currKardexs = _.orderBy(currKardexs, ['name'], ['desc']);
      break;
    case '2':
      currKardexs = _.orderBy(currKardexs, ['date_time', 'date_added'], ['desc', 'desc']);
      break;
    case '3':
      currKardexs = _.orderBy(currKardexs, ['date_time', 'date_added'], ['asc', 'asc']);
      break;
    case '4':
      currKardexs = _.orderBy(currKardexs, ['edited_at'], ['desc']);
      break;
    case '5':
      currKardexs = _.orderBy(currKardexs, ['edited_at'], ['asc']);
      break;
    default:
      // do nothing
  }
  kardexGroupContainer.querySelectorAll('.kardex-container').forEach((el) => {
    el.style.order = currKardexs
      .map((kardex) => kardex.id)
      .indexOf(parseInt(el.querySelector('.kardex-id-span').textContent));
  });
};
sortKardexs();
sortKardexSelect.addEventListener('change', sortKardexs);

const clearFiltersBtn = document.querySelector('.clear-filters-btn');
const clearFilters = () => {
  dateRangeMinInput.value = '';
  dateRangeMaxInput.value = '';
  searchDashboardInput.value = '';
  filterKardexs('forceFilterKardexs');
};
clearFiltersBtn.addEventListener('click', clearFilters);
