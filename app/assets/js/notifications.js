window.confirm = (message, btn_text=false) => {
        var PromiseConfirm = $('#PromiseConfirm').modal({
            keyboard: false,
            backdrop: 'static'
        }).modal('show');
        let confirm = false;
        let confirm_button_selector = $('#confirm-delete1')
        if(btn_text !== false) {
            confirm_button_selector.html(btn_text)
        }
        confirm_button_selector.on('click', e => {
            confirm = true;
        });
        $('#confirm-text').html(message)
        return new Promise(function (resolve, reject) {
            PromiseConfirm.on('hidden.bs.modal', (e) => {
                resolve(confirm);
            });
        });
    };

function notification(success, text=null) {
    if(success === true) {
        if(text != null) {
            $('#notification-success-text').html(text)
        }
        return $('#notification-success').modal('show')
    } else {
        if(text != null) {
            $('#notification-error-text').html(text)
        }
        return $('#notification-error').modal('show')
    }
}
