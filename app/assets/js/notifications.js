window.confirm = (message) => {
        var PromiseConfirm = $('#PromiseConfirm').modal({
            keyboard: false,
            backdrop: 'static'
        }).modal('show');
        let confirm = false;
        $('#confirm-delete1').on('click', e => {
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
