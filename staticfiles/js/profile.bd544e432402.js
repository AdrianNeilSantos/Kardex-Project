/* global _, axios, bootstrap, moment, nurseId, origPicture */

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
    .get(`/api/v1/kardex/paginated/?nurse=${nurseId}&name=${ kardexNameFilter }&min-date=${ kardexMinDateFilter }&max-date=${ kardexMaxDateFilter }&limit=100&offset=${(page - 1) * 100}`)
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
  // var sCallerName;
  //   {
  //       let re = /([^(]+)@|at ([^(]+) \(/g;
  //       let aRegexResult = re.exec(new Error().stack);
  //       sCallerName = aRegexResult[1] || aRegexResult[2];
  //   }
  //   console.log(sCallerName);
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

const dateRangeMinInput = document.querySelector('#dateRangeMinInput');
const dateRangeMaxInput = document.querySelector('#dateRangeMaxInput');

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

const showUpdateProfileBtn = document.querySelector('#showUpdateProfileBtn');
const updateProfileForm = document.querySelector('#updateProfileForm');
const toggleUpdateProfileFormDisplay = () => {
  if (!showUpdateProfileBtn.classList.contains('bg-danger')) {
    showUpdateProfileBtn.classList.add('bg-danger');
    showUpdateProfileBtn.querySelector('i').classList.replace('fa-eye', 'fa-eye-slash');
    showUpdateProfileBtn.querySelector('span').textContent = 'Hide Update Profile';
    updateProfileForm.classList.remove('d-none');
  } else {
    showUpdateProfileBtn.classList.remove('bg-danger');
    showUpdateProfileBtn.querySelector('i').classList.replace('fa-eye-slash', 'fa-eye');
    showUpdateProfileBtn.querySelector('span').textContent = 'Show Update Profile';
    updateProfileForm.classList.add('d-none');
  }
};
showUpdateProfileBtn.addEventListener('click', toggleUpdateProfileFormDisplay);

const showSpecificOnDutyInputsBtn = document.querySelector('#showSpecificOnDutyInputsBtn');
const specificOnDutyInputsDiv = document.querySelector('#specificOnDutyInputsDiv');
const onDutyGeneralInputs = document.querySelectorAll('input[id*="General"]');
const onDutyGeneralInputGroup = onDutyGeneralInputs[0].closest('.input-group');
const toggleSpecificOnDutyInputsDisplay = () => {
  if (!showSpecificOnDutyInputsBtn.classList.contains('btn-outline-danger')) {
    showSpecificOnDutyInputsBtn.classList.replace('btn-outline-primary', 'btn-outline-danger');
    showSpecificOnDutyInputsBtn.textContent = 'Hide Specific On Duty Inputs';
    specificOnDutyInputsDiv.classList.replace('d-none', 'd-flex');

    onDutyGeneralInputGroup.classList.add('d-none');
  } else {
    showSpecificOnDutyInputsBtn.classList.replace('btn-outline-danger', 'btn-outline-primary');
    showSpecificOnDutyInputsBtn.textContent = 'Show Specific On Duty Inputs';
    specificOnDutyInputsDiv.classList.replace('d-flex', 'd-none');

    onDutyGeneralInputGroup.classList.remove('d-none');
  }
};
showSpecificOnDutyInputsBtn.addEventListener('click', toggleSpecificOnDutyInputsDisplay);

const updateProfileBtn = document.querySelector('#updateProfileBtn');
const formInputs = document.querySelectorAll('#updateProfileForm .form-control');
const checkSubmitEligibility = () => {
  const errors = [];

  const onDutyInputs = Array.from(document.querySelectorAll('input[id^="onDuty"][class="form-control"]'));
  formInputs.forEach((input) => {
    if (input.offsetParent === null)
      return;

    if (!input.value.length)
      errors.push(`${input.parentNode.querySelector('.input-group-text').textContent} is required. Please input a value.`);
  
    if (input.id.includes('Start')) {
      const onDutyStartInput = input;
      const onDutyEndInput = onDutyInputs[onDutyInputs.indexOf(input) + 1];

      if (onDutyStartInput.value.length !== 4)
        errors.push(`${onDutyStartInput.parentNode.querySelector('.input-group-text').textContent} on duty time must be in 24-hour format (HHss). Please input such value.`);

      if (onDutyEndInput.value.length !== 4)
        errors.push(`${onDutyEndInput.parentNode.querySelector('.input-group-text').textContent} on duty time must be in 24-hour format (HHss). Please input such value.`);

      if (Number(onDutyStartInput.value) > Number(onDutyEndInput.value))
        errors.push(`${onDutyStartInput.parentNode.querySelector('.input-group-text').textContent} on duty time must be earlier than ${onDutyEndInput.parentNode.querySelector('.input-group-text').textContent}.`);
    }
  });

  !errors.length
    ? submitUpdateProfileForm()
    : displayErrors(errors);
};
updateProfileBtn.addEventListener('click', checkSubmitEligibility);

