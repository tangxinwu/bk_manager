// 测试环境相关功能

//212 服务器上传jar包
$("#uploader").off("click").on("click", function () {
   var formData = new FormData($("#jar_form")[0]);

   $.ajax(
       {
           url:"/test_environment/",
           type : "POST",
           data : formData,
           async : false,
           cache : false,
           contentType : false,
           processData : false,
           success : function (returndata) {
               alert(returndata);
               if (returndata == "传送失败"){
                   return false;
               }
               if (returndata == "上传的文件不能为空！"){
                   return false;
                   } else if (returndata == "上传文件名不合法") {
                   return false;
               }else {
                      alert("开始替换jar包，将会自动重启服务....");
                       $.get("/test_environment?action=jar",function (result) {
                           alert(result);
                       });
               }
           },
           error : function (returndata) {
               alert(returndata);
           }


       });
});


//212服务器替换jar包并重启服务
$("#212_restart_service").off("click").on("click", function () {
       $.get("/test_environment?action=jar",function (result) {
           alert(result);
               });
});


//213 war文件替换
$("#war_uploader").off("click").on("click", function () {
   var formData = new FormData($("#webapp_form")[0]);

   $.ajax(
       {
           url:"/test_environment/",
           type : "POST",
           data : formData,
           async : false,
           cache : false,
           contentType : false,
           processData : false,
           success : function (returndata) {
               alert(returndata);
               if (returndata == "传送失败"){
                   return false;
               }
               if (returndata == "上传的文件不能为空！"){
                   return false;
                   } else if (returndata == "上传文件名不合法") {
                   return false;
               }else {
                      alert("开始替换war包，将会自动重启服务....");
                       $.get("/test_environment?action=war",function (result) {
                           alert(result);
                       });
               }
           },
           error : function (returndata) {
               alert(returndata);
           }


       });
});


//213重启
$("#213_restart_service").off("click").on("click", function () {
       $.get("/test_environment?action=war",function (result) {
           alert(result);
               });
});


//212数据库替换数据
$("#sql_uploader").off("click").on("click", function () {
   var formData = new FormData($("#sql_form")[0]);

   $.ajax(
       {
           url:"/test_environment/",
           type : "POST",
           data : formData,
           async : false,
           cache : false,
           contentType : false,
           processData : false,
           success : function (returndata) {
               alert(returndata);
               if (returndata == "传送失败"){
                   return false;
               }
               if (returndata == "上传的文件不能为空！"){
                   return false;
                   } else if (returndata == "上传文件名不合法") {
                   return false;
               }else {
                      alert("开始更新数据库....");
                       $.get("/test_environment?action=sql",function (result) {
                           alert(result);
                       });
               }
           },
           error : function (returndata) {
               alert(returndata);
           }


       });
});


//弹出层

$(function () {
   $("#myModal").modal();
});