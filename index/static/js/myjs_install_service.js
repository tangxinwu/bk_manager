//绑定按钮功能
$(function () {
   var button_content = $(".col-sm-4 button");
   $.each(button_content,function (k,v) {
      if (k%2 == 0){
          var software_name = $(this).parent(".btn-group").siblings(".h4").text();
            //点击按钮触发事件
          $(this).off("click").on("click", function () {
                $(".covered").show();
                $("#software_package_name").val(software_name);
        });

      };
   });
});

//绑定 软件安装按钮

$(function () {
   $(".covered input[type='button']").off("click").on("click", function () {
         var software_name = $("#software_package_name").val();
         var ipaddr = $(".covered select").val();
          $(".covered input[type='button']").val("正在安装...");
          $(".covered input[type='button']").attr("disabled",true);
         $.post("/install_service/", {"software_name" : software_name,"ipaddr":ipaddr}, function (result) {
                    if (result){
                        $(".covered input[type='button']").val("安装");
                        $(".covered input[type='button']").css("disabled",false);
                        alert("安装完成");
                        $(".covered").hide();
                        $(".covered input[type='button']").attr("disabled",false);
                    }

            });
   }) ;
});