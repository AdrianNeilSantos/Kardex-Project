const inputs = document.querySelectorAll('input');
const showInfoToast = () => {
  console.log('test');
  // const infoToast = document.querySelector('.info-toast');
  // new bootstrap.Toast(infoToast).show();
};
document.querySelectorAll('.form-control').forEach((el) => el.addEventListener('click', (e) => console.log(e.target)));
