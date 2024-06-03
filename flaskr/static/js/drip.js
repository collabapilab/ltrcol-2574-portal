function defect_table_array(table_id, data, showAttr=false) {

    var numColumns = showAttr ? 15 : 14;
    var hotListReasons = {}; // Used for tooltip generation
    var statusMap = {
        J: 'Junked',
        F: 'Forwarded',
        C: 'Closed',
        D: 'Duplicate',
        M: 'More',
        S: 'Submitted',
        N: 'New',
        O: 'Open',
        R: 'Resolved',
        V: 'Verified',
        P: 'Postoned',
        W: 'Waiting',
        I: 'Info_Req',
        H: 'Held',
        U: 'Unreproducable',
        A: 'Assigned'
    }
    // If table exists just clear the data and add the rows - much quicker than destroy.
    if ($.fn.DataTable.isDataTable('#' + table_id)) {
        $('#' + table_id).DataTable().clear();
        $('#' + table_id).DataTable().rows.add(data).draw();
    } else {
        // Otherwise we need to init a new Datatable.
        $('#' + table_id).DataTable({
            data: data,
            //destroy: true,
            //deferRender: true,
            orderCellsTop: true,
            ordering: true,
            order: [
                [2, 'desc']
            ],
            drawCallback: function () {
                document.getElementById("loader").style.display = "none";
            },
            rowCallback: function (row, data) {

                // Add tooltip with the hotlist reasons.
                if (hotListReasons[data.id].length > 0) {
                    $('td:eq(2)', row).attr('title', hotListReasons[data.id].join('\n'));
                }
            },
            columns: [{
                    title: "id",
                    name: "id",
                    data: "id",
                    render: function (data, type, row) {
                        if (type === 'display') {
                            cdets_web_url = "https://scripts.cisco.com/app/quicker_cdets/?bug=" + data
                            html = "<a href='" + cdets_web_url + "' target='_blank ' title='Open defect in Quicker CDETS'>" + data + "</a>"
                            return html;
                        }
                        return data;
                    }
                },
                {
                    title: "Submitter",
                    name: "Submitter",
                    data: "Submitter",
                    render: function (data, type, row) {
                        if (type === 'display') {
                            if (row.Submitted_SVS === 'Y') {
                                dir_web_url = "/submitter?id=" + data
                                html = "<a href='" + dir_web_url + "' target='_blank ' title='Go to " + data + "`s Submitter page'>" + data + "</a>"
                                return html;
                            } else {
                                return '<span title="Currently not in SVS">' + data + '</span>';
                            }
                        }
                        return data;
                    }
                },
                {
                    title: "Heat Map",
                    name: 'HeatMap',
                    data: null,
                    render: function (data, type, row) {
                        heatValue = 0;
                        reasons = [];

                        var cdets = row.id;
                        var status_age = row.Status_age;
                        var severity = row.Severity;
                        var status = row.Status;
                        var submitted = new Date(row.Submitted_date);
                        var srCount = row.TACSRcount;

                        if (severity >= 5 && severity <= 6) {
                            heatValue = 1;
                            reasons.push('Severity ' + severity);
                        } else if (severity >= 3 && severity <= 4) {
                            heatValue = 2;
                            reasons.push('Severity ' + severity);
                        } else if (severity >= 1 && severity <= 2) {
                            heatValue = 3;
                            reasons.push('Severity ' + severity);
                        }

                        var now = new Date()
                        var timeOpen = now.getTime() - submitted.getTime();
                        var daysOpen = timeOpen / (1000 * 3600 * 24);

                        if (status === 'N' && daysOpen >= 60 && severity >= 5 && severity <= 6) {
                            heatValue += 2;
                            reasons.push('New status with days open ' + parseInt(daysOpen));
                        }

                        /*
                        if (status === 'I') {
                            heatValue += 2;
                            reasons.push('Info state');
                        }
                        */



                        var inProcessStates = ['P', 'W', 'F', 'A', 'I', 'O', 'H'];

                        if (inProcessStates.indexOf(status) >= 0) {
                            if (srCount > 5 && srCount <= 9) {
                                heatValue += 3;
                                reasons.push('TAC SR Count ' + srCount);
                            } else if (srCount >= 10) {
                                heatValue = 6;
                                reasons.push('TAC SR Count ' + srCount);
                            }
                            if (daysOpen > 30 && daysOpen <= 60 && severity <= 4) {
                                heatValue += 1;
                                reasons.push('Days open ' + parseInt(daysOpen) + ' with severity ' + severity + ' and status ' + status);
                            } else if (daysOpen > 60 && daysOpen <= 90 && severity <= 4) {
                                heatValue += 2;
                                reasons.push('Days open ' + parseInt(daysOpen) + ' with severity ' + severity) + ' and status ' + status;
                            } else if (daysOpen > 90 && severity <= 4) {
                                heatValue += 3;
                                reasons.push('Days open ' + parseInt(daysOpen) + ' with severity ' + severity + ' and status ' + status);
                            }
                        }

                        // Calculate Heat Map for defects in I State
                        if (status === 'I') {
                            if (status_age > 30 && status_age <= 60) {
                                heatValue += 1;
                                reasons.push('I State age ' + parseInt(status_age));
                            } else if (status_age > 60 && status_age <= 90) {
                                heatValue += 2;
                                reasons.push('I State age ' + parseInt(status_age));
                            } else if (status_age > 90) {
                                heatValue += 3;
                                reasons.push('I State age ' + parseInt(status_age));
                            }

                        }

                        if (heatValue > 8) {
                            heatValue = 8;
                        }

                        hotListReasons[row.id] = reasons;
                        heat_bar_array = [
                            ['10', 'info'],
                            ['30', 'info'],
                            ['40', 'info'],
                            ['50', 'info'],
                            ['65', 'warning'],
                            ['80', 'warning'],
                            ['100', 'warning'],
                            ['100', 'danger'],
                            ['100', 'danger'],
                        ]
                        html = '<div class="progress" style="height:2.0em;"> '
                        html += '<div class="progress-bar bg-' + heat_bar_array[heatValue][1] + '" role="progressbar" style="font-size:2.0em; width: ' + heat_bar_array[heatValue][0] + '%" aria-valuenow="' + heat_bar_array[heatValue][0] + '" aria-valuemin="0" aria-valuemax="100">' + heatValue + '</div>'
                        html += '</div>'

                        if (type === 'display') {
                            return html;
                        }

                        return heatValue;

                    }
                },
                {
                    title: "Status",
                    name: "Status",
                    data: "Status",
                    render: function (data, type, row) {
                        if (type === 'display') {
                            var title = ' title="Unknown Attribute"';
                            if (statusMap.hasOwnProperty(data)) {
                                title = ' title="' + statusMap[data] + '"';
                            }
                            return '<span' + title + '>' + data + '</span>';
                        }
                        return data;
                    }
                },
                {
                    title: "Status Age",
                    name: "Status Age",
                    data: "Status_age"
                },
                {
                    title: "Sev",
                    name: "Sev",
                    data: "Severity"
                },
                {
                    title: "Pri",
                    name: "Pri",
                    data: "Priority"
                },
                {
                    title: "DE-Pri",
                    name: "DE-Pri",
                    data: "DE_Priority"
                },
                {
                    title: "TAC",
                    name: "TAC",
                    data: "Ticket_count"
                },
                {
                    title: "PSIRT",
                    name: "PSIRT",
                    data: "PSIRT"
                },
                {
                    title: "CAP",
                    name: "CAP",
                    data: "CAPLINK"
                },
                {
                    title: "Age",
                    name: "Age",
                    data: "Age"
                }, {
                    title: "Project",
                    data: "Project",
                    name: "Project",
                    className: 'text-left',
                    align: "left",
                    render: function (data, type, row) {
                        if (type === 'display') {
                            return "<span style='font-size:.8em;'>" + data + "</span>";
                        }
                        return data;
                    }
                },
                {
                    title: "Headline, Impact and Product",
                    data: "Project",
                    className: 'text-left',
                    render: function (data, type, row) {
                        if (type === 'display') {
                            html = "Headline:<span style='font-weight:600;'>" + row['Headline'] + "</span><br/>"
                            html += "Impact:" + row['Impact'] + "<br/>"
                            html += "Product:" + row['Product'] + "&nbsp;Component:" + row['Component']
                            return "<span style='font-size:.8em;'>" + html + "</span>";
                        }
                        return data;
                    }
                },
                {
                    title: "Attributes",
                    name: "Attribute",
                    data: "Attribute",
                    className: 'text-left',
                    visible: showAttr,
                    render: function (data, type, row) {
                        if (type === 'display') {
                            var attrs = data.split(' ');
                            var html = '';
                            var span = '';
                            var endSpan = '';
                            var re = /^(svs|ecats)\-(\w+)\-([A-Za-z]\d{5,6})\-{0,1}(oib|ts|ss|encountered|encountered-oib|encountered-ts|encountered-ss|seen|seen-oibseen-tsseen-ss)*$/i;

                            for (i=0; i<attrs.length; i++) {
                                var attr = attrs[i];
                                if (attr.toLowerCase().includes('svs') || attr.toLowerCase().includes('ecats')) {
                                    var valid = attr.match(re);
                                    if (valid) {
                                        span = "<span style='font-weight:600;'>";
                                    } else {
                                        span = "<span class='highlight' style='font-weight:600;'>";
                                    }
                                    
                                    endSpan = "</span>"
                                    html += span + attr + endSpan + "<br/>";
                                }
                            }
                            return "<span style='font-size:.8em;'>" + html + "</span>";
                        } else if (type === 'filter' || type === 'sort') {
                            return row.SVS_Attr_Valid.trim();
                        }
                        return data;
                    }
                },



            ],
            initComplete: function () {
                var th = '';
                var api = this.api();

                for (x = 0; x < numColumns; x++) {
                    th += '<th></th>';
                }

                // Remove all thead rows except first
                $('#' + table_id + ' thead').find("tr:gt(0)").remove()

                // Append blank thead row to first row.
                $('#' + table_id + ' > thead').append('<tr>' + th + '</tr>');

                drip_columns = ["Sev", "Pri", "Status", "PSIRT", "CAP", "IMPACT", "Project"]
                for (x = 0; x < drip_columns.length; x++) {
                    this.api().columns(drip_columns[x] + ":name").every(function () {
                        var column = this;
                        //$(column.header()).append("<br>")
                        var select = $('<select><option value="">' + drip_columns[x] + '</option></select>')
                            //.appendTo($(column.header()))
                            .appendTo($('#' + table_id + ' thead tr:eq(1) th').eq(column.index()).empty())
                            .on('change', function () {
                                var val = $.fn.dataTable.util.escapeRegex(
                                    $(this).val()
                                );
                                column
                                    .search(val ? '^' + val + '$' : '', true, false)
                                    .draw();
                            });
                        column.data().unique().sort().each(function (d, j) {
                            select.append('<option value="' + d + '">' + d + '</option>')
                        })
                    });
                }

                var attrColumn = api.column("Attribute:name");
                var select = $('<select><option value="">Valid</option></select>')
                    .appendTo($('#' + table_id + ' thead tr:eq(1) th').eq(attrColumn.index()).empty())
                    .on('change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );
                        attrColumn
                            .search(val ? '^' + val + '$' : '', true, false)
                            .draw();
                    });
                select.append('<option value="Y">Yes</option><option value="N">No</option>')
            

                // Build select list for heat map filter.
                var heatMapRange = [0, 1, 2, 3, 4, 5, 6, 7, 8];
                column = this.api().column('HeatMap:name');
                select = $('<select id="hotlist"><option value="">Heat Map</option></select>')
                    .appendTo($('#' + table_id + ' thead tr:eq(1) th').eq(column.index()).empty())
                    .on('change', function () {
                        hotlistSelector = $(this).val();
                        $('#' + table_id).DataTable().draw(false);
                    });

                $.each(heatMapRange, function (d, j) {

                    // If top end of range don't display >= just display =.
                    var gt = d != heatMapRange[heatMapRange.length - 1] ? '&gt;' : '';
                    select.append('<option value="' + d + '">Defects ' + gt + '= ' + d + '</option>')
                });

                $('.defect_table_select').select2({
                    //theme: "bootstrap4",  //Small text input with this option
                    allowClear: true,
                });

            }

        });
    }

}