const pictureInput = document.querySelector('#pictureInput');
const cardPictureDisplay = document.querySelector('.card-img-top');
const imgGearBtn = document.querySelector('.img-gear-btn'); 
const readImgFile = () => {
  if (!pictureInput.files || !pictureInput.files[0])
    return;
  
  const reader = new FileReader();

  reader.onload = (e) => {
    cardPictureDisplay.src = e.target.result;
    imgXBtn.classList.remove('d-none');
    imgCheckBtn.classList.remove('d-none');
  };
  reader.readAsDataURL(pictureInput.files[0]);
};
pictureInput.addEventListener('change', readImgFile);
imgGearBtn.addEventListener('click', () => pictureInput.click());

const imgXBtn = document.querySelector('.img-x-btn');
const revertImg = () => {
  pictureInput.value = '';
  cardPictureDisplay.src = origPicture;

  imgXBtn.classList.add('d-none');
  imgCheckBtn.classList.add('d-none');
};
imgXBtn.addEventListener('click', revertImg);

const imgCheckBtn = document.querySelector('.img-check-btn');
// const updateImg = () => {
//   updateProfileForm.submit();
// };
imgCheckBtn.addEventListener('click', checkSubmitEligibility);

const displayErrors = (errors) => {
  const toastContainer = document.querySelector('.toast-container');
  const errorToast = document.querySelector('.error-toast');
  errors.forEach(error => {
    const errorToastClone = errorToast.cloneNode(true);
    errorToastClone.querySelector('.toast-body').textContent = error;
    toastContainer.appendChild(errorToastClone);
    
    new bootstrap.Toast(errorToastClone).show();

    // 7s since autohide is set to 5s to allow for fade animation
    setTimeout(() => {
      toastContainer.removeChild(errorToastClone);
    }, 7000);
  });
};

const onDutyMondayStartInput = document.querySelector('#onDutyMondayStartInput');
const onDutyMondayEndInput = document.querySelector('#onDutyMondayEndInput');
const onDutyTuesdayStartInput = document.querySelector('#onDutyTuesdayStartInput');
const onDutyTuesdayEndInput = document.querySelector('#onDutyTuesdayEndInput');
const onDutyWednesdayStartInput = document.querySelector('#onDutyWednesdayStartInput');
const onDutyWednesdayEndInput = document.querySelector('#onDutyWednesdayEndInput');
const onDutyThursdayStartInput = document.querySelector('#onDutyThursdayStartInput');
const onDutyThursdayEndInput = document.querySelector('#onDutyThursdayEndInput');
const onDutyFridayStartInput = document.querySelector('#onDutyFridayStartInput');
const onDutyFridayEndInput = document.querySelector('#onDutyFridayEndInput');
const onDutySaturdayStartInput = document.querySelector('#onDutySaturdayStartInput');
const onDutySaturdayEndInput = document.querySelector('#onDutySaturdayEndInput');
const onDutySundayStartInput = document.querySelector('#onDutySundayStartInput');
const onDutySundayEndInput = document.querySelector('#onDutySundayEndInput');

const onDutyInput = document.querySelector('#onDutyInput');
const submitUpdateProfileForm = () => {
  formInputs.forEach((el) => {
    el.value = el.value.trim();
  });

  if (!onDutyGeneralInputGroup.classList.contains('d-none'))
    onDutyInput.value = `${onDutyGeneralInputs[0].value}-${onDutyGeneralInputs[1].value},${onDutyGeneralInputs[0].value}-${onDutyGeneralInputs[1].value},${onDutyGeneralInputs[0].value}-${onDutyGeneralInputs[1].value},${onDutyGeneralInputs[0].value}-${onDutyGeneralInputs[1].value},${onDutyGeneralInputs[0].value}-${onDutyGeneralInputs[1].value},${onDutyGeneralInputs[0].value}-${onDutyGeneralInputs[1].value},${onDutyGeneralInputs[0].value}-${onDutyGeneralInputs[1].value}`;
  else
    onDutyInput.value = `${onDutyMondayStartInput.value}-${onDutyMondayEndInput.value},${onDutyTuesdayStartInput.value}-${onDutyTuesdayEndInput.value},${onDutyWednesdayStartInput.value}-${onDutyWednesdayEndInput.value},${onDutyThursdayStartInput.value}-${onDutyThursdayEndInput.value},${onDutyFridayStartInput.value}-${onDutyFridayEndInput.value},${onDutySaturdayStartInput.value}-${onDutySaturdayEndInput.value},${onDutySundayStartInput.value}-${onDutySundayEndInput.value}`;

  const wardInput = document.querySelector('#wardInput');
  wardInput.value = wardInput.value.includes(',')
    ? wardInput.value.split(',').map((ward) => ward.trim()).join(',')
    : wardInput.value.trim();

  const departmentInput = document.querySelector('#departmentInput');
  departmentInput.value = departmentInput.value.includes(',')
    ? departmentInput.value.split(',').map((department) => department.trim()).join(',')
    : departmentInput.value.trim();

  updateProfileForm.submit();
};


