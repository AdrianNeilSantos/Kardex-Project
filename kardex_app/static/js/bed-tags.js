/* global _, axios, html2canvas, moment */
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

let currKardexs = [];
let kardexTotal = 0;
const bedTagContainerTemplate = document.querySelector('.bed-tag-container');
const bedTagsGroupContainer = document.querySelector('.bed-tags-group-container');
const downloadAsJPG = (e) => {
  const target = e.target.closest('.small-bed-tag');
  target.classList.remove('box-shadow');
  const patientName = target.querySelector('.name-span')
    .textContent
    .replace('Patient\'s Name: ', '');
  console.log(target);
  html2canvas(target).then(async (canvas) => {
    const imgDataURL = canvas.toDataURL('image/jpeg');
    // console.log(imgDataURL);
    const imgDataBlob = await (await fetch(imgDataURL)).blob();
    const bedTag = new File([imgDataBlob], `Bed Tag - ${ patientName }.jpg`, {
      type: 'image/jpeg',
      lastModified: new Date()
    });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(bedTag);
    link.download = `Bed Tag - ${ patientName }.jpg`;
    link.click();
  });
};

const generateSmallBedTags = () => {
  const bedTagContainers = currKardexs.map((kardex) => {
    const bedTagContainer = bedTagContainerTemplate.cloneNode(true);
    bedTagContainer.classList.remove('d-none');

    const smallBedTag = bedTagContainer.querySelector('.small-bed-tag');
    smallBedTag.classList.remove('d-none');

    const smallBedTagText = smallBedTag.querySelector('.small-bed-tag-text');

    const idDiv = document.createElement('div');
    idDiv.classList.add('border-dashed', 'text-center', 'mb-2', 'py-1', 'px-1');
    idDiv.style.width = '97%';
    const idLine = document.createElement('span');
    idLine.classList.add('span1', 'fw-bold');
    idLine.textContent = `BED TAG NO ${ kardex.id }`;
    idDiv.append(idLine); 
    smallBedTagText.append(idDiv);

    const nameDiv = document.createElement('div');
    nameDiv.classList.add('border-dashed', 'w-100', 'py-3', 'px-1');
    const nameLine = document.createElement('span');
    nameLine.classList.add('name-span', 'span1');
    nameLine.textContent = `Patient's Name: ${ kardex.last_name || '' }, ${ kardex.first_name || '' }`;
    nameDiv.append(nameLine);
    smallBedTagText.append(nameDiv);

    const sexAgeDiv = document.createElement('div');
    sexAgeDiv.classList.add('border-dashed', 'w-100', 'py-3', 'px-1');
    const sexAgeLine = document.createElement('span');
    sexAgeLine.classList.add('span1');
    if (kardex.sex && kardex.age) {
      sexAgeLine.textContent = `Age/Sex: ${kardex.age} years old, ${kardex.sex}`;
    } else {
      sexAgeLine.textContent = 'Age/Sex:';
    }
    sexAgeDiv.append(sexAgeLine);
    smallBedTagText.append(sexAgeDiv);

    const hospitalNumDiv = document.createElement('div');
    hospitalNumDiv.classList.add('border-dashed', 'w-100', 'py-3', 'px-1');
    const hospitalNumLine = document.createElement('span');
    hospitalNumLine.classList.add('span1');
    hospitalNumLine.textContent = `Hospital No.: ${ kardex.hospital_num || '' }`;
    hospitalNumDiv.append(hospitalNumLine);
    smallBedTagText.append(hospitalNumDiv);

    const dateDiv = document.createElement('div');
    dateDiv.classList.add('border-dashed', 'w-100', 'py-3', 'px-1');
    const dateLine = document.createElement('span');
    dateLine.classList.add('span1');
    if (kardex.date_time) { 
      dateLine.textContent = `Date and Time of Admission: ${ moment(kardex.date_time).format('MMMM Do YYYY, h:mm A') }`;
    } else {
      dateLine.textContent = `Date and Time of Admission: ${ moment(kardex.date_added).format('MMMM Do YYYY, h:mm A') }`;
    }
    dateDiv.append(dateLine);
    smallBedTagText.append(dateDiv);

    const hospitalDrsDiv = document.createElement('div');
    hospitalDrsDiv.classList.add('border-dashed', 'w-100', 'py-3', 'px-1');
    const hospitalDrsLine = document.createElement('span');
    hospitalDrsLine.classList.add('span1');
    hospitalDrsLine.textContent = `Physician: ${ kardex.drs || '' }`;
    hospitalDrsDiv.append(hospitalDrsLine);
    smallBedTagText.append(hospitalDrsDiv);

    const bedTagIdSpan = smallBedTag.querySelector('.bed-tag-id-span');
    bedTagIdSpan.textContent = kardex.id;
    bedTagIdSpan.classList.add('d-none');

    return bedTagContainer;
  });

  bedTagsGroupContainer.append(...bedTagContainers);

  const downloadAsJPGLinks = document.querySelectorAll('.download-as-jpg-link');
  downloadAsJPGLinks.forEach((link) => link.addEventListener('click', downloadAsJPG));
};

