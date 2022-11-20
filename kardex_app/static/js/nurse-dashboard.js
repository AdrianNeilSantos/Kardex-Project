/* global _, axios, moment, superuser */

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

let currNurses = [];
let nurseTotal = 0;

const currDate = new Date();
const currDay = currDate.getDay();
const currHours = currDate.getHours();
const currMins = currDate.getMinutes();
const currTime = currDate.setHours(currHours, currMins, 0);

const nurseContainerTemplate = document.querySelector('.nurse-container');
const nurseGroupContainer = document.querySelector('.nurse-group-container');
const generateNurseCards = () => {
  const nurseContainers = currNurses.map((nurse) => {
    const nurseContainer = nurseContainerTemplate.cloneNode(true);
    nurseContainer.classList.remove('d-none');

    const nurseCard = nurseContainer.querySelector('.nurse-card');

    const nurseHeader = nurseCard.querySelector('.card-header');
    const currNurseOnDuty = nurse.on_duty && nurse.on_duty.includes(',')
      ? nurse.on_duty.split(',')[currDay].split('-')
      : null;
    let dateNurseOnDuty = currNurseOnDuty
      ? currNurseOnDuty.map((on_duty) => {
        return new Date().setHours(on_duty.slice(0, 2), on_duty.slice(2), 0);
      })
      : null;
    
    const nurseHeaderSpan = nurseHeader.querySelector('span');
    if (dateNurseOnDuty && currTime >= dateNurseOnDuty[0] && currTime < dateNurseOnDuty[1]) {
      nurseHeader.classList.replace('text-danger', 'text-success');
      nurseHeaderSpan.textContent = 'On Duty';
    } else {
      nurseHeader.classList.replace('text-success', 'text-danger');
      nurseHeaderSpan.textContent = 'Off Duty';
    }

    const nurseImage = nurseCard.querySelector('.nurse-image');
    nurseImage.querySelector('img').src = nurse.picture
      ? nurse.picture
      : '/static/images/DO-3.jpg';

    const nurseCardBlock = nurseCard.querySelector('.card-block');
    const nurseName = nurseCardBlock.querySelector('.nurse-name');
    nurseName.textContent = `${ nurse.last_name }, ${ nurse.first_name }`;
    
    const nurseIdLevel = nurseCardBlock.querySelector('.nurse-id-level');
    nurseIdLevel.querySelector('b').textContent = `ID # ${ nurse.id } -`;
    nurseIdLevel.querySelector('span').textContent = nurse.nurse_level
      ? nurse.nurse_level
      : '(Missing Nurse Level)';

    const nurseDemographic = nurseCardBlock.querySelector('.nurse-demographic');
    nurseDemographic.textContent = `${ nurse.sex }, ${ moment().diff(new Date(nurse.birthday), 'years', false) } years old`;

    const nurseOnDuty = nurseCardBlock.querySelector('.nurse-on-duty');
    nurseOnDuty.querySelector('span').textContent = currNurseOnDuty
      ? currNurseOnDuty.map((on_duty) => {
        let hours = parseInt(on_duty.slice(0, 2));
        const mins = on_duty.slice(2);

        let meridiem = 'AM';
        if (hours > 12) {
          hours -= 12;
          meridiem = 'PM';
        }
        return `${ hours.toString() }:${ mins }${ meridiem }`;
      }).join(' - ')
      : '(Missing On Duty Time)';

    const nurseCardFooter = nurseCard.querySelector('.card-footer');
    if (superuser) {
      // for nurse delete modal toggle link
      const deleteLink = document.createElement('a');
      deleteLink.classList.add('delete-link', 'link', 'text-danger');
      deleteLink.href = '#';
      deleteLink.setAttribute('data-bs-toggle', 'modal');
      deleteLink.setAttribute('data-bs-target', `#delete_nurse_${ nurse.id }`);
      
      const deleteIcon = document.createElement('i');
      deleteIcon.classList.add('fa-solid', 'fa-trash');
      deleteLink.appendChild(deleteIcon);

      const deleteSpan = document.createElement('span');
      deleteSpan.textContent = ' Delete';
      deleteLink.appendChild(deleteSpan);

      // for nurse delete modal
      const nurseDeleteModalTemplate = document.querySelector('.nurse-delete-modal');
      const nurseDeleteModal = nurseDeleteModalTemplate.cloneNode(true);

      nurseDeleteModal.id = `delete_nurse_${ nurse.id }`;

      const nurseDeleteModalBody = nurseDeleteModal.querySelector('.modal-body');
      nurseDeleteModalBody.querySelector('strong').textContent = `${ nurse.first_name } ${ nurse.last_name }`;

      const nurseDeleteModalFooter = nurseDeleteModal.querySelector('.modal-footer');
      const nurseDeleteModalFooterLink = nurseDeleteModalFooter.querySelector('a');
      nurseDeleteModalFooterLink.href = `delete-nurse/${ nurse.id }`;

      nurseCard.insertBefore(nurseDeleteModal, nurseCard.firstChild);
      nurseCardFooter.insertBefore(deleteLink, nurseCardFooter.firstChild);
    }

    const visitProfileLink = nurseCardFooter.querySelector('.visit-profile-link');
    visitProfileLink.href = window.location.href.slice(-1) === '/'
      ? window.location.href.slice(0, -1).split('/').slice(0, -1).join('/') + `/profile/${ nurse.id }`
      : window.location.href.split('/').slice(0, -1).join('/') + `/profile/${ nurse.id }`;

    const nurseIdSpan = nurseCard.querySelector('.nurse-id-span');
    nurseIdSpan.classList.add('d-none');
    nurseIdSpan.textContent = nurse.id;

    return nurseContainer;
  });

  nurseGroupContainer.append(...nurseContainers);
};