function defect_table(table_id, data, showSubmitter = false) {

    $('#' + table_id).DataTable({
        destroy: true,
        paging: true,
        searching: true,
        info: true,
        scrollX: false,
        responsive: true,
        ordering: true,
        iDisplayLength: 20,
        data: data,
        order: [
            [14, "desc"]
        ],
        columnDefs: [{
                targets: showSubmitter ? [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14] : [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14],
                visible: true
            },
            {
                targets: ['_all'],
                visible: false
            }
        ],
        columns: [{
                title: "ID",
                data: 'id'
            },
            {
                title: "Submitter",
                data: 'Submitter'
            },
            {
                title: "State",
                data: 'Status'
            },
            {
                title: "Priority",
                data: 'Priority'
            },
            {
                title: "Severity",
                data: 'Severity'
            },
            {
                title: "TACSRcount",
                data: 'TACSRcount'
            },
            {
                title: "Found",
                data: 'Found'
            },
            {
                title: "DE Mgr",
                data: 'DE_Manager'
            },
            {
                title: "Age",
                data: 'Age'
            },
            {
                title: "Component",
                data: 'Component'
            },
            {
                title: "Product",
                data: 'Product'
            },
            {
                title: "Project",
                data: 'Project'
            },
            {
                title: "Headline",
                data: 'Headline'
            },
            {
                title: "Attribute",
                data: 'Attribute'
            },
            {
                title: "Submit Date",
                data: 'Submitted_date'
            }
        ]
    });
}




