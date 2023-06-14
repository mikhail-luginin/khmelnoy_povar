function run_datatable(table_id, ajax_url, url, ajax_columns,
                       has_delete = true, has_update = false,
                       has_dismiss = false, has_edit = true, has_actions = true, custom_dict = {}, order_id = 0) {
    let datatable_dict = {
        language: {
            "url": "//cdn.datatables.net/plug-ins/1.11.1/i18n/ru.json"
        },
        lengthMenu: [10, 25, 50, 100, 200, 500],
        pageLength: 25,
        responsive: true,

        ajax: {
            url: ajax_url,
            dataSrc: ''
        },
        columns: ajax_columns,
        deferRender: true,
        "order": [[order_id, "desc"]],
        footerCallback: function (row, data, start, end, display) {
            var api = this.api();
            var total = [];
            for (var i = 0; i < api.columns().count(); i++) {
                pageTotal = api.column(i, {page: 'current'}).data().reduce(function (a, b) {
                    return (parseFloat(a) || 0) + (parseFloat(b) || 0);
                }, 0);
                total[i] = pageTotal;
            }
            // Update footer with totals for relevant columns
            $(api.columns().footer()).html(function (index) {
                return total[index];
            });
        }


    }
    if (has_actions === true) {
        datatable_dict['columns'] = ajax_columns.concat([
            {
                "data": null,
                render: function (data, type, row) {
                    let actions = ''
                    if (has_edit === true) {
                        actions += '<a href="' + url + '/edit?id=' + row.id + '"><i class="fa fa-edit"></i></a>'
                    }
                    if (has_delete === true) {
                        actions += '<a href="#" onclick="delete_confirm(' + '\'' + row.id + '\'' + ', ' + '\'Вы действительно хотите удалить данную запись?\'' + ', ' + '\'' + url + '/delete' + '\'' + ')"><i class="fa fa-trash"></i></a>'
                    }
                    if (has_update === true) {
                        actions += '<a href="' + url + '/update?id=' + row.id + '"><i class="fa fa-cloud-upload"></i></a>'
                    }
                    if (has_dismiss === true) {
                        if (row.active_status === 'Активный') {
                            actions += '<a href="#" onclick="delete_confirm(' + '\'' + row.id + '\'' + ', ' + '\'Вы действительно хотите уволить ' + row.fio + '?\'' + ', ' + '\'' + url + '/dismiss' + '\'' + ', ' + '\'' + 'Уволить' + '\'' + ')"><i class="fa fa-user-minus"></i></a>'
                        } else {
                            actions += '<a href="' + url + '/return?id=' + row.id + '"<i class="fa fa-user"></i</a>'
                        }
                    }
                    return actions
                }
            }
        ])
    }
    let table = $('#' + table_id).DataTable(Object.assign(datatable_dict, custom_dict))
    // Apply column filter
    $('#' + table_id + ' .dt-column-filter th').each(function (i) {
        $('input', this).on('keyup change', function () {
            if (table.column(i).search() !== this.value) {
                table
                    .column(i)
                    .search(this.value)
                    .draw()
            }
        })
    })
    // Toggle Column filter function
    var responsiveFilter = function (table, index, val) {
        var th = $(table).find('.dt-column-filter th').eq(index)
        val === true ? th.removeClass('d-none') : th.addClass('d-none')
    }
    // Run Toggle Column filter at first
    $.each(table.columns().responsiveHidden(), function (index, val) {
        responsiveFilter('#' + table_id, index, val)
    })
    // Run Toggle Column filter on responsive-resize event
    table.on('responsive-resize', function (e, datatable, columns) {
        $.each(columns, function (index, val) {
            responsiveFilter('#' + table_id, index, val)
        })
    })
    return table
}

function run_datatable_with_json(table_id, json, columns) {
    let datatable_dict = {
        language: {
            "url": "//cdn.datatables.net/plug-ins/1.11.1/i18n/ru.json"
        },
        lengthMenu: [10, 25, 50, 100, 200, 500],
        pageLength: 25,
        responsive: true,

        data: json,
        columns: columns,
        footerCallback: function (row, data, start, end, display) {
            var api = this.api();
            var total = [];
            for (var i = 0; i < api.columns().count(); i++) {
                pageTotal = api.column(i, {page: 'current'}).data().reduce(function (a, b) {
                    return (parseFloat(a) || 0) + (parseFloat(b) || 0);
                }, 0);
                total[i] = pageTotal;
            }
            // Update footer with totals for relevant columns
            $(api.columns().footer()).html(function (index) {
                return total[index];
            });
        }


    }
    let table = $('#' + table_id).DataTable(datatable_dict)
    // Apply column filter
    $('#' + table_id + ' .dt-column-filter th').each(function (i) {
        $('input', this).on('keyup change', function () {
            if (table.column(i).search() !== this.value) {
                table
                    .column(i)
                    .search(this.value)
                    .draw()
            }
        })
    })
    // Toggle Column filter function
    var responsiveFilter = function (table, index, val) {
        var th = $(table).find('.dt-column-filter th').eq(index)
        val === true ? th.removeClass('d-none') : th.addClass('d-none')
    }
    // Run Toggle Column filter at first
    $.each(table.columns().responsiveHidden(), function (index, val) {
        responsiveFilter('#' + table_id, index, val)
    })
    // Run Toggle Column filter on responsive-resize event
    table.on('responsive-resize', function (e, datatable, columns) {
        $.each(columns, function (index, val) {
            responsiveFilter('#' + table_id, index, val)
        })
    })
    return table
}
