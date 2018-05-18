/*
所有服务操作js将放在这儿
 */


$(function () {
    var all_service_info = new Array()
    $(".col-sm-4 .h4").each(function () {
        all_service_info.push($(this).text());

    });
    $.post("/service_status/", {"all_service_info":JSON.stringify(all_service_info)}, function (result) {
        var new_result = result.replace("[", "").replace("]","");
        var status_list = new_result.split(",");
        var status_title = $(".col-sm-4 h4 strong");
        $.each(status_title, function (k,v) {
            var show_value = status_list[k].replace("\'", "").replace("\'","").trim(" ");
            if (show_value == "端口检测失败"){
               $(this).html("<h1 style='color: red;'>" + show_value + "</h1>");
            } else {
                $(this).html("<h1>" + show_value + "</h1>");
            };

        });

    },"text");
    });



//关机函数

function shutdown_server() {
    $.post("/shutdown_server/", {"action":"shutdown"}, function (result) {
       if (result==0){
           alert("已安全关闭系统！");
       }else {
           alert("关闭系统出错！");
       }
    });

}


    
