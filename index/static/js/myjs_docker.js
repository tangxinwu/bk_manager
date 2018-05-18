/*
docker页面操作js将放在这儿
 */


//service列表的自动刷新
$(function () {
   $.post("docker_service", {"action" : "refresh_service"},function (result) {
       $.each(result.split("\n"), function (k,v) {
           if (v != ""){
               //alert(v);
           };
       });
   }) ;
});
