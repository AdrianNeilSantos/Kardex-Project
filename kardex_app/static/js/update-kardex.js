/* global bootstrap */

const updateKardexForm = document.querySelector('#updateKardexForm');
const nameOfWardInput = document.querySelector('#nameOfWardInput');
const ivfInput = document.querySelector('#ivfInput');
const laboratoryWorkUps = document.querySelector('#laboratoryWorkUpsInput');
const medicationsInput = document.querySelector('#medicationsInput');
const sideDripInput = document.querySelector('#sideDripInput');
const specialNotationsInput = document.querySelector('#specialNotationsInput');
const referralsInput = document.querySelector('#referralsInput');

const firstNameInput = document.querySelector('#firstNameInput');
firstNameInput.addEventListener('keyup', (e) => e.target.value = e.target.value.replace(/\s{2}/g, ' '));

const lastNameInput = document.querySelector('#lastNameInput');
lastNameInput.addEventListener('keyup', (e) => e.target.value = e.target.value.replace(/\s{2}/g, ' '));

const ageSexInput = document.querySelector('#ageSexInput');
const dateTimeInput = document.querySelector('#dateTimeInput');
const hospitalNumInput = document.querySelector('#hospitalNumInput');
const dxInput = document.querySelector('#dxInput');
const drsInput = document.querySelector('#drsInput');
const dietInput = document.querySelector('#dietInput');

const ageInput = document.querySelector('#ageInput');
const sexInput = document.querySelector('#sexInput');

const updateKardexBtn = document.querySelector('#updateKardexBtn');

const suggestionBtns = document.querySelectorAll('.suggestion-btn');
const handleSuggestionBtns = (extraFieldNames) => {
  const suggestionBtnArr = suggestionBtns;
  suggestionBtnArr.forEach((btn) => {
    const btnText = btn.textContent.trim();
    if (extraFieldNames.includes(btnText)) {
      btn.classList.add('btn-success');
      btn.classList.remove('btn-outline-dark');
    } else {
      btn.classList.add('btn-outline-dark');
      btn.classList.remove('btn-success');
    }
  });
};

const versionModals = Array.from(document.querySelectorAll('[id^="comparisonModal"]'));
const closeModal = (e) => {
  const closedModal = e.target;

  const closedModalBody = closedModal.querySelector('.modal-body');
  closedModalBody.querySelector('#modalContainerCurr')
    && closedModalBody.querySelector('#modalContainerCurr').remove();
  closedModalBody.querySelector('#modalContainerPrev')
    && closedModalBody.querySelector('#modalContainerPrev').remove();
  
  Array.from(closedModal
    .querySelector('[id^="modalContainer"]')
    .querySelectorAll('.change-span'))
    .forEach((el) => el.classList.add('d-none'));
};
versionModals
  .forEach((el) => el.addEventListener('hidden.bs.modal', closeModal));