let firstAPICall = true;
let nurseNameFilter = '';
let nurseMinOnDutyFilter = '';
let nurseMaxOnDutyFilter = '';
const getNursePage = async (page) => {
  await axios
    .get(`/api/v1/nurse/paginated/?&name=${ nurseNameFilter }&min-on-duty=${ nurseMinOnDutyFilter }&max-on-duty=${ nurseMaxOnDutyFilter }&limit=100&offset=${(page - 1) * 100}`)
    .then((res) => {
      currNurses = res.data.results;
      nurseTotal = res.data.count;

      generateNurseCards();

      if (!firstAPICall) {
        sortNurses();
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
const nurseCounterSpans = document.querySelectorAll('.nurse-counter-span');
let freezePageControllers = false;
const getRelevantData = async (page) => {
  // var sCallerName;
  //   {
  //       let re = /([^(]+)@|at ([^(]+) \(/g;
  //       let aRegexResult = re.exec(new Error().stack);
  //       sCallerName = aRegexResult[1] || aRegexResult[2];
  //   }
  //   console.log(sCallerName);
  freezePageControllers = true;
  nurseGroupContainer.style.minHeight = '282px';
  removeChildren('nurse-group-container');

  await getNursePage(page);
  nurseGroupContainer.style.minHeight = currNurses.length ? '' : '282px';
  freezePageControllers = false;

  const offset = (page - 1) * 100;
  const pages = ~~(nurseTotal / 100) + 1;
  nurseCounterSpans.forEach((el) => {
    el.textContent = `Showing ${ nurseTotal ? offset + 1 : 0 }-${ offset + currNurses.length } out of ${ nurseTotal } Nurses visible to you across ${ pages } ${ pages === 1 ? 'page' : 'pages' }`;
  });
};
// initialize dashboard with kardex and nurse info for 1st 100 kardexs
getRelevantData(1);

let maxPage = ~~(nurseTotal / 100) + 1;
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

const onDutyRangeMinInput = document.querySelector('#onDutyRangeMinInput');
const onDutyRangeMaxInput = document.querySelector('#onDutyRangeMaxInput');

const filterNurses = (e) => {
  if (e !== 'forceFilterNurses' && e.target.id !== 'searchDashboardBtn' && e.key !== 'Enter')
    return;

  nurseNameFilter = searchDashboardInput.value;
  nurseMinOnDutyFilter = onDutyRangeMinInput.value;
  nurseMaxOnDutyFilter = onDutyRangeMaxInput.value;

  getRelevantData(pageInputs[0].value);
};
searchDashboardInput.addEventListener('keydown', filterNurses);
searchDashboardBtn.addEventListener('click', filterNurses);
onDutyRangeMinInput.addEventListener('keydown', filterNurses);
onDutyRangeMaxInput.addEventListener('keydown', filterNurses);

const sortNurseSelect = document.querySelector('#sortNurseSelect');
const sortNurses = () => {
  const sortVal = sortNurseSelect.value;
  switch (sortVal) {
  case '0':
    currNurses = _.orderBy(currNurses, ['last_name', 'first_name'], ['asc']);
    break;
  case '1':
    currNurses = _.orderBy(currNurses, ['last_name', 'first_name'], ['desc']);
    break;
  default:
    // do nothing
  }
  nurseGroupContainer.querySelectorAll('.nurse-container').forEach((el) => {
    el.style.order = currNurses
      .map((kardex) => kardex.id)
      .indexOf(parseInt(el.querySelector('.nurse-id-span').textContent));
  });
};
sortNurses();
sortNurseSelect.addEventListener('change', sortNurses);

const clearFiltersBtn = document.querySelector('.clear-filters-btn');
const clearFilters = () => {
  onDutyRangeMinInput.value = '';
  onDutyRangeMaxInput.value = '';
  searchDashboardInput.value = '';
  filterNurses('forceFilterNurses');
};
clearFiltersBtn.addEventListener('click', clearFilters);