function attr_table(table_id, data) {
    //console.log(data)
    $('#' + table_id).DataTable({
        destroy: true,
        paging: true,
        searching: true,
        info: true,
        scrollX: false,
        deferRender: true,
        //responsive: true,
        ordering: true,
        iDisplayLength: 20,
        data: data,
        order: [
            [14, "desc"]
        ],
        columnDefs: [{
                targets: [0, 1, 2, 3],
                visible: true
            },
            {
                targets: ['_all'],
                visible: false
            }
        ],
        columns: [{
                title: "ID",
                data: 'id',
                render: function (data, type, row) {
                    if (type === 'display') {
                        cdets_web_url = "https://scripts.cisco.com/app/quicker_cdets/?bug=" + data
                        html = "<a href='" + cdets_web_url + "' target='_blank '>" + data + "</a>"
                        return html;
                    }
                    return data;
                }
        },
            {
                title: "Submitter",
                data: 'Submitter',
                render: function (data, type, row) {
                    if (type === 'display') {
                        dir_web_url = "/submitter?id=" + data
                        html = "<a href='" + dir_web_url + "' target='_blank '>" + data + "</a>"
                        return html;
                    }
                    return data;
                }
        },
            {
                title: "State",
                data: 'Status'
            },
            {
                title: "Attribute",
                data: 'Attribute',
                className: 'dt-left dt-wrap',
                render: function (data, type, row) {
                    var hilite = data.replace(/svs/g,"<span class='highlight'>svs</span>");
                    hilite = hilite.replace(/SVS/g,"<span class='highlight'>SVS</span>");
                    hilite = hilite.replace(/ecats/g,"<span class='highlight'>ecats</span>");
                    hilite = hilite.replace(/ECATS/g,"<span class='highlight'>ECATS</span>");
                    return hilite;
                }
            },
            {
                title: "Priority",
                data: 'Priority'
            },
            {
                title: "Severity",
                data: 'Severity'
            },
            {
                title: "TACSRcount",
                data: 'TACSRcount'
            },
            {
                title: "Found",
                data: 'Found'
            },
            {
                title: "DE Mgr",
                data: 'DE_Manager'
            },
            {
                title: "Age",
                data: 'Age'
            },
            {
                title: "Component",
                data: 'Component'
            },
            {
                title: "Product",
                data: 'Product'
            },
            {
                title: "Project",
                data: 'Project'
            },
            {
                title: "Headline",
                data: 'Headline'
            },
            {
                title: "Submit Date",
                data: 'Submitted_date'
            }
        ]
    });
}

