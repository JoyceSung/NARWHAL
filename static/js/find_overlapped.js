upload_files_stat={"tsv":false};
var ajaxcounter=0;

$(document).ready(function () {
    $("#submission_panel").hide();
    $("#upload_button").hide();

    
    $('#re_enter').bind("cut copy paste", function(e) {
        e.preventDefault();
        alert("You cannot paste text into this textbox!");
        $('#re_enter').bind("contextmenu", function(e) {
            e.preventDefault();
        });
    });

    $("#addFilesButton").on("click", function () {
      addSampleInput();
      $("#upload_button").show();

    });

    $("#removeFilesButton").on("click", function () {
      removeSampleInput();
    });
  
    function addSampleInput() {
      var sampleInput = $("<input>")
        .attr("type", "text")
        .attr("placeholder", "Sample Name")
        .addClass("sample-input")
        .on("input", function () {
          var value = $(this).val();
          var isValid = /^[a-zA-Z0-9]+$/.test(value);
          if (!isValid) {
            $(this).addClass("invalid");
          } else {
            $(this).removeClass("invalid");
          }
        });
  
      $("#sampleNamesContainer").append(sampleInput);
    }

    function removeSampleInput() {
      var sampleInputs = $(".sample-input");
      if (sampleInputs.length > 0) {
        sampleInputs.last().remove();
      }
      if (sampleInputs.length <= 1) {
        $("#upload_button").hide();
      }
    }


    var csrftoken = getCookie('csrftoken');
    var upload_id = Sha256.hash(Math.random());
    var uploadfileObj_tsv = $("#fileuploader_tsv").uploadFile({
        url:"/data_upload_tsv/",
        multiple:false,
        dragDrop:true,
        allowedTypes:"tsv",
        maxFileSize:5242880,
        maxFileCount:100,
        uploadStr:'<i class="glyphicon glyphicon-plus"></i>Add a file...',
        uploadButtonClass:"btn btn-secondary fileinput-button",
        fileName:"myfile",
        autoSubmit:true,
        returnType:"json",
        sequential:false,
        showFileCounter:false,
        sequentialCount:1,
        serialize:true,
        uploadQueueOrder:"bottom",
        showDelete:true,
        dynamicFormData: function() {
            var data = {'csrfmiddlewaretoken':csrftoken,
                        'upload_id':upload_id,
                        'uploadfile':"tsv",
                        'timeInMs':Date.now(),
                       };
            return data;
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            upload_files_stat['tsv'] = true;
            if(upload_files_stat['tsv'])
            {
                $("#upload_id").val(data['upload_id']);
                $("#tsv_browser_upload").show();
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_tsv", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });
            $("#upload_id").val('');
            upload_files_stat['tsv'] = false;
        }
    });
    
    $(".sample-input").on("blur", function () {
      var value = $(this).val();
      var isValid = /^[a-zA-Z0-9_]+$/.test(value);
      if (!isValid) {
        alert("Please enter only letters, numbers, and underscores.");
        $(this).val(""); // 清空輸入框的內容
      }
    });

    $("#upload_button").on("click", function () {
      var sampleNames = [];
      $(".sample-input").each(function () {
        var value = $(this).val().trim();
        if (value !== "") {
          var isValid = /^[a-zA-Z0-9_]+$/.test(value);
          if (!isValid) {
            alert("Please enter only letters, numbers, and underscores.");
            return; // 中止迴圈
          }
          sampleNames.push(value);
        }
      });

      if (sampleNames.length === 0) {
        alert("Please enter at least one sample name.");
        return;}
      
    
      // 發送 AJAX 請求到後端 view.py
      var csrftoken = getCookie('csrftoken');
    
      $.ajax({
        url: "/confirmed_sample_names/",
        type: "POST",
        data: {sampleNames: sampleNames, 'upload_id':upload_id, csrfmiddlewaretoken: csrftoken },
        success: function (response) {
          if (response.error) {
            alert("Error: " + response.error);
          } else {
            alert("Samples successfully confirmed.");
          }
        },
        error: function (xhr, textStatus, errorThrown) {
          // 获取服务器返回的JsonResponse的错误信息
          var errorResponse = xhr.responseText;
          try {
            var errorJson = JSON.parse(errorResponse);
            if (errorJson.error) {
              alert("ERROR! " + errorJson.error);
            } else {
              alert("An error occurred during the request.");
            }
          } catch (e) {
            alert("An error occurred during the request.");
          }
        }
    });
    
      // 执行其他逻辑...
    });
    
});



$('#HLA-multiple').select2({
    width: "80%",
    allowClear: true,
    maximumSelectionLength: 1,
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
$(".sample-input").each(function(index) {
  var sampleName = $(this).val();
  console.log("Sample Name " + (index + 1) + ": " + sampleName);
});


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
    if (!$(".sample-input").val()) {
      alert("Sample Name invalid!");
      return false;
  }
  
    

});



