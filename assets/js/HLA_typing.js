upload_files_stat={"R1":false, "R2":false};
var ajaxcounter=0;

$(document).ready(function () {
    $("table").hide();
    $("#upload_button").hide();
    $("#url_upload").hide();
    $("#submission_panel").hide();
    $('#re_enter').bind("cut copy paste", function(e) {
        e.preventDefault();
        alert("You cannot paste text into this textbox!");
        $('#re_enter').bind("contextmenu", function(e) {
            e.preventDefault();
        });
    });

    var csrftoken = getCookie('csrftoken');
    var upload_id = Sha256.hash(Math.random());
    var uploadfileObj = $("#fileuploader").uploadFile({
        url:"/data_upload/",
        multiple:true,
        dragDrop:true,
        maxFileCount:2,
        allowedTypes:"gz",
        maxFileSize:21474836480,
        uploadStr:'<i class="glyphicon glyphicon-plus"></i>Add files...',
        uploadButtonClass:"btn btn-secondary fileinput-button",
        fileName:"myfile",
        autoSubmit:false,
        returnType:"json",
        sequential:true,
        sequentialCount:1,
        serialize:true,
        uploadQueueOrder:"bottom",
        showDelete:true,
        dynamicFormData: function() {
            var data = {'csrfmiddlewaretoken':csrftoken,
                        'upload_id':upload_id
                       };
            return data;
        },
        extraHTML:function() {
            var obj_rad_uploadfile = $(".rad_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(obj_rad_uploadfile.length > 0) {
                obj_rad_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(obj_rad_uploadfile.attr("name") == "uploadfile_type1") htm_name = 'uploadfile_type2';
                else htm_name = 'uploadfile_type1';
            }
            else {
                htm_name = 'uploadfile_type1';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="rad_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="rad_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#upload_button").hide();
                $("#upload_id").val(data['upload_id']);
                $("#url_upload").hide();
                $("#browser_upload").show();
                $("input[id=from_browser]").prop("checked", true).attr("checked", true);
                $("#upload_method").val($("input[name=rad_upload_method]:checked").val())
                $("input[name=rad_upload_method]").attr("disabled", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });

            $("#upload_button").hide();
            $("#upload_id").val('');
            $("#upload_method").val('')
            $("input[name=rad_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1']] = false;
            }
        }
    });

    $("#upload_button").click(function()
    {
        $("input[name='uploadfile_type1']").attr("disabled", true);
        $("input[name='uploadfile_type2']").attr("disabled", true);
        uploadfileObj.startUpload();
    });

    $("#upload_area").change(function(){
        if(uploadfileObj.getFileCount() == 2) {$("#upload_button").show();}
    });

    $("#upload_area").on("click", ".rad_uploadfile_type", function(){
        var obj_rad_uploadfile = $(".rad_uploadfile_type");
        var current_inx = obj_rad_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        obj_rad_uploadfile.removeAttr("checked");
        obj_rad_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        obj_rad_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });


    $("#url_confirm_button").click(function(event){
        var str_url_R1 = $("#url_R1").val();
        var str_url_R2 = $("#url_R2").val();
        $("#url_R1_err").text("");
        $("#url_R2_err").text("");
        var upload_id = Sha256.hash(Math.random());

        if(str_url_R1 == "" || str_url_R2 == "") {
            if(str_url_R1 == "") {$("#url_R1_err").text("*Required field.");}
            if(str_url_R2 == "") {$("#url_R2_err").text("*Required field.");}
        }
        else {
            $.ajax({
                type: "POST",
                dataType: "json",
                url: "/confirm_urls",
                data: {
                    'csrfmiddlewaretoken': csrftoken,
                    'url_R1': str_url_R1,
                    'url_R2': str_url_R2,
                    'upload_id':upload_id
                },
                error: function () {
                    // do nothing
                    alert('Failed to download from the URLs. Please contact the administrator.');
                },
                success: function (data) {
                        $("#upload_id").val(upload_id);
                        $("#url_R1").attr("disabled", true);
                        $("#url_R2").attr("disabled", true);
                        $("#confirmed_url_R1").val(str_url_R1);
                        $("#confirmed_url_R2").val(str_url_R2);
                        $("#url_confirm_button").hide();
                        $("#browser_upload").hide();
                        $("#url_upload").show();
                        $("input[id=from_url]").prop("checked", true).attr("checked", true);
                        $("#upload_method").val($("input[name=rad_upload_method]:checked").val())
                        $("input[name=rad_upload_method]").attr("disabled", true);
                }
            });
        }
    });

});


$("input[name='rad_upload_method']").change(function(){
    if($("#from_browser").is(':checked')){
        $("#url_upload").hide();
        $("#browser_upload").show();
    }
    else if($("#from_url").is(':checked')){
        $("#browser_upload").hide();
        $("#url_upload").show();
    }

});

$("#accept_privacy_statement").change(function(){
    var check_val;
    check_val = $("#accept_privacy_statement:checked").val();
    if(check_val == "accept"){
        $("#submission_panel").show();
    }
    else {
        $("#submission_panel").hide();
    }
});

function validateEmail(email) {
  var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
};

$("#submit").click(function() {
    if(!validateEmail($("#email").val()))
    {
        alert("Email invalid!");
        return false;
    }
    if($("#email").val() !=$("#re_enter").val())
    {
        alert("Email re-enter not matched!");
        return false;
    }
    if($("#accept_privacy_statement:checked").val() != "accept")
    {
        alert("Must accept the Privacy Statement of NARWHAL!");
        return false;
    }

});