function product_series_bar_chart(canvas_id, data, labels) {
    //This cart is going to make a stackable BAR chart of the 
    // data related to the top 3 products on a per month basis 
}

function single_series_line_chart(canvas_id, data, labels) {
    // Clear previous chart
    $("canvas#" + canvas_id).remove();
    $("div." + canvas_id)
        .append('<canvas id="' + canvas_id + '"></canvas>')
        .append('<div id="' + canvas_id + '-cisco"></div>');
    document.getElementById(canvas_id + '-cisco').innerHTML = 'Cisco Confidential';

    var ctx = document.getElementById(canvas_id).getContext("2d");
    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderColor: "#005073",
                fill: false,
                datalabels: {
                    align: 'top',
                    clamp: false,
                    offset: 5,
                    anchor: 'end',
                    color: "#005073",
                    rotation: 0
                }
            }]
        },
        options: {
            layout: {   // Keep the right side from cutting off the edge of page.
                padding: {
                    right: 10
                }
            },
            plugins: {
                datalabels: {
                    display: true,
                },
                labels: false
            },
            title: {
                display: false,
            },
            legend: {
                display: false,
            },
            scales: {
                xAxes: [{
                    stacked: true,
                    ticks: {
                        autoSkip: false,
                        maxRotation: 90,
                        minRotation: 90

                    },
                    gridLines: {
                        display: false,
                    },
                }],
                yAxes: [{
                    gridLines: {
                        display: false,
                    },
                }]
            },
        }
    });
}