window.onresize = () => {
  const smallBedTags = document.querySelectorAll('.small-bed-tag');
  smallBedTags.forEach((smallBedTag) => {
    smallBedTag.querySelectorAll('span').forEach((span) => {
      span.style.fontSize = `${1.75 * smallBedTag.offsetWidth / 1022}rem`;
    });
  });
};

let firstAPICall = true;
let bedTagNameFilter = '';
let bedTagMinDateFilter = '';
let bedTagMaxDateFilter = '';
const getKardexPage = async (page) => {
  await axios
    .get(`/api/v1/kardex/paginated/?name=${ bedTagNameFilter }&min-date=${ bedTagMinDateFilter }&max-date=${ bedTagMaxDateFilter }&limit=100&offset=${(page - 1) * 100}`)
    .then((res) => {
      currKardexs = res.data.results
        .map((kardex) => {
          kardex.edited_at = kardex.edited_at.reverse();
          return kardex;
        });
      kardexTotal = res.data.count;

      generateSmallBedTags();

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
const bedTagsCounterSpans = document.querySelectorAll('.bed-tags-counter-span');
let freezePageControllers = false;
const getRelevantData = async (page) => {
  freezePageControllers = true;
  bedTagsGroupContainer.style.minHeight = '282px';
  removeChildren('bed-tags-group-container');

  await getKardexPage(page);
  bedTagsGroupContainer.style.minHeight = currKardexs.length ? '' : '282px';
  freezePageControllers = false;

  const offset = (page - 1) * 100;
  const pages = ~~(kardexTotal / 100) + 1;
  bedTagsCounterSpans.forEach((el) => {
    el.textContent = `Showing ${kardexTotal ? offset + 1 : 0}-${offset + currKardexs.length} out of ${kardexTotal} Bed Tags accessible to you across ${ pages } ${ pages === 1 ? 'page' : 'pages' }`;
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
const dateRangeMinInput = document.querySelector('#dateRangeMinInput');
const dateRangeMaxInput = document.querySelector('#dateRangeMaxInput');

const filterKardexs = (e) => {
  if (e !== 'forceFilterKardexs' && e.target.id !== 'searchDashboardBtn' && e.key !== 'Enter')
    return;

  bedTagNameFilter = searchDashboardInput.value;
  bedTagMinDateFilter = dateRangeMinInput.value;
  bedTagMaxDateFilter = dateRangeMaxInput.value;

  getRelevantData(pageInputs[0].value);
};

searchDashboardInput.addEventListener('keydown', filterKardexs);
searchDashboardBtn.addEventListener('click', filterKardexs);
dateRangeMinInput.addEventListener('keydown', filterKardexs);
dateRangeMaxInput.addEventListener('keydown', filterKardexs);

const sortBedTagsSelect = document.querySelector('#sortBedTagsSelect');
const sortKardexs = () => {
  const sortVal = sortBedTagsSelect.value;
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
  bedTagsGroupContainer.querySelectorAll('.bed-tag-container').forEach((el) => {
    el.style.order = currKardexs
      .map((kardex) => kardex.id)
      .indexOf(parseInt(el.querySelector('.bed-tag-id-span').textContent));
  });
};
sortKardexs();
sortBedTagsSelect.addEventListener('change', sortKardexs);

const clearFiltersBtn = document.querySelector('.clear-filters-btn');
const clearFilters = () => {
  dateRangeMinInput.value = '';
  dateRangeMaxInput.value = '';
  searchDashboardInput.value = '';
  filterKardexs('forceFilterKardexs');
};
clearFiltersBtn.addEventListener('click', clearFilters);