const compareCurrLinks = document.querySelectorAll('[id^="compareCurr"][id$="Link"]');
const compareWCurr = (idx) => {
  const versionModal = versionModals[idx - 1];

  const currVersionModalContainer = versionModal
    .querySelector('[id^="modalContainer"]').cloneNode(true);
  currVersionModalContainer.id = 'modalContainerCurr';

  const currVersionTitle = currVersionModalContainer.querySelector('[id^="modalCardTitle"]');
  currVersionTitle.id = 'modalCardTitleCurr';
  currVersionTitle.getElementsByTagName('span')[0].textContent = firstNameInput.value.trim();
  currVersionTitle.getElementsByTagName('span')[1].textContent = '(Your Current Version)';

  const currVersionBody = currVersionModalContainer.querySelector('[id^="modalCardBody"]');
  currVersionBody.id = 'modalCardBodyCurr';

  const currNameOfWard = currVersionBody.querySelector('[id^="nameOfWard"]');
  currNameOfWard.id = 'nameOfWardCurr';
  currNameOfWard.getElementsByTagName('span')[1].textContent = nameOfWardInput.value.trim();

  const currIvf = currVersionBody.querySelector('[id^="ivf"]');
  currIvf.id = 'ivfCurr';
  currIvf.getElementsByTagName('span')[1].textContent = ivfInput.value.trim();

  const currLaboratoryWorkUps = currVersionBody.querySelector('[id^="laboratoryWorkUps"]');
  currLaboratoryWorkUps.id = 'laboratoryWorkUpsCurr';
  currLaboratoryWorkUps.getElementsByTagName('span')[1].textContent = laboratoryWorkUps.value.trim();

  const currMedications = currVersionBody.querySelector('[id^="medications"]');
  currMedications.id = 'medicationsCurr';
  currMedications.getElementsByTagName('span')[1].textContent = medicationsInput.value.trim();

  const currSideDrip = currVersionBody.querySelector('[id^="sideDrip"]');
  currSideDrip.id = 'sideDripCurr';
  currSideDrip.getElementsByTagName('span')[1].textContent = sideDripInput.value.trim();

  const currSpecialNotations = currVersionBody.querySelector('[id^="specialNotations"]');
  currSpecialNotations.id = 'specialNotationsCurr';
  currSpecialNotations.getElementsByTagName('span')[1].textContent = specialNotationsInput.value.trim();

  const currReferrals = currVersionBody.querySelector('[id^="referrals"]');
  currReferrals.id = 'referralsCurr';
  currReferrals.getElementsByTagName('span')[1].textContent = referralsInput.value.trim();

  const currFirstName = currVersionBody.querySelector('[id^="firstName"]:not([id^="nameOfWard"]');
  currFirstName.id = 'firstNameCurr';
  currFirstName.getElementsByTagName('span')[1].textContent = firstNameInput.value.trim();

  const currLastName = currVersionBody.querySelector('[id^="lastName"]:not([id^="nameOfWard"]');
  currLastName.id = 'lastNameCurr';
  currLastName.getElementsByTagName('span')[1].textContent = lastNameInput.value.trim();

  const currAgeSex = currVersionBody.querySelector('[id^="ageSex"]');
  currAgeSex.id = 'ageSexCurr';
  currAgeSex.getElementsByTagName('span')[1].textContent = ageSexInput.value.trim();

  const currDateTime = currVersionBody.querySelector('[id^="dateTime"]');
  currDateTime.id = 'dateTimeCurr';
  currDateTime.getElementsByTagName('span')[1].textContent = dateTimeInput.value.trim();

  const currHospitalNum = currVersionBody.querySelector('[id^="hospital#"]');
  currHospitalNum.id = 'hospitalNumCurr';
  currHospitalNum.getElementsByTagName('span')[1].textContent = hospitalNumInput.value.trim();

  const currDx = currVersionBody.querySelector('[id^="dx"]');
  currDx.id = 'dxCurr';
  currDx.getElementsByTagName('span')[1].textContent = dxInput.value.trim();

  const currDrs = currVersionBody.querySelector('[id^="drs"]');
  currDrs.id = 'drsCurr';
  currDrs.getElementsByTagName('span')[1].textContent = drsInput.value.trim();

  const currDiet = currVersionBody.querySelector('[id^="diet"]');
  currDiet.id = 'dietCurr';
  currDiet.getElementsByTagName('span')[1].textContent = dietInput.value.trim();

  versionModal
    .querySelector('.modal-body')
    .appendChild(currVersionModalContainer);
  const activatedVersionModal = new bootstrap.Modal(versionModal);
  activatedVersionModal.show();
};
compareCurrLinks.forEach((el) => {
  el.addEventListener('click', (e) => compareWCurr(e.target.id.replace(/\D/g, '')));
});

const comparePrevLinks = document.querySelectorAll('[id^="comparePrev"][id$="Link"]');
const compareWPrev = (idx) => {
  if (idx == versionModals.length)
    return;

  const targetModal = versionModals[idx - 1];
  Array.from(targetModal
    .querySelector('[id^="modalContainer"]')
    .querySelectorAll('.change-span'))
    .forEach((el) => el.classList.remove('d-none'));
  
  const prevModal = versionModals[idx];
  const prevVersionModalContainer = prevModal
    .querySelector('[id^="modalContainer"]').cloneNode(true);
  prevVersionModalContainer.id = 'modalContainerPrev';

  targetModal
    .querySelector('.modal-body')
    .insertBefore(prevVersionModalContainer, targetModal.querySelector('[id^="modalContainer"]'));
  const activatedVersionModal = new bootstrap.Modal(targetModal);
  activatedVersionModal.show();
};
comparePrevLinks.forEach((el) => {
  el.addEventListener('click', (e) => compareWPrev(e.target.id.replace(/\D/g, '')));
});