function multi_series_line_chart(canvas_id, data, labels) {
    // Clear previous chart
    $("canvas#" + canvas_id).remove();
    $("div." + canvas_id)
        .append('<canvas id="' + canvas_id + '"></canvas>')
        .append('<div id="' + canvas_id + '-cisco"></div>');
    document.getElementById(canvas_id + '-cisco').innerHTML = 'Cisco Confidential';

    var colors = ["#005073", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#3e95cd"]
    var datasets = [];
    var count = 0;   // Used to grab next color

    // Build datasets
    for (label in data) {

        datasets.push({
                data: data[label],
                label: label,
                borderColor: colors[count],
                fill: false,
                datalabels: {
                    align: 'top',
                    clamp: false,
                    offset: 5,
                    anchor: 'end',
                    color: colors[count],
                    rotation: 0
                }
            })
        count++;
    }

    var ctx = document.getElementById(canvas_id).getContext("2d");
    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            layout: {   // Keep the right side from cutting off the edge of page.
                padding: {
                    right: 10
                }
            },
            plugins: {
                datalabels: {
                    //display: true,
                    display: function (context) {
                        return context.chart.isDatasetVisible(context.datasetIndex);
                    }                },
                labels: false
            },
            title: {
                display: false,
            },
            legend: {
                //display: false,
            },
            scales: {
                xAxes: [{
                    stacked: true,
                    ticks: {
                        autoSkip: false,
                        maxRotation: 90,
                        minRotation: 90

                    },
                    gridLines: {
                        display: false,
                    },
                }],
                yAxes: [{
                    gridLines: {
                        display: false,
                    },
                }]
            },
        }
    });
}


