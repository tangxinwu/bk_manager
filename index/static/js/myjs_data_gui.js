//测试接口

$(function () {
   $("#test").off("click").on("click", function () {
       $.post("/server_type_count/", {"action": "get"}, function (result) {
          console.log(result);
       });
   }) ;
});