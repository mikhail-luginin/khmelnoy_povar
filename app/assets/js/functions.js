function delete_confirm(id, message, url, btn_text=false) {
    confirm(message, btn_text).then(function (result) {
        if(result) {
            return window.location.href = url + '?id=' + id
        }
    })
}