function single_series_bar_chart(canvas_id, data, labels) {
    // This color sequence is just an array that has different hex 
    // color values. 
    color_sequence = palette('tol-rainbow', data.length).map(function (hex) {
        return '#' + hex;
    })

    max = Math.max.apply(Math, data)

    // Clear previous chart
    $("canvas#" + canvas_id).remove();
    $("div." + canvas_id)
        .append('<canvas id="' + canvas_id + '"></canvas>')
        .append('<div id="' + canvas_id + '-cisco"></div>');
    document.getElementById(canvas_id + '-cisco').innerHTML = 'Cisco Confidential';

    var ctx = document.getElementById(canvas_id).getContext("2d");
    var myLineChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: color_sequence,
                fill: false,
                datalabels: {
                    align: 'end',
                    clamp: false,
                    offset: 5,
                    rotation: 270,
                    anchor: 'end',
                    color: "#696969",
                    rotation: 270
                }
            }]
        },
        options: {
            plugins: {
                datalabels: {
                    display: true,
                },
                labels: false,
            },
            title: {
                display: false,
            },
            legend: {
                display: false,
            },
            scales: {
                xAxes: [{
                    stacked: true,
                    ticks: {
                        autoSkip: false,
                        maxRotation: 90,
                        minRotation: 90

                    },
                    gridLines: {
                        display: false,
                    },
                }],
                yAxes: [{
                    gridLines: {
                        display: false,
                    },
                    ticks: {
                        suggestedMax: max + 10,
                    }
                }]
            },
        }
    });
    
    var canvas = document.getElementById(canvas_id);
    canvas.onclick = function(evt) {

        var api = {
            top30customer: "/api/v1/globalstats/customer_top_product/",
            top30product: "/api/v1/globalstats/product_top_customer/",
            top30component: "/api/v1/globalstats/component_top_customer/"
        };

        var activePoint = myLineChart.getElementAtEvent(evt)[0];

        if (typeof activePoint !== 'undefined') {
            var data = activePoint._chart.data;
            var datasetIndex = activePoint._datasetIndex;
            var label = data.labels[activePoint._index];
            var value = data.datasets[datasetIndex].data[activePoint._index];
            //console.log(canvas_id, label, value);
            //$('#myModal').modal('show');

            // Get manager, submitter or customer
            var modalLabel = getModalLabe();
            $('#myModalLabel').html('<span>' + modalLabel + ' defect count: ' + label + ': ' + value + '</span>')
            $('#myModal').modal( {keyboard: true} );
            $("#myModal").appendTo("body");
            $('#modal-text').html('Searching...');
            $.getJSON(api[canvas_id] + label + "/5/limit/5", function (json) {
                pairs = [];

                for (i=0; i<json.length; i++) {
                    data = json[i];
                    var cust = data[0].length > 0 ? data[0] : 'Unknown';
                    var dir_web_url = "/customer?id=" + cust;

                    pairs.push(("<a href='" + dir_web_url + "' target='_blank '>" + cust + "</a>") + ': ' + data[1])
                }

                $('#modal-text').html('Overall Top 5 Customers:</br>' + pairs.join('</br>'));
            });
               
            
        }
    };

}

function validString(data) {
    return typeof data !== 'undefined' ? data : '';
}

function getModalLabe() {
    var modalLabel = validString($('#manager_select_picker').val());
    modalLabel += validString($('#submitter_select_picker').val());
    modalLabel += validString($('#customer_select_picker').val());

    return modalLabel;
}

function state_pie_chart(div_id, data, labels) {
    color_sequence = palette('tol-rainbow', data.length).map(function (hex) {
        return '#' + hex;
    })

    // Clear previous chart
    $("canvas#" + div_id).remove();
    $("div." + div_id)
        .append('<canvas id="' + div_id + '"></canvas>')
        .append('<div id="' + div_id + '-cisco"></div>');
    document.getElementById(div_id + '-cisco').innerHTML = 'Cisco Confidential';

    var chart = document.getElementById(div_id).getContext('2d');
    myPieChart = new Chart(chart, {
        type: 'pie',
        options: {
            responsive: true,
            legend: {
                display: true,
                position: "left",
                labels: {
                    fontSize: 14,
                    generateLabels: function (chart) {
                        var data = chart.data;
                        if (data.labels.length && data.datasets.length) {
                            return data.labels.map(function (label, i) {
                                var meta = chart.getDatasetMeta(0);
                                var ds = data.datasets[0];
                                var arc = meta.data[i];
                                var custom = arc && arc.custom || {};
                                var getValueAtIndexOrDefault = Chart.helpers
                                    .getValueAtIndexOrDefault;
                                var arcOpts = chart.options.elements.arc;
                                var fill = custom.backgroundColor ? custom.backgroundColor :
                                    getValueAtIndexOrDefault(ds.backgroundColor, i, arcOpts
                                        .backgroundColor);
                                var stroke = custom.borderColor ? custom.borderColor :
                                    getValueAtIndexOrDefault(ds.borderColor, i, arcOpts
                                        .borderColor);
                                var bw = custom.borderWidth ? custom.borderWidth :
                                    getValueAtIndexOrDefault(ds.borderWidth, i, arcOpts
                                        .borderWidth);

                                // We get the value of the current label
                                var value = chart.config.data.datasets[arc._datasetIndex].data[arc
                                    ._index];

                                return {
                                    text: label + " : " + value,
                                    fillStyle: fill,
                                    strokeStyle: stroke,
                                    lineWidth: bw,
                                    hidden: isNaN(ds.data[i]) || meta.data[i].hidden,
                                    index: i
                                };
                            });
                        } else {
                            return [];
                        }
                    }
                }

            },
            plugins: {
                datalabels: {
                    display: false,
                },
                labels: [{
                    render: function (args) {
                        return args.label + ":" + args.value
                    },
                    position: "outside",
                    arc: true,
                    fontColor: "#000"
                }, ],

            },
        },
        data: {
            labels: labels,
            datasets: [{
                backgroundColor: color_sequence,
                data: data,

            }]
        },
    });

}



