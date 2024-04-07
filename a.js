run = true
function scrollToEndPage() {
    if(run){
    const el = document.documentElement;

    if (el.scrollTop < el.scrollHeight - el.clientHeight) {
        el.scrollTop = Math.ceil(el.scrollHeight - el.clientHeight);
    }}
}

setInterval(scrollToEndPage, 1000);


buttons = document.querySelectorAll('.btn-green.js_ajax-load')
const delay = ms => new Promise(res => setTimeout(res, ms));

(async () => {
    for (let i = 0; i < buttons.length; i++) {
        const button = buttons[i];
        button.click()
        await delay(3000);

        download_button = document.getElementById('btncsv').click()
        document.querySelector('.modal-backdrop.fade.in').remove()
        document.querySelector('.modal.fade.modalDownload.modal_ajax.in').remove()
    }
  })();
