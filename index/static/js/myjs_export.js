/*
导出execl操作js将放在这儿
 */


//版本列表的button绑定
$($("#export_by_time input[type='button']").off("click").on("click", function () {
    var start_time = $('#datepicker').val();
    var end_time = $('#datepicker2').val();
    window.location.href='/GenExcelFile?type_name=banbenfabu_list' + '&&start_time=' + start_time + '&&end_time=' + end_time;

}));