function initialize_year_selector(defaultVal=5) {

    var defaultStr = ' (default)';

    var year_select_array = {
        "1": "1 year back" + (defaultVal == 1 ? defaultStr : ''),
        "2": "2 year back" + (defaultVal == 2 ? defaultStr : ''),
        "3": "3 year back" + (defaultVal == 3 ? defaultStr : ''),
        "4": "4 year back" + (defaultVal == 4 ? defaultStr : ''),
        "5": "5 year back" + (defaultVal == 5 ? defaultStr : ''),
    }

    $.each(year_select_array, function (key, value) {
        $('#year_selector')
            .append($("<option></option>")
                .attr("value", key)
                .text(value));
    });

    $('#year_selector').select2({
        //theme: "bootstrap4",  //Small text input with this option
        allowClear: true,
        placeholder: 'Select length of years',
    });

    $('#year_selector').select2('val', '5');
}

// Datatables search API to filter heat map.
function enable_hotlist_filter() {
    $.fn.dataTable.ext.search.push(
        function (settings, searchData, index, rowData, counter) {
            var hotlist = parseInt(searchData[2]) || 0;
            var hotlistSelector = $('#hotlist').val();

            // Initial table load nothing will be selected.
            if (typeof hotlistSelector === 'undefined') {
                hotlistSelector = 0;
            }

            // Display the row if heatmap value >= selected option.
            if (hotlist >= hotlistSelector) {
                return true;
            }

            // Otherwise don't display row.
            return false;
        }
    );
}


function stacked_bar_chart(div_id, dataset_data1, labels_data1, dataset_data2, labels_data2, x_labels, year) {
    color_sequence = palette('tol-rainbow', dataset_data1.length).map(function (hex) {
        return '#' + hex;
    });

    color_sequence2 = palette('tol-rainbow', dataset_data1.length).reverse().map(function (hex) {
        return '#' + hex;
    });

    fontSizeDataLabels = [
        0, 20, 18, 16, 14, 10
    ]

    var chart = document.getElementById(div_id).getContext('2d');
    stackedBarChart = new Chart(chart, {
        type: 'bar',
        data: {
            labels: x_labels,
            datasets: [{
                    //label: labels_data1,
                    data: dataset_data1,
                    backgroundColor: '#fbab18',
                    datalabels: {
                        align: 'end',
                        anchor: 'start'
                    },
                    label: labels_data1,
                },
                {
                    //label: labels_data2,
                    data: dataset_data2,
                    backgroundColor: '#6abf4b',
                    datalabels: {
                        align: 'end',
                        anchor: 'start'
                    },
                    label: labels_data2,
                }
            ],
        },
        options: {
            defaultFontFamily: "Latoight",
            tooltips: {
                callbacks: {
                    title: function (tooltipItem, data) {
                        return data.datasets[tooltipItem[0]['datasetIndex']].label[tooltipItem[0]['index']]
                    },
                    label: function (tooltipItem, data) {
                        return data.datasets[tooltipItem['datasetIndex']].data[tooltipItem['index']] + " Defects";
                    },
                },
                enabled: true
            },
            hover: {
                mode: null
            },
            plugins: {
                datalabels: {
                    color: "#333",
                    rotation: 270,
                    font: {
                        family: "LatoLight",
                        size: fontSizeDataLabels[year],
                    },
                    formatter: function (value, context) {
                        //console.log(context)
                        prod_label = context.dataset.label[context.dataIndex] + ":" + context.dataset.data[context.dataIndex]
                        return prod_label;
                    }
                },
                labels: false,
            },
            legend: {
                display: false,
            },
            scales: {
                xAxes: [{
                    stacked: true,
                    ticks: {
                        fontFamily: "LatoLight",
                        autoSkip: false,
                        maxRotation: 90,
                        minRotation: 90
                    }
                }],
                yAxes: [{
                    stacked: true
                }]
            }
        }
    });
}