const newFieldNameInput = document.querySelector('#newFieldNameInput');
const newFieldValueInput = document.querySelector('#newFieldValueInput');
const editExtraFields = () => {
  const filledExtraFieldNameInputs = Array.from(document.querySelectorAll('[id^="extraFieldNameInput"]'))
    .concat(newFieldNameInput)
    .filter((el) => el.value.trim() !== '');
  const extraFieldNames = filledExtraFieldNameInputs.map((el) => el.value.trim());

  const filledExtraFieldNameInputsIdx = filledExtraFieldNameInputs.map((el) => el.id.slice(-1));
  const extraFieldValueInputs = Array.from(document.querySelectorAll('[id^="extraFieldValueInput"]'))
    .concat(newFieldValueInput)
    .filter((el) => filledExtraFieldNameInputsIdx.includes(el.id.slice(-1)));
  const extraFieldValues = extraFieldValueInputs.map((el) => el.value.trim());

  const extraFieldsInput = document.querySelector('#extraFieldsInput');  
  extraFieldsInput.value = extraFieldNames.join(';;');

  const extraFieldValuesInput = document.querySelector('#extraFieldValuesInput');
  extraFieldValuesInput.value = extraFieldValues.join(';;');

  console.log(extraFieldsInput.value);
  console.log(extraFieldValuesInput.value);

  handleSuggestionBtns(extraFieldNames);
};
editExtraFields();
newFieldNameInput.addEventListener('keyup', editExtraFields);
newFieldValueInput.addEventListener('keyup', editExtraFields);

document.querySelectorAll('[id^="extraFieldNameInput"]')
  .forEach((el) => el.addEventListener('keyup', editExtraFields));
document.querySelectorAll('[id^="extraFieldValueInput"]')
  .forEach((el) => el.addEventListener('keyup', editExtraFields));

const extraFieldsDiv = document.querySelector('.extra-fields');
const removeExtraField = (e) => {
  const removeFieldBtnPart = e.target;
  const extraFieldToRemove = removeFieldBtnPart.closest('.extra-field');
  extraFieldsDiv.removeChild(extraFieldToRemove);

  // to fix ids of remaining extra fields and removal buttons upon removal of one
  const currExtraFields = document.querySelectorAll('.extra-field');
  currExtraFields.forEach((el, i) => {
    el.querySelector('[id^="extraFieldNameInput"]').id = `extraFieldNameInput${i + 1}`;
    el.querySelector('[id^="extraFieldValueInput"]').id = `extraFieldValueInput${i + 1}`;
    el.querySelector('[id^="removeFieldBtn"]').id = `removeFieldBtn${i + 1}`;
  });

  editExtraFields();
};
document.querySelectorAll('[id^="removeFieldBtn"]')
  .forEach((el) => el.addEventListener('click', removeExtraField));

const addFieldBtn = document.querySelector('#addFieldBtn');
const addField = (fieldName = '') => {
  const currExtraFields = document.querySelectorAll('.extra-field');

  const extraFieldNameInput = document.querySelector('#newFieldNameInput').cloneNode(true);
  extraFieldNameInput.id = `extraFieldNameInput${currExtraFields.length + 1}`;
  extraFieldNameInput.classList.add('underline-field', 'w-156', 'form-control');
  extraFieldNameInput.value = fieldName;
  extraFieldNameInput.addEventListener('keyup', editExtraFields);

  const extraFieldValueInput = document.querySelector('#newFieldValueInput').cloneNode(true);
  extraFieldValueInput.id = `extraFieldValueInput${currExtraFields.length + 1}`;
  extraFieldValueInput.classList.add('underline-field', 'form-control');
  extraFieldValueInput.value = '';
  extraFieldValueInput.addEventListener('keyup', editExtraFields);

  const colonSpan = document.createElement('span');
  colonSpan.classList.add('fs-2', 'fw-bold', 'me-3');
  colonSpan.textContent = ':';

  const removeBtnIcon = document.createElement('i');
  removeBtnIcon.classList.add('text-danger', 'fa-solid', 'fa-xmark');

  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.id = `removeFieldBtn${currExtraFields.length + 1}`;
  removeBtn.classList.add('btn', 'btn-outline-danger', 'ms-3');
  removeBtn.appendChild(removeBtnIcon);
  removeBtn.addEventListener('click', removeExtraField);

  const containerDiv = document.createElement('div');
  containerDiv.classList.add('extra-field', 'd-flex', 'align-items-center', 'mb-3', 'pe-0', 'pe-md-4');

  containerDiv.appendChild(extraFieldNameInput);
  containerDiv.appendChild(colonSpan);
  containerDiv.appendChild(extraFieldValueInput);
  containerDiv.appendChild(removeBtn);

  const addFieldDiv = document.querySelector('.add-field');
  extraFieldsDiv.insertBefore(containerDiv, addFieldDiv);

  editExtraFields();
};
addFieldBtn.addEventListener('click', () => addField());
suggestionBtns.forEach(el => {
  el.addEventListener('click', () => addField(el.textContent.trim()));
});

