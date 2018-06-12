//定时备份快照的js

$("tbody tr").off("click").on("click", function () {
    //选取tr下的td子元素的第二个 就是ip界面
    var ip = $(this).children()[1].innerText;
    $("#myModalLabel").text(ip);
    $("#myModal").modal();
});

//更改或增加定时任务
$("#save").off("click").on("click",function () {
   var ip = $("#myModalLabel").text()
   var interval = $("#interval").val();
   var timing_unit = $("#timing_unit").val();
   var week_day = $("#week_day").val();
   var detail_time = $("#detail_time").val();
   if (interval && (week_day != "" || detail_time != "")){
        alert("间隔时间和定点星期和定点时间不能同时使用！")
        return false;
   }
   if (interval == "" && week_day == "" && detail_time == ""){
       alert("间隔时间和定点时间至少选择一个！")
       return false;
   }
   if (interval < 0){
       alert("间隔时间请调到正数！");
       return false;
   }
    $.post("/timer_snapshot/", {"ip":ip, "interval" : interval, "timing_unit" :timing_unit, "week_day":week_day, "detail_time":detail_time }, function (result) {
        alert(result);
        if (result=="变更成功"){
            var obj = document.getElementById(ip).getElementsByTagName("td");
            obj[2].innerText = interval;
            obj[3].innerText = timing_unit;
            obj[4].innerText = week_day;
            obj[5].innerText = detail_time;
        }

    });
});

//后台snapshot控制的进程的状态

$(function () {
   $.post("/snapshot_status/", {"action":"status"}, function (result) {
      if (result == "Exited"){
          $("#alert_status").attr("src","/static/images/red-alert.gif");

      }else {
          $("#alert_status").attr("src","/static/images/green-alert.gif");
      }
   });
   $("#process_submit").off("click").on("click", function () {
      var action = $("#sent_singal").val();
      $.post("/snapshot_status/", {"action":action}, function (result) {
         alert(result);
         if (result == "Stared failed!" || result == "Daemon stopped!" || result == "Daemon not running!"){
             $("#alert_status").attr("src","/static/images/red-alert.gif");
         }else {
             $("#alert_status").attr("src","/static/images/green-alert.gif");
         }
      });
   });
});


//search 查找js

$("#filter_ip").off("click").on("click", function () {
    var tr_objects = $("tbody tr");
    var filter_content = $("#filter_content").val();

    $.each(tr_objects, function (k,v) {
        var children_content =$(this).children();
        if (children_content[1].innerText.indexOf(filter_content) != -1){
            $(this).show();
        }else {
            $(this).hide();
        }
    })
});

