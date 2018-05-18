//只显示和当前的部门匹配的投票选项
function filter_option(department_name) {
    $.post("/filter_option/",{"department_name" : department_name}, function (result) {
        if (result == "[]"){
            alert("没有部门相关的投票！");
            return;
        };
        $(".covered").hide();
        $(".col-md-3").hide();
        var real_data = JSON.parse(result);
        console.log(real_data);
        $.each(real_data, function (k,v) {
                 var temp_str = '<input type="checkbox" name="' + v["fields"]["OptionName"] + "\n"
                                + '" id="' + v["pk"] + '" data-toggle="checkbox' +'">';
                 var label_str = '<label class="checkbox">' + temp_str + v["fields"]["OptionName"] + '</label>'

                 $(".col-xs-4 .card").append(label_str);
        });
        // var option_name = real_data[0]["fields"]["OptionName"];
        // var option_id = real_data[0]["pk"];
    });
};


//开始投票
$(function(){
    $(".col-md-3 input[type='button']").off("click").on("click",function(){
    var name = $(".col-md-3 input[type='text']").val();
    var department_name = $(".col-md-3 select").val();
    if ($.trim(name) == ""){
        alert("使用匿名投票！");
        $("#logged_name").text("匿名");
    }else {
        $("#logged_name").text(name);
    };
        $("#department").text(department_name);
        var department_name = $("#department").text();
        filter_option(department_name);


});
});


//投票按钮绑定

$(function () {
   $(".col-md-6 input[type='button']").off("click").on("click",function () {
     var checkbox_objects = $(".col-xs-4 input[type='checkbox']:checked");
     var option_ids = new Array();
     var logged_name = $("#logged_name").text();
     var department = $("#department").text();
     $.each(checkbox_objects, function (k,v) {
          option_ids.push(v.id);
     });
     //如果用户没有选择复选框将会停止
     if (option_ids == ""){
       alert("必须选择一项！");
       return false;
     };
     $.post("/vote_action/", {"option_ids" : option_ids.join("-"),"logged_name" : logged_name, "department" : department}, function (result) {
         alert(result);
     $.post("/get_vote_data/", {"action":"get_data"},function (result) {
        var option = JSON.parse(result);
         myChart.setOption(option);
     });

    });

   });
});