const checkSubmitEligibility = () => {
  const errors = [];

  const firstName = firstNameInput.value;
  !firstName.length
    && errors.push('FIRST NAME is required. Please enter the patient\'s name.');

  !/^[a-z ]+$/i.test(firstName)
    && errors.push('FIRST NAME must only contain letters and spaces.');

  const lastName = lastNameInput.value;
  !lastName.length
    && errors.push('LAST NAME is required. Please enter the patient\'s name.');
  
  !/^[a-z ]+$/i.test(lastName)
    && errors.push('LAST NAME must only contain letters and spaces.');

  const ageSex = ageSexInput.value;
  ageSex.length && !/^[0-9]+\/[a-zA-Z]+$/.test(ageSex)
    && errors.push('AGE/SEX should follow the format "age/sex", where age is a number from 0 to 125 and sex is e.g., Male, Female');
  
  const dateTime = dateTimeInput.value;
  dateTime.length && !/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}$/.test(dateTime)
    && errors.push('DATE/TIME should follow the format "YYYY-MM-DDTHH:MM", where YYYY is a year from 1900 to 2100, MM is a month from 01 to 12, DD is a day from 01 to 31, HH is an hour from 00 to 23, and MM is a minute from 00 to 59');

  const extraFieldNameInputs = Array.from(document.querySelectorAll('[id^="extraFieldNameInput"]'))
    .concat(newFieldNameInput);
  const extraFieldValueInputs = Array.from(document.querySelectorAll('[id^="extraFieldValueInput"]'))
    .concat(newFieldValueInput);

  for (let i = 0; i < extraFieldNameInputs.length; i++) {
    if (extraFieldValueInputs[i].value.length && !extraFieldNameInputs[i].value.length) {
      errors.push('All extra fields with a corresponding value must have a name. Check if there exists an input with a placeholder "New Field Name" where there is a value on the right-hand side and either fill them or remove them.');
      break;
    }
  }

  for (let i = 0; i < extraFieldNameInputs.length; i++) {
    if (extraFieldNameInputs[i].value.includes(';;')) {
      errors.push('";;" is not allowed in extra field names. Please remove it/them from the extra field names.');
      break;
    }
  }

  // filter(name => name) removes empty elements
  const extraFieldNames = extraFieldNameInputs.map(el => el.value);
  new Set(extraFieldNames.filter(name => name)).size !== extraFieldNames.filter(name => name).length
    && errors.push('Duplicate extra field names are not allowed. Please check if there are any duplicate and either edit them or remove them.');

  for (let i = 0; i < extraFieldValueInputs.length; i++) {
    if (extraFieldValueInputs[i].value.includes(';;')) {
      errors.push('";;" is not allowed in extra field values. Please remove it/them from the extra field values.');
      break;
    }
  }

  !errors.length
    ? submitUpdateKardexForm()
    : displayErrors(errors);
};
updateKardexBtn.addEventListener('click', checkSubmitEligibility);

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

const editedByInput = document.querySelector('#editedByInput');
const editedAtInput = document.querySelector('#editedAtInput');
const userIdSpan = document.querySelector('#userIdSpan');
const submitUpdateKardexForm = () => {
  const formInputs = document.querySelectorAll('#updateKardexForm .form-control');
  formInputs.forEach((el) => {
    el.value = el.value.trim();
  });

  // +00:00 is required as ArrayField incorrectly offsets datetime
  editedByInput.value += userIdSpan.textContent.trim();
  editedAtInput.value += new Date().toISOString().split(':').slice(0, -1).join(':') + '+00:00';

  const age = Number(ageSexInput.value.split('/')[0]);
  ageInput.value = age;

  const sex = ageSexInput.value.split('/')[1];
  sexInput.value = sex;

  updateKardexForm.submit();
};
