function delete_confirm(id, message, url) {
    confirm(message).then(function (result) {
        if(result) {
            return window.location.href = url + '?id=' + id
        }
    })
}