upload_files_stat={"R1":false, "R2":false, "mass":false};
confirmed_urls_stat={"reads":false, "mass":false};

var ajaxcounter=0;
$(document).ready(function () {
    // DNA-seq
    $("#DNA_pipeline").hide();
    $("#dna_tumor_upload_button").hide();
    $("#dna_normal_upload_button").hide();
    $("#dna_tumor_url_upload").hide();
    $("#dna_normal_url_upload").hide();
    $("#dna_hla_bottom").hide();
    $("#dna_mass_url_upload").hide();
    $("#dna_submission_panel").hide();
    $("table[name='dna_ic50_table']").hide();

    // RNA-seq
    $("#RNA_pipeline").hide();
    $("#rna_tumor_upload_button").hide();
    $("#rna_normal_upload_button").hide();
    $("#rna_tumor_url_upload").hide();
    $("#rna_normal_url_upload").hide();
    $("#rna_mass_url_upload").hide();
    $("#rna_hla_bottom").hide();
    $("#rna_submission_panel").hide();
    $("table[name='rna_ic50_table']").hide();
    $("table[name='variant_table']").hide();
    $("table[name='expression_table']").hide();

    // DNA + RNA-seq
    $("#DNA_with_RNA_pipeline").hide();
    $("#drna_tumor_upload_button").hide();
    $("#drna_normal_upload_button").hide();
    $("#drna_tumor_url_upload").hide();
    $("#drna_normal_url_upload").hide();
    $("#drna_mass_url_upload").hide();
    $("#drna_hla_bottom").hide();
    $("#rdna_tumor_upload_button").hide();
    $("#rdna_normal_upload_button").hide();
    $("#rdna_tumor_url_upload").hide();
    $("#rdna_normal_url_upload").hide();
    $("#rdna_mass_url_upload").hide();
    $("#drna_submission_panel").hide();
    $("table[name='drna_ic50_table']").hide();
    $("table[name='drna_expression_table']").hide();
    

    $("input[name='data_type']").change(function(){
        var DNA_seq;
        DNA_seq = $("#DNA_seq:checked").val();
        var RNA_seq;
        RNA_seq = $("#RNA_seq:checked").val();
        if((DNA_seq == "DNA_seq") && (RNA_seq == "RNA_seq")){
            $("#DNA_with_RNA_pipeline").show();
            $("#DNA_pipeline").hide();
            $("#RNA_pipeline").hide();
        }
        else if(DNA_seq == "DNA_seq"){
            $("#DNA_pipeline").show();
            $("#RNA_pipeline").hide();
            $("#DNA_with_RNA_pipeline").hide();
        }
        else if(RNA_seq == "RNA_seq") {
            $("#RNA_pipeline").show();
            $("#DNA_pipeline").hide();
            $("#DNA_with_RNA_pipeline").hide();
        }
        else{
            $("#DNA_with_RNA_pipeline").hide();
            $("#DNA_pipeline").hide();
            $("#RNA_pipeline").hide();
        }
    });
    $('#re_enter_dna').bind("cut copy paste", function(e) {
        e.preventDefault();
        alert("You cannot paste text into this textbox!");
        $('#re_enter_dna').bind("contextmenu", function(e) {
            e.preventDefault();
        });
    });
    $('#re_enter_rna').bind("cut copy paste", function(e) {
        e.preventDefault();
        alert("You cannot paste text into this textbox!");
        $('#re_enter_rna').bind("contextmenu", function(e) {
            e.preventDefault();
        });
    });
    $('#re_enter_drna').bind("cut copy paste", function(e) {
        e.preventDefault();
        alert("You cannot paste text into this textbox!");
        $('#re_enter_drna').bind("contextmenu", function(e) {
            e.preventDefault();
        });
    });

    // DNA-seq upload
    var csrftoken = getCookie('csrftoken');
    var upload_id = Sha256.hash(Math.random());
    var uploadfileObj_dna_tumor = $("#fileuploader_dna_tumor").uploadFile({
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
            var dna_tumor_uploadfile = $(".dna_tumor_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(dna_tumor_uploadfile.length > 0) {
                dna_tumor_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(dna_tumor_uploadfile.attr("name") == "uploadfile_type1_dna_tumor") htm_name = 'uploadfile_type2_dna_tumor';
                else htm_name = 'uploadfile_type1_dna_tumor';
            }
            else {
                htm_name = 'uploadfile_type1_dna_tumor';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="dna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="dna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#dna_tumor_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#dna_tumor_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_dna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_dna_tumor']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_dna_tumor']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#dna_tumor_upload_button").hide();
                $("#upload_id").val(data['upload_id']);
                $("#dna_tumor_url_upload").hide();
                $("#dna_tumor_browser_upload").show();
                $("input[id=dna_tumor_from_browser]").prop("checked", true).attr("checked", true);
                $("#dna_T_upload_method").val($("input[name=dna_tumor_upload_method]:checked").val())
                $("input[name=dna_tumor_upload_method]").attr("disabled", true);
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

            $("#dna_tumor_upload_button").hide();
            $("#upload_id").val('');
            $("#dna_T_upload_method").val('')
            $("input[name=dna_tumor_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_dna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_dna_tumor']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_dna_tumor']] = false;
            }
        }
    });

    var uploadfileObj_dna_normal = $("#fileuploader_dna_normal").uploadFile({
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
            var dna_normal_uploadfile = $(".dna_normal_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(dna_normal_uploadfile.length > 0) {
                dna_normal_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(dna_normal_uploadfile.attr("name") == "uploadfile_type1_dna_normal") htm_name = 'uploadfile_type2_dna_normal';
                else htm_name = 'uploadfile_type1_dna_normal';
            }
            else {
                htm_name = 'uploadfile_type1_dna_normal';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="dna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="dna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#dna_normal_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#dna_normal_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_dna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_dna_normal']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_dna_normal']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#dna_normal_upload_button").hide();
                $("#upload_id").val(data['upload_id']);
                $("#dna_normal_url_upload").hide();
                $("#dna_normal_browser_upload").show();
                $("input[id=dna_normal_from_browser]").prop("checked", true).attr("checked", true);
                $("#dna_N_upload_method").val($("input[name=dna_normal_upload_method]:checked").val())
                $("input[name=dna_normal_upload_method]").attr("disabled", true);
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

            $("#dna_normal_upload_button").hide();
            $("#upload_id").val('');
            $("#dna_N_upload_method").val('')
            $("input[name=dna_normal_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_dna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_dna_normal']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_dna_normal']] = false;
            }
        }
    });

    // DNA MASS upload
    var uploadfileObj_dna_mass = $("#fileuploader_dna_mass").uploadFile({
        url:"/data_upload/",
        multiple:false,
        dragDrop:true,
        maxFileCount:1,
        allowedTypes:"gz",
        maxFileSize:2147483648,
        uploadStr:'<i class="glyphicon glyphicon-plus"></i>Add a file...',
        uploadButtonClass:"btn btn-secondary fileinput-button",
        fileName:"myfile",
        autoSubmit:true,
        returnType:"json",
        sequential:true,
        sequentialCount:1,
        serialize:true,
        uploadQueueOrder:"bottom",
        showDelete:true,
        dynamicFormData: function() {
            var data = {'csrfmiddlewaretoken':csrftoken,
                        'upload_id':upload_id,
                        'uploadfile_dna_mass':"mass"
                       };
            return data;
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            upload_files_stat['mass'] = true;
            
            if(upload_files_stat['R1'] && upload_files_stat['R2'] && upload_files_stat['mass'])
            {
                $("#upload_id").val(data['upload_id']);
                $("input[id=dna_mass_from_browser]").prop("checked", true).attr("checked", true);
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
            $("#upload_id").val('');
            $("#dna_mass_upload_method").val('')
            $("input[name=dna_Ms_upload_method]").attr("disabled", false);
            upload_files_stat['mass'] = false;
        }
    });


    // RNA upload
    var upload_id_rna = Sha256.hash(Math.random());
    var uploadfileObj_rna_tumor = $("#fileuploader_rna_tumor").uploadFile({
        url:"/data_upload_rna/",
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
                        'upload_id_rna':upload_id_rna
                       };
            return data;
        },
        extraHTML:function() {
            var rna_tumor_uploadfile = $(".rna_tumor_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(rna_tumor_uploadfile.length > 0) {
                rna_tumor_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(rna_tumor_uploadfile.attr("name") == "uploadfile_type1_rna_tumor") htm_name = 'uploadfile_type2_rna_tumor';
                else htm_name = 'uploadfile_type1_rna_tumor';
            }
            else {
                htm_name = 'uploadfile_type1_rna_tumor';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="rna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="rna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rna_tumor_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rna_tumor_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_rna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rna_tumor']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rna_tumor']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#rna_tumor_upload_button").hide();
                $("#upload_id_rna").val(data['upload_id_rna']);
                $("#rna_tumor_url_upload").hide();
                $("#rna_tumor_browser_upload").show();
                $("input[id=rna_tumor_from_browser]").prop("checked", true).attr("checked", true);
                $("#rna_T_upload_method").val($("input[name=rna_tumor_upload_method]:checked").val())
                $("input[name=rna_tumor_upload_method]").attr("disabled", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_rna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });

            $("#rna_tumor_upload_button").hide();
            $("#upload_id_rna").val('');
            $("#rna_T_upload_method").val('')
            $("input[name=rna_tumor_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_rna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rna_tumor']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rna_tumor']] = false;
            }
        }
    });

    var uploadfileObj_rna_normal = $("#fileuploader_rna_normal").uploadFile({
        url:"/data_upload_rna/",
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
                        'upload_id_rna':upload_id_rna
                       };
            return data;
        },

        extraHTML:function() {
            var rna_normal_uploadfile = $(".rna_normal_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(rna_normal_uploadfile.length > 0) {
                rna_normal_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(rna_normal_uploadfile.attr("name") == "uploadfile_type1_rna_normal") htm_name = 'uploadfile_type2_rna_normal';
                else htm_name = 'uploadfile_type1_rna_normal';
            }
            else {
                htm_name = 'uploadfile_type1_rna_normal';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="rna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="rna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rna_normal_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rna_normal_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_rna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rna_normal']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rna_normal']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#rna_normal_upload_button").hide();
                $("#upload_id_rna").val(data['upload_id_rna']);
                $("#rna_normal_url_upload").hide();
                $("#rna_normal_browser_upload").show();
                $("input[id=rna_normal_from_browser]").prop("checked", true).attr("checked", true);
                $("#rna_N_upload_method").val($("input[name=rna_normal_upload_method]:checked").val())
                $("input[name=rna_normal_upload_method]").attr("disabled", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_rna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });

            $("#rna_normal_upload_button").hide();
            $("#upload_id_rna").val('');
            $("#rna_N_upload_method").val('')
            $("input[name=rna_normal_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_rna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rna_normal']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rna_normal']] = false;
            }
        }
    });

    // RNA MASS upload
    var uploadfileObj_rna_mass = $("#fileuploader_rna_mass").uploadFile({
        url:"/data_upload_rna/",
        multiple:false,
        dragDrop:true,
        maxFileCount:1,
        allowedTypes:"gz",
        maxFileSize:2147483648,
        uploadStr:'<i class="glyphicon glyphicon-plus"></i>Add a file...',
        uploadButtonClass:"btn btn-secondary fileinput-button",
        fileName:"myfile",
        autoSubmit:true,
        returnType:"json",
        sequential:true,
        sequentialCount:1,
        serialize:true,
        uploadQueueOrder:"bottom",
        showDelete:true,
        dynamicFormData: function() {
            var data = {'csrfmiddlewaretoken':csrftoken,
                        'upload_id_rna':upload_id_rna,
                        'uploadfile_rna_mass':"mass"
                       };
            return data;
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            upload_files_stat['mass'] = true;
            
            if(upload_files_stat['R1'] && upload_files_stat['R2'] && upload_files_stat['mass'])
            {
                $("#upload_id_rna").val(data['upload_id_rna']);
                $("#rna_mass_url_upload").hide();
                $("#rna_mass_browser_upload").show();
                $("input[id=rna_mass_from_browser]").prop("checked", true).attr("checked", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_rna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });
            
            $("#upload_id_rna").val('');
            $("#rna_mass_upload_method").val('')
            $("input[name=rna_Ms_upload_method]").attr("disabled", false);
            upload_files_stat['mass'] = false;
        }
    });

    // DNA + RNA upload
    // DNA + RNA DNA part
    var upload_id_drna = Sha256.hash(Math.random());
    var uploadfileObj_rdna_tumor = $("#fileuploader_rdna_tumor").uploadFile({
        url:"/data_upload_drna/",
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
                        'upload_id_drna':upload_id_drna
                       };
            return data;
        },
        extraHTML:function() {
            var rdna_tumor_uploadfile = $(".rdna_tumor_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(rdna_tumor_uploadfile.length > 0) {
                rdna_tumor_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(rdna_tumor_uploadfile.attr("name") == "uploadfile_type1_rdna_tumor") htm_name = 'uploadfile_type2_rdna_tumor';
                else htm_name = 'uploadfile_type1_rdna_tumor';
            }
            else {
                htm_name = 'uploadfile_type1_rdna_tumor';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="rdna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="rdna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rdna_tumor_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rdna_tumor_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_rdna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rdna_tumor']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rdna_tumor']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#rdna_tumor_upload_button").hide();
                $("#upload_id_drna").val(data['upload_id_drna']);
                $("#rdna_tumor_url_upload").hide();
                $("#rdna_tumor_browser_upload").show();
                $("input[id=rdna_tumor_from_browser]").prop("checked", true).attr("checked", true);
                $("#rdna_T_upload_method").val($("input[name=rdna_tumor_upload_method]:checked").val())
                $("input[name=rdna_tumor_upload_method]").attr("disabled", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_drna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });

            $("#rdna_tumor_upload_button").hide();
            $("#upload_id_drna").val('');
            $("#rdna_T_upload_method").val('')
            $("input[name=rdna_tumor_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_rdna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rdna_tumor']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rdna_tumor']] = false;
            }
        }
    });


    var uploadfileObj_rdna_normal = $("#fileuploader_rdna_normal").uploadFile({
        url:"/data_upload_drna/",
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
                        'upload_id_drna':upload_id_drna
                       };
            return data;
        },

        extraHTML:function() {
            var rdna_normal_uploadfile = $(".rdna_normal_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(rdna_normal_uploadfile.length > 0) {
                rdna_normal_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(rdna_normal_uploadfile.attr("name") == "uploadfile_type1_rdna_normal") htm_name = 'uploadfile_type2_rdna_normal';
                else htm_name = 'uploadfile_type1_rdna_normal';
            }
            else {
                htm_name = 'uploadfile_type1_rdna_normal';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="rdna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="rdna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rdna_normal_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#rdna_normal_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_rdna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rdna_normal']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rdna_normal']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#rdna_normal_upload_button").hide();
                $("#upload_id_drna").val(data['upload_id_drna']);
                $("#rdna_normal_url_upload").hide();
                $("#rdna_normal_browser_upload").show();
                $("input[id=rdna_normal_from_browser]").prop("checked", true).attr("checked", true);
                $("#rdna_N_upload_method").val($("input[name=rdna_normal_upload_method]:checked").val())
                $("input[name=rdna_normal_upload_method]").attr("disabled", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_drna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });

            $("#rdna_normal_upload_button").hide();
            $("#upload_id_drna").val('');
            $("#rdna_N_upload_method").val('')
            $("input[name=rdna_normal_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_rdna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_rdna_normal']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_rdna_normal']] = false;
            }
        }
    });

    // DNA + RNA RNA part
    var uploadfileObj_drna_tumor = $("#fileuploader_drna_tumor").uploadFile({
        url:"/data_upload_drna/",
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
                        'upload_id_drna':upload_id_drna
                       };
            return data;
        },
        extraHTML:function() {
            var drna_tumor_uploadfile = $(".drna_tumor_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(drna_tumor_uploadfile.length > 0) {
                drna_tumor_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(drna_tumor_uploadfile.attr("name") == "uploadfile_type1_drna_tumor") htm_name = 'uploadfile_type2_drna_tumor';
                else htm_name = 'uploadfile_type1_drna_tumor';
            }
            else {
                htm_name = 'uploadfile_type1_drna_tumor';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="drna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="drna_tumor_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#drna_tumor_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#drna_tumor_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_drna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_drna_tumor']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_drna_tumor']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#drna_tumor_upload_button").hide();
                $("#upload_id_drna").val(data['upload_id_drna']);
                $("#drna_tumor_url_upload").hide();
                $("#drna_tumor_browser_upload").show();
                $("input[id=drna_tumor_from_browser]").prop("checked", true).attr("checked", true);
                $("#drna_T_upload_method").val($("input[name=drna_tumor_upload_method]:checked").val())
                $("input[name=drna_tumor_upload_method]").attr("disabled", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_drna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });

            $("#drna_tumor_upload_button").hide();
            $("#upload_id_drna").val('');
            $("#drna_T_upload_method").val('')
            $("input[name=drna_tumor_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_drna_tumor'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_drna_tumor']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_drna_tumor']] = false;
            }
        }
    });

    var uploadfileObj_drna_normal = $("#fileuploader_drna_normal").uploadFile({
        url:"/data_upload_drna/",
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
                        'upload_id_drna':upload_id_drna
                       };
            return data;
        },

        extraHTML:function() {
            var drna_normal_uploadfile = $(".drna_normal_uploadfile_type");
            var htm_name = '';
            var htm_R1_checked = '';
            var htm_R2_checked = '';
            var htm_disabled = '';
            if(drna_normal_uploadfile.length > 0) {
                drna_normal_uploadfile.each(function(index) {
                    if($(this).is(':checked')) {
                        if($(this).val() == 'R1') htm_R2_checked = ' checked';
                        else if($(this).val() == 'R2') htm_R1_checked = ' checked';
                    }
                    if($(this).is(':disabled')) htm_disabled = ' disabled';
                });
                if(drna_normal_uploadfile.attr("name") == "uploadfile_type1_drna_normal") htm_name = 'uploadfile_type2_drna_normal';
                else htm_name = 'uploadfile_type1_drna_normal';
            }
            else {
                htm_name = 'uploadfile_type1_drna_normal';
                htm_R1_checked = ' checked';
            }

            return '<label class="radio-inline"> <input type="radio" class="drna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R1" value="R1"'+htm_R1_checked+htm_disabled+'>R1</input></label><label class="radio-inline"><input type="radio" class="drna_normal_uploadfile_type" name="'+htm_name+'" id="'+htm_name+'_R2" value="R2"'+htm_R2_checked+htm_disabled+'>R2</input></label>';
        },
        onCancel: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#drna_normal_upload_button").hide();
        },
        onAbort: function(files,pd)
        {
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(pd));
            $("#drna_normal_upload_button").hide();
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            if(typeof(data['uploadfile_type1_drna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_drna_normal']] = true;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_drna_normal']] = true;
            }
            //console.log(JSON.stringify(upload_files_stat));

            if(upload_files_stat['R1'] && upload_files_stat['R2'])
            {
                $("#drna_normal_upload_button").hide();
                $("#upload_id_drna").val(data['upload_id_drna']);
                $("#drna_normal_url_upload").hide();
                $("#drna_normal_browser_upload").show();
                $("input[id=drna_normal_from_browser]").prop("checked", true).attr("checked", true);
                $("#drna_N_upload_method").val($("input[name=drna_normal_upload_method]:checked").val())
                $("input[name=drna_normal_upload_method]").attr("disabled", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_drna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });

            $("#drna_normal_upload_button").hide();
            $("#upload_id_drna").val('');
            $("#drna_N_upload_method").val('')
            $("input[name=drna_normal_upload_method]").attr("disabled", false);
            if(typeof(data['uploadfile_type1_drna_normal'])=='undefined')
            {
                upload_files_stat[data['uploadfile_type2_drna_normal']] = false;
            }
            else
            {
                upload_files_stat[data['uploadfile_type1_drna_normal']] = false;
            }
        }
    });

    // DNA + RNA MASS part
    var uploadfileObj_drna_mass = $("#fileuploader_drna_mass").uploadFile({
        url:"/data_upload_drna/",
        multiple:false,
        dragDrop:true,
        maxFileCount:1,
        allowedTypes:"gz",
        maxFileSize:2147483648,
        uploadStr:'<i class="glyphicon glyphicon-plus"></i>Add a file...',
        uploadButtonClass:"btn btn-secondary fileinput-button",
        fileName:"myfile",
        autoSubmit:true,
        returnType:"json",
        sequential:true,
        sequentialCount:1,
        serialize:true,
        uploadQueueOrder:"bottom",
        showDelete:true,
        dynamicFormData: function() {
            var data = {'csrfmiddlewaretoken':csrftoken,
                        'upload_id_drna':upload_id_drna,
                        'uploadfile_drna_mass':"mass"
                       };
            return data;
        },
        onSuccess:function(files,data,xhr,pd){
            //console.log(JSON.stringify(files));
            //console.log(JSON.stringify(data));
            upload_files_stat['mass'] = true;
            
            if(upload_files_stat['R1'] && upload_files_stat['R2'] && upload_files_stat['mass'])
            {
                $("#upload_id_drna").val(data['upload_id_drna']);
                $("#drna_mass_url_upload").hide();
                $("#drna_mass_browser_upload").show();
                $("input[id=drna_mass_from_browser]").prop("checked", true).attr("checked", true);
            }
        },
        deleteCallback: function (data, pd) {
            var post_data = {};
            Object.keys(data).forEach(function(key, index) {
                post_data[key] = this[key];
            }, data);
            $.post("/delete_upload_drna", post_data,
            function (resp, textStatus, jqXHR) {
                //Show Message
                //console.log(JSON.stringify(resp));
            });
            $("#upload_id_drna").val('');
            $("#drna_mass_upload_method").val('')
            $("input[name=drna_Ms_upload_method]").attr("disabled", false);
            upload_files_stat['mass'] = false;
        }
    });

    //  DNA-seq upload area
    $("#dna_tumor_upload_area").change(function(){
        if(uploadfileObj_dna_tumor.getFileCount() == 2) {$("#dna_tumor_upload_button").show();}
    });

    $("#dna_tumor_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_dna_tumor']").attr("disabled", true);
        $("input[name='uploadfile_type2_dna_tumor']").attr("disabled", true);
        uploadfileObj_dna_tumor.startUpload();
    });

    $("#dna_tumor_upload_area").on("click", ".dna_tumor_uploadfile_type", function(){
        var dna_tumor_uploadfile = $(".dna_tumor_uploadfile_type");
        var current_inx = dna_tumor_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        dna_tumor_uploadfile.removeAttr("checked");
        dna_tumor_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        dna_tumor_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });

    $("#dna_normal_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_dna_normal']").attr("disabled", true);
        $("input[name='uploadfile_type2_dna_normal']").attr("disabled", true);
        uploadfileObj_dna_normal.startUpload();
    });

    $("#dna_normal_upload_area").change(function(){
        if(uploadfileObj_dna_normal.getFileCount() == 2) {$("#dna_normal_upload_button").show();}
    });

    $("#dna_normal_upload_area").on("click", ".dna_normal_uploadfile_type", function(){
        var dna_normal_uploadfile = $(".dna_normal_uploadfile_type");
        var current_inx = dna_normal_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        dna_normal_uploadfile.removeAttr("checked");
        dna_normal_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        dna_normal_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });



    //  RNA-seq upload area
    $("#rna_tumor_upload_area").change(function(){
        if(uploadfileObj_rna_tumor.getFileCount() == 2) {$("#rna_tumor_upload_button").show();}
    });

    $("#rna_tumor_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_rna_tumor']").attr("disabled", true);
        $("input[name='uploadfile_type2_rna_tumor']").attr("disabled", true);
        uploadfileObj_rna_tumor.startUpload();
    });



    $("#rna_tumor_upload_area").on("click", ".rna_tumor_uploadfile_type", function(){
        var rna_tumor_uploadfile = $(".rna_tumor_uploadfile_type");
        var current_inx = rna_tumor_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        rna_tumor_uploadfile.removeAttr("checked");
        rna_tumor_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        rna_tumor_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });


    $("#rna_normal_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_rna_normal']").attr("disabled", true);
        $("input[name='uploadfile_type2_rna_normal']").attr("disabled", true);
        uploadfileObj_rna_normal.startUpload();
    });

    $("#rna_normal_upload_area").change(function(){
        if(uploadfileObj_rna_normal.getFileCount() == 2) {$("#rna_normal_upload_button").show();}
    });

    $("#rna_normal_upload_area").on("click", ".rna_normal_uploadfile_type", function(){
        var rna_normal_uploadfile = $(".rna_normal_uploadfile_type");
        var current_inx = rna_normal_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        rna_normal_uploadfile.removeAttr("checked");
        rna_normal_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        rna_normal_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });

    //  DNA + RNA-seq upload area
    // DNA part
    $("#rdna_tumor_upload_area").change(function(){
        if(uploadfileObj_rdna_tumor.getFileCount() == 2) {$("#rdna_tumor_upload_button").show();}
    });

    $("#rdna_tumor_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_rdna_tumor']").attr("disabled", true);
        $("input[name='uploadfile_type2_rdna_tumor']").attr("disabled", true);
        uploadfileObj_rdna_tumor.startUpload();
    });

    $("#rdna_tumor_upload_area").on("click", ".rdna_tumor_uploadfile_type", function(){
        var rdna_tumor_uploadfile = $(".rdna_tumor_uploadfile_type");
        var current_inx = rdna_tumor_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        rdna_tumor_uploadfile.removeAttr("checked");
        rdna_tumor_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        rdna_tumor_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });

    $("#rdna_normal_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_rdna_normal']").attr("disabled", true);
        $("input[name='uploadfile_type2_rdna_normal']").attr("disabled", true);
        uploadfileObj_rdna_normal.startUpload();
    });

    $("#rdna_normal_upload_area").change(function(){
        if(uploadfileObj_rdna_normal.getFileCount() == 2) {$("#rdna_normal_upload_button").show();}
    });

    $("#rdna_normal_upload_area").on("click", ".rdna_normal_uploadfile_type", function(){
        var rdna_normal_uploadfile = $(".rdna_normal_uploadfile_type");
        var current_inx = rdna_normal_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        rdna_normal_uploadfile.removeAttr("checked");
        rdna_normal_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        rdna_normal_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });
    // RNA part
    $("#drna_tumor_upload_area").change(function(){
        if(uploadfileObj_drna_tumor.getFileCount() == 2) {$("#drna_tumor_upload_button").show();}
    });

    $("#drna_tumor_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_drna_tumor']").attr("disabled", true);
        $("input[name='uploadfile_type2_drna_tumor']").attr("disabled", true);
        uploadfileObj_drna_tumor.startUpload();
    });



    $("#drna_tumor_upload_area").on("click", ".drna_tumor_uploadfile_type", function(){
        var drna_tumor_uploadfile = $(".drna_tumor_uploadfile_type");
        var current_inx = drna_tumor_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        drna_tumor_uploadfile.removeAttr("checked");
        drna_tumor_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        drna_tumor_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });


    $("#drna_normal_upload_button").click(function()
    {
        $("input[name='uploadfile_type1_drna_normal']").attr("disabled", true);
        $("input[name='uploadfile_type2_drna_normal']").attr("disabled", true);
        uploadfileObj_drna_normal.startUpload();
    });

    $("#drna_normal_upload_area").change(function(){
        if(uploadfileObj_drna_normal.getFileCount() == 2) {$("#drna_normal_upload_button").show();}
    });

    $("#drna_normal_upload_area").on("click", ".drna_normal_uploadfile_type", function(){
        var drna_normal_uploadfile = $(".drna_normal_uploadfile_type");
        var current_inx = drna_normal_uploadfile.index(this);
        var corresponding_idx = (-1)*current_inx+3;
        drna_normal_uploadfile.removeAttr("checked");
        drna_normal_uploadfile.eq(current_inx).prop("checked", true).attr("checked", true);
        drna_normal_uploadfile.eq(corresponding_idx).prop("checked", true).attr("checked", true);
    });



// DNA url
    $("#dna_tumor_url_confirm_button").click(function(event){
        var str_url_R1 = $("#url_dna_tumor_R1").val();
        var str_url_R2 = $("#url_dna_tumor_R2").val();
        $("#url_dna_tumor_R1_err").text("");
        $("#url_dna_tumor_R2_err").text("");
        // var upload_id = Sha256.hash(Math.random());

        if(str_url_R1 == "" || str_url_R2 == "") {
            if(str_url_R1 == "") {$("#url_dna_tumor_R1_err").text("*Required field.");}
            if(str_url_R2 == "") {$("#url_dna_tumor_R2_err").text("*Required field.");}
        }
        else {
            $.ajax({
                type: "POST",
                dataType: "json",
                url: "/confirm_urls",
                data: {
                    'csrfmiddlewaretoken': csrftoken,
                    'url_dna_tumor_R1': str_url_R1,
                    'url_dna_tumor_R2': str_url_R2,
                    'upload_id':upload_id,
                    'upload_id_rna':"None",
                    'upload_id_drna':"None"
                },
                error: function () {
                    // do nothing
                    alert('Failed to download from the URLs. Please check your file links or formats.');
                },
                success: function (data) {
                        $("#upload_id").val(upload_id);
                        $("#url_dna_tumor_R1").attr("disabled", true);
                        $("#url_dna_tumor_R2").attr("disabled", true);
                        $("#confirmed_url_dna_tumor_R1").val(str_url_R1);
                        $("#confirmed_url_dna_tumor_R2").val(str_url_R2);
                        $("#dna_tumor_url_confirm_button").hide();
                        $("#dna_tumor_browser_upload").hide();
                        $("#dna_tumor_url_upload").show();
                        $("input[id=dna_tumor_from_url]").prop("checked", true).attr("checked", true);
                        $("#dna_T_upload_method").val($("input[name=dna_tumor_upload_method]:checked").val())
                        $("input[name=dna_tumor_upload_method]").attr("disabled", true);
                }
            });
        }
    });

    $("#dna_normal_url_confirm_button").click(function(event){
        var str_url_R1 = $("#url_dna_normal_R1").val();
        var str_url_R2 = $("#url_dna_normal_R2").val();
        $("#url_dna_normal_R1_err").text("");
        $("#url_dna_normal_R2_err").text("");

        if(str_url_R1 == "" || str_url_R2 == "") {
            if(str_url_R1 == "") {$("#url_dna_normal_R1_err").text("*Required field.");}
            if(str_url_R2 == "") {$("#url_dna_normal_R2_err").text("*Required field.");}
        }
        else {
            $.ajax({
                type: "POST",
                dataType: "json",
                url: "/confirm_urls",
                data: {
                    'csrfmiddlewaretoken': csrftoken,
                    'url_dna_normal_R1': str_url_R1,
                    'url_dna_normal_R2': str_url_R2,
                    'upload_id':upload_id,
                    'upload_id_rna':"None",
                    'upload_id_drna':"None"                },
                error: function () {
                    // do nothing
                    alert('Failed to download from the URLs. Please check your file links or formats.');
                },
                success: function (data) {
                        $("#upload_id").val(upload_id);
                        $("#url_dna_normal_R1").attr("disabled", true);
                        $("#url_dna_normal_R2").attr("disabled", true);
                        $("#confirmed_url_dna_normal_R1").val(str_url_R1);
                        $("#confirmed_url_dna_normal_R2").val(str_url_R2);
                        $("#dna_normal_url_confirm_button").hide();
                        $("#dna_normal_browser_upload").hide();
                        $("#dna_normal_url_upload").show();
                        $("input[id=dna_normal_from_url]").prop("checked", true).attr("checked", true);
                        $("#dna_N_upload_method").val($("input[name=dna_normal_upload_method]:checked").val())
                        $("input[name=dna_normal_upload_method]").attr("disabled", true);
                        
                }
            });
        }
    });


// DNA MASS

    $("#dna_mass_url_confirm_button").click(function(event){
        var str_url_Ms = $("#url_dna_Ms").val();
    $("#url_dna_Ms_err").text("");
        if(str_url_Ms == "") {
            $("#url_dna_Ms_err").text("*Required field.");
        }
        else {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/confirm_urls",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'url_dna_Ms': str_url_Ms,
                'upload_id':upload_id,
                'upload_id_rna':"None",
                'upload_id_drna':"None"
            },
            
            error: function () {
                alert('Failed to download from the URLs. Please check your file links or formats.');
            },
            success: function (data) {
                    confirmed_urls_stat['mass'] = true;
                    $("#url_dna_Ms").attr("disabled", true);
                    $("#dna_mass_confirmed_url").val(str_url_Ms);
                    $("#dna_mass_url_confirm_button").hide();
                    $("input[id=dna_mass_upload_method]").prop("checked", true).attr("checked", true);
                    $("#dna_Ms_upload_method").val($("input[name=dna_mass_upload_method]:checked").val())             
            }
        });
    }
    });



// RNA url
    $("#rna_tumor_url_confirm_button").click(function(event){
        var str_url_R1 = $("#url_rna_tumor_R1").val();
        var str_url_R2 = $("#url_rna_tumor_R2").val();
        $("#url_rna_tumor_R1_err").text("");
        $("#url_rna_tumor_R2_err").text("");
        // var upload_id_rna = Sha256.hash(Math.random());

        if(str_url_R1 == "" || str_url_R2 == "") {
        if(str_url_R1 == "") {$("#url_rna_tumor_R1_err").text("*Required field.");}
        if(str_url_R2 == "") {$("#url_rna_tumor_R2_err").text("*Required field.");}
        }
        else {
            $.ajax({
            type: "POST",
            dataType: "json",
            url: "/confirm_urls",
            // url: "/confirm_urls_rna",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'url_rna_tumor_R1': str_url_R1,
                'url_rna_tumor_R2': str_url_R2,
                'upload_id':"None",
                'upload_id_rna':upload_id_rna,
                'upload_id_drna':"None"
            },
            error: function () {
                // do nothing
                alert('Failed to download from the URLs. Please check your file links or formats.');
            },
            success: function (data) {
                    $("#upload_id_rna").val(upload_id_rna);
                    $("#url_rna_tumor_R1").attr("disabled", true);
                    $("#url_rna_tumor_R2").attr("disabled", true);
                    $("#confirmed_url_rna_tumor_R1").val(str_url_R1);
                    $("#confirmed_url_rna_tumor_R2").val(str_url_R2);
                    $("#rna_tumor_url_confirm_button").hide();
                    $("#rna_tumor_browser_upload").hide();
                    $("#rna_tumor_url_upload").show();
                    $("input[id=rna_tumor_from_url]").prop("checked", true).attr("checked", true);
                    $("#rna_T_upload_method").val($("input[name=rna_tumor_upload_method]:checked").val())
                    $("input[name=rna_tumor_upload_method]").attr("disabled", true);
            }
            });
        }
    });


    $("#rna_normal_url_confirm_button").click(function(event){
        var str_url_R1 = $("#url_rna_normal_R1").val();
        var str_url_R2 = $("#url_rna_normal_R2").val();
        $("#url_rna_normal_R1_err").text("");
        $("#url_rna_normal_R2_err").text("");

        if(str_url_R1 == "" || str_url_R2 == "") {
        if(str_url_R1 == "") {$("#url_rna_normal_R1_err").text("*Required field.");}
        if(str_url_R2 == "") {$("#url_rna_normal_R2_err").text("*Required field.");}
        }
        else {
            $.ajax({
            type: "POST",
            dataType: "json",
            url: "/confirm_urls",
            // url: "/confirm_urls_rna",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'url_rna_normal_R1': str_url_R1,
                'url_rna_normal_R2': str_url_R2,
                'upload_id':"None",
                'upload_id_rna':upload_id_rna,
                'upload_id_drna':"None"
            },
            error: function () {
                // do nothing
                alert('Failed to download from the URLs. Please check your file links or formats.');
            },
            success: function (data) {
                    $("#upload_id_rna").val(upload_id_rna);
                    $("#url_rna_normal_R1").attr("disabled", true);
                    $("#url_rna_normal_R2").attr("disabled", true);
                    $("#confirmed_url_rna_normal_R1").val(str_url_R1);
                    $("#confirmed_url_rna_normal_R2").val(str_url_R2);
                    $("#rna_normal_url_confirm_button").hide();
                    $("#rna_normal_browser_upload").hide();
                    $("#rna_normal_url_upload").show();
                    $("input[id=rna_normal_from_url]").prop("checked", true).attr("checked", true);
                    $("#rna_N_upload_method").val($("input[name=rna_normal_upload_method]:checked").val())
                    $("input[name=rna_normal_upload_method]").attr("disabled", true);
            }
            });
        }
    });

// RNA MASS

$("#rna_mass_url_confirm_button").click(function(event){
    var str_url_Ms = $("#url_rna_Ms").val();
$("#url_rna_Ms_err").text("");
    if(str_url_Ms == "") {
        $("#url_rna_Ms_err").text("*Required field.");
    }
    else {
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/confirm_urls",
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'url_rna_Ms': str_url_Ms,
            'upload_id':"None",
            'upload_id_rna':upload_id_rna,
            'upload_id_drna':"None"
        },
        
        error: function () {
            alert('Failed to download from the URLs. Please check your file links or formats.');
        },
        success: function (data) {
                confirmed_urls_stat['mass'] = true;
                $("#url_rna_Ms").attr("disabled", true);
                $("#rna_mass_confirmed_url").val(str_url_Ms);
                $("#rna_mass_url_confirm_button").hide(); 
                $("input[id=rna_mass_upload_method]").prop("checked", true).attr("checked", true);
                $("#rna_Ms_upload_method").val($("input[name=rna_mass_upload_method]:checked").val())             
        }
    });
}
});


// DNA + RNA url
$("#rdna_tumor_url_confirm_button").click(function(event){
    var str_url_R1 = $("#url_rdna_tumor_R1").val();
    var str_url_R2 = $("#url_rdna_tumor_R2").val();
    $("#url_rdna_tumor_R1_err").text("");
    $("#url_rdna_tumor_R2_err").text("");
    // var upload_id_drna = Sha256.hash(Math.random());

    if(str_url_R1 == "" || str_url_R2 == "") {
        if(str_url_R1 == "") {$("#url_rdna_tumor_R1_err").text("*Required field.");}
        if(str_url_R2 == "") {$("#url_rdna_tumor_R2_err").text("*Required field.");}
    }
    else {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/confirm_urls",
            // url: "/confirm_urls_drna", 
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'url_rdna_tumor_R1': str_url_R1,
                'url_rdna_tumor_R2': str_url_R2,
                'upload_id':"None",
                'upload_id_rna':"None",
                'upload_id_drna':upload_id_drna
            },
            error: function () {
                // do nothing
                alert('Failed to download from the URLs. Please check your file links or formats.');
            },
            success: function (data) {
                    $("#upload_id_drna").val(upload_id_drna);
                    $("#url_rdna_tumor_R1").attr("disabled", true);
                    $("#url_rdna_tumor_R2").attr("disabled", true);
                    $("#confirmed_url_rdna_tumor_R1").val(str_url_R1);
                    $("#confirmed_url_rdna_tumor_R2").val(str_url_R2);
                    $("#rdna_tumor_url_confirm_button").hide();
                    $("#rdna_tumor_browser_upload").hide();
                    $("#rdna_tumor_url_upload").show();
                    $("input[id=rdna_tumor_from_url]").prop("checked", true).attr("checked", true);
                    $("#rdna_T_upload_method").val($("input[name=rdna_tumor_upload_method]:checked").val())
                    $("input[name=rdna_tumor_upload_method]").attr("disabled", true);
            }
        });
    }
});

$("#rdna_normal_url_confirm_button").click(function(event){
    var str_url_R1 = $("#url_rdna_normal_R1").val();
    var str_url_R2 = $("#url_rdna_normal_R2").val();
    $("#url_rdna_normal_R1_err").text("");
    $("#url_rdna_normal_R2_err").text("");

    if(str_url_R1 == "" || str_url_R2 == "") {
        if(str_url_R1 == "") {$("#url_rdna_normal_R1_err").text("*Required field.");}
        if(str_url_R2 == "") {$("#url_rdna_normal_R2_err").text("*Required field.");}
    }
    else {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/confirm_urls",
            // url: "/confirm_urls_drna",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'url_rdna_normal_R1': str_url_R1,
                'url_rdna_normal_R2': str_url_R2,
                'upload_id':"None",
                'upload_id_rna':"None",
                'upload_id_drna':upload_id_drna            },
            error: function () {
                // do nothing
                alert('Failed to download from the URLs. Please check your file links or formats.');
            },
            success: function (data) {
                    $("#upload_id_drna").val(upload_id_drna);
                    $("#url_rdna_normal_R1").attr("disabled", true);
                    $("#url_rdna_normal_R2").attr("disabled", true);
                    $("#confirmed_url_rdna_normal_R1").val(str_url_R1);
                    $("#confirmed_url_rdna_normal_R2").val(str_url_R2);
                    $("#rdna_normal_url_confirm_button").hide();
                    $("#rdna_normal_browser_upload").hide();
                    $("#rdna_normal_url_upload").show();
                    $("input[id=rdna_normal_from_url]").prop("checked", true).attr("checked", true);
                    $("#rdna_N_upload_method").val($("input[name=rdna_normal_upload_method]:checked").val())
                    $("input[name=rdna_normal_upload_method]").attr("disabled", true);
            }
        });
    }
});

$("#drna_tumor_url_confirm_button").click(function(event){
    var str_url_R1 = $("#url_drna_tumor_R1").val();
    var str_url_R2 = $("#url_drna_tumor_R2").val();
    $("#url_drna_tumor_R1_err").text("");
    $("#url_drna_tumor_R2_err").text("");
    // var upload_id_drna = Sha256.hash(Math.random());

    if(str_url_R1 == "" || str_url_R2 == "") {
        if(str_url_R1 == "") {$("#url_drna_tumor_R1_err").text("*Required field.");}
        if(str_url_R2 == "") {$("#url_drna_tumor_R2_err").text("*Required field.");}
    }
    else {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/confirm_urls",
            // url: "/confirm_urls_drna",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'url_drna_tumor_R1': str_url_R1,
                'url_drna_tumor_R2': str_url_R2,
                'upload_id':"None",
                'upload_id_rna':"None",
                'upload_id_drna':upload_id_drna            },
            error: function () {
                // do nothing
                alert('Failed to download from the URLs. Please check your file links or formats.');
            },
            success: function (data) {
                    $("#upload_id_drna").val(upload_id_drna);
                    $("#url_drna_tumor_R1").attr("disabled", true);
                    $("#url_drna_tumor_R2").attr("disabled", true);
                    $("#confirmed_url_drna_tumor_R1").val(str_url_R1);
                    $("#confirmed_url_drna_tumor_R2").val(str_url_R2);
                    $("#drna_tumor_url_confirm_button").hide();
                    $("#drna_tumor_browser_upload").hide();
                    $("#drna_tumor_url_upload").show();
                    $("input[id=drna_tumor_from_url]").prop("checked", true).attr("checked", true);
                    $("#drna_T_upload_method").val($("input[name=drna_tumor_upload_method]:checked").val())
                    $("input[name=drna_tumor_upload_method]").attr("disabled", true);
            }
        });
    }
});


$("#drna_normal_url_confirm_button").click(function(event){
    var str_url_R1 = $("#url_drna_normal_R1").val();
    var str_url_R2 = $("#url_drna_normal_R2").val();
    $("#url_drna_normal_R1_err").text("");
    $("#url_drna_normal_R2_err").text("");

    if(str_url_R1 == "" || str_url_R2 == "") {
        if(str_url_R1 == "") {$("#url_drna_normal_R1_err").text("*Required field.");}
        if(str_url_R2 == "") {$("#url_drna_normal_R2_err").text("*Required field.");}
    }
    else {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/confirm_urls",
            // url: "/confirm_urls_drna",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'url_drna_normal_R1': str_url_R1,
                'url_drna_normal_R2': str_url_R2,
                'upload_id':"None",
                'upload_id_rna':"None",
                'upload_id_drna':upload_id_drna        
            },
            error: function () {
                // do nothing
                alert('Failed to download from the URLs. Please check your file links or formats.');
            },
            success: function (data) {
                    $("#upload_id_drna").val(upload_id_drna);
                    $("#url_drna_normal_R1").attr("disabled", true);
                    $("#url_drna_normal_R2").attr("disabled", true);
                    $("#confirmed_url_drna_normal_R1").val(str_url_R1);
                    $("#confirmed_url_drna_normal_R2").val(str_url_R2);
                    $("#drna_normal_url_confirm_button").hide();
                    $("#drna_normal_browser_upload").hide();
                    $("#drna_normal_url_upload").show();
                    $("input[id=drna_normal_from_url]").prop("checked", true).attr("checked", true);
                    $("#drna_N_upload_method").val($("input[name=drna_normal_upload_method]:checked").val())
                    $("input[name=drna_normal_upload_method]").attr("disabled", true);
            }
        });
    }
});

// DNA + RNA RNA MASS


$("#drna_mass_url_confirm_button").click(function(event){
    var str_url_Ms = $("#url_drna_Ms").val();
$("#url_drna_Ms_err").text("");
    if(str_url_Ms == "") {
        $("#url_drna_Ms_err").text("*Required field.");
    }
    else {
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/confirm_urls",
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'url_rna_Ms': str_url_Ms,
            'upload_id':"None",
            'upload_id_rna':"None",
            'upload_id_drna':upload_id_drna
        },
        
        error: function () {
            alert('Failed to download from the URLs. Please check your file links or formats.');
        },
        success: function (data) {
                confirmed_urls_stat['mass'] = true;
                $("#url_drna_Ms").attr("disabled", true);
                $("#drna_mass_confirmed_url").val(str_url_Ms);
                $("#drna_mass_url_confirm_button").hide();  
                $("input[id=drna_mass_upload_method]").prop("checked", true).attr("checked", true);
                $("#drna_Ms_upload_method").val($("input[name=drna_mass_upload_method]:checked").val())             
        }
    });
}
});

// upload_method
// DNA
$("input[name='dna_tumor_upload_method']").change(function(){
    if($("#dna_tumor_from_browser").is(':checked')){
        $("#dna_tumor_url_upload").hide();
        $("#dna_tumor_browser_upload").show();
    }
    else if($("#dna_tumor_from_url").is(':checked')){
        $("#dna_tumor_browser_upload").hide();
        $("#dna_tumor_url_upload").show();
    }

});

$("input[name='dna_normal_upload_method']").change(function(){
    if($("#dna_normal_from_browser").is(':checked')){
        $("#dna_normal_url_upload").hide();
        $("#dna_normal_browser_upload").show();
    }
    else if($("#dna_normal_from_url").is(':checked')){
        $("#dna_normal_browser_upload").hide();
        $("#dna_normal_url_upload").show();
    }

});

$("input[name='dna_mass_upload_method']").change(function(){
    if($("#dna_mass_from_browser").is(':checked')){
        $("#dna_mass_url_upload").hide();
        $("#dna_mass_browser_upload").show();
    }
    else if($("#dna_mass_from_url").is(':checked')){
        $("#dna_mass_browser_upload").hide();
        $("#dna_mass_url_upload").show();
    }

});
// RNA
$("input[name='rna_tumor_upload_method']").change(function(){
    if($("#rna_tumor_from_browser").is(':checked')){
        $("#rna_tumor_url_upload").hide();
        $("#rna_tumor_browser_upload").show();
    }
    else if($("#rna_tumor_from_url").is(':checked')){
        $("#rna_tumor_browser_upload").hide();
        $("#rna_tumor_url_upload").show();
    }

});

$("input[name='rna_normal_upload_method']").change(function(){
    if($("#rna_normal_from_browser").is(':checked')){
        $("#rna_normal_url_upload").hide();
        $("#rna_normal_browser_upload").show();
    }
    else if($("#rna_normal_from_url").is(':checked')){
        $("#rna_normal_browser_upload").hide();
        $("#rna_normal_url_upload").show();
    }

});

$("input[name='rna_mass_upload_method']").change(function(){
    if($("#rna_mass_from_browser").is(':checked')){
        $("#rna_mass_url_upload").hide();
        $("#rna_mass_browser_upload").show();
    }
    else if($("#rna_mass_from_url").is(':checked')){
        $("#rna_mass_browser_upload").hide();
        $("#rna_mass_url_upload").show();
    }

});
// DNA+RNA
$("input[name='rdna_tumor_upload_method']").change(function(){
    if($("#rdna_tumor_from_browser").is(':checked')){
        $("#rdna_tumor_url_upload").hide();
        $("#rdna_tumor_browser_upload").show();
    }
    else if($("#rdna_tumor_from_url").is(':checked')){
        $("#rdna_tumor_browser_upload").hide();
        $("#rdna_tumor_url_upload").show();
    }

});

$("input[name='rdna_normal_upload_method']").change(function(){
    if($("#rdna_normal_from_browser").is(':checked')){
        $("#rdna_normal_url_upload").hide();
        $("#rdna_normal_browser_upload").show();
    }
    else if($("#rdna_normal_from_url").is(':checked')){
        $("#rdna_normal_browser_upload").hide();
        $("#rdna_normal_url_upload").show();
    }

});

$("input[name='drna_tumor_upload_method']").change(function(){
    if($("#drna_tumor_from_browser").is(':checked')){
        $("#drna_tumor_url_upload").hide();
        $("#drna_tumor_browser_upload").show();
    }
    else if($("#drna_tumor_from_url").is(':checked')){
        $("#drna_tumor_browser_upload").hide();
        $("#drna_tumor_url_upload").show();
    }

});

$("input[name='drna_normal_upload_method']").change(function(){
    if($("#drna_normal_from_browser").is(':checked')){
        $("#drna_normal_url_upload").hide();
        $("#drna_normal_browser_upload").show();
    }
    else if($("#drna_normal_from_url").is(':checked')){
        $("#drna_normal_browser_upload").hide();
        $("#drna_normal_url_upload").show();
    }

});

$("input[name='drna_mass_upload_method']").change(function(){
    if($("#drna_mass_from_browser").is(':checked')){
        $("#drna_mass_url_upload").hide();
        $("#drna_mass_browser_upload").show();
    }
    else if($("#drna_mass_from_url").is(':checked')){
        $("#drna_mass_browser_upload").hide();
        $("#drna_mass_url_upload").show();
    }

});

// HLA upload setting
$('#DNA-HLA-multiple').select2({
            width: "80%",
            allowClear: true,
            maximumSelectionLength: 8,
        });

$('#RNA-HLA-multiple').select2({
            width: "80%",
            allowClear: true,
            maximumSelectionLength: 8,
        });

$('#DNA-RNA-HLA-multiple').select2({
            width: "80%",
            allowClear: true,
            maximumSelectionLength: 8,
        });

$("input[name='dna_hla_upload_method']").change(function(){
    if($("#dna_hla_from_bottom").is(':checked')){
        $("#dna_hla_process").hide();
        $("#dna_hla_bottom").show();
    }
    else if($("#dna_hla_in_process").is(':checked')){
        $("#dna_hla_bottom").hide();
        $("#dna_hla_process").show();
    }

});

$("input[name='rna_hla_upload_method']").change(function(){
    if($("#rna_hla_from_bottom").is(':checked')){
        $("#rna_hla_process").hide();
        $("#rna_hla_bottom").show();
    }
    else if($("#rna_hla_in_process").is(':checked')){
        $("#rna_hla_bottom").hide();
        $("#rna_hla_process").show();
    }

});

$("input[name='drna_hla_upload_method']").change(function(){
    if($("#drna_hla_from_bottom").is(':checked')){
        $("#drna_hla_process").hide();
        $("#drna_hla_bottom").show();
    }
    else if($("#drna_hla_in_process").is(':checked')){
        $("#drna_hla_bottom").hide();
        $("#drna_hla_process").show();
    }

});

// ic50 setting
$("input[name='dna_ic50_setting']").change(function(){
    if($("#dna_ic50_default").is(':checked')){
        $("table[name='dna_ic50_table']").hide();
    }
    if($("#dna_ic50_custom").is(':checked')){
        $("table[name='dna_ic50_table']").show();
    }
});

$("input[name='rna_ic50_setting']").change(function(){
    if($("#rna_ic50_default").is(':checked')){
        $("table[name='rna_ic50_table']").hide();
    }
    if($("#rna_ic50_custom").is(':checked')){
        $("table[name='rna_ic50_table']").show();
    }
});

$("input[name='drna_ic50_setting']").change(function(){
    if($("#drna_ic50_default").is(':checked')){
        $("table[name='drna_ic50_table']").hide();
    }
    if($("#drna_ic50_custom").is(':checked')){
        $("table[name='drna_ic50_table']").show();
    }
});

$("#dna_max_ic_strong").on("change", function(e){
    var x = $("#dna_max_ic_inter").val()
  if($(this).val() > (x*100)/100-1){
    $(this).val(((x*100)/100-1));
    alert("Max ic50 for strong binding cannot excede max ic50 for intermediate binding")
  }
});

$("#dna_max_ic_inter").on("change", function(e){
    var x = $("#dna_max_ic_strong").val()
  if($(this).val() < (x*100)/100+1){
    $(this).val(((x*100)/100+1));
    alert("Max ic50 for intermediate binding cannot be less than max ic50 for strong binding")
  }
});

$("#dna_max_ic_inter").on("change", function(e){
    var x = $("#dna_max_ic_weak").val()
  if($(this).val() > (x*100)/100-1){
    $(this).val(((x*100)/100-1));
    alert("Max ic50 for intermediate binding cannot excede max ic50 for weak binding")
  }
});

$("#dna_max_ic_weak").on("change", function(e){
    var x = $("#dna_max_ic_inter").val()
  if($(this).val() < (x*100)/100+1){
    $(this).val(((x*100)/100+1));
    alert("Max ic50 for weak binding cannot be less than max ic50 for intermediate binding")
  }
});

$("#rna_max_ic_strong").on("change", function(e){
    var x = $("#rna_max_ic_inter").val()
  if($(this).val() > (x*100)/100-1){
    $(this).val(((x*100)/100-1));
    alert("Max ic50 for strong binding cannot excede max ic50 for intermediate binding")
  }
});

$("#rna_max_ic_inter").on("change", function(e){
    var x = $("#rna_max_ic_strong").val()
  if($(this).val() < (x*100)/100+1){
    $(this).val(((x*100)/100+1));
    alert("Max ic50 for intermediate binding cannot be less than max ic50 for strong binding")
  }
});

$("#rna_max_ic_inter").on("change", function(e){
    var x = $("#rna_max_ic_weak").val()
  if($(this).val() > (x*100)/100-1){
    $(this).val(((x*100)/100-1));
    alert("Max ic50 for intermediate binding cannot excede max ic50 for weak binding")
  }
});

$("#rna_max_ic_weak").on("change", function(e){
    var x = $("#rna_max_ic_inter").val()
  if($(this).val() < (x*100)/100+1){
    $(this).val(((x*100)/100+1));
    alert("Max ic50 for weak binding cannot be less than max ic50 for intermediate binding")
  }
});

$("#drna_max_ic_strong").on("change", function(e){
    var x = $("#drna_max_ic_inter").val()
  if($(this).val() > (x*100)/100-1){
    $(this).val(((x*100)/100-1));
    alert("Max ic50 for strong binding cannot excede max ic50 for intermediate binding")
  }
});

$("#drna_max_ic_inter").on("change", function(e){
    var x = $("#drna_max_ic_strong").val()
  if($(this).val() < (x*100)/100+1){
    $(this).val(((x*100)/100+1));
    alert("Max ic50 for intermediate binding cannot be less than max ic50 for strong binding")
  }
});

$("#drna_max_ic_inter").on("change", function(e){
    var x = $("#drna_max_ic_weak").val()
  if($(this).val() > (x*100)/100-1){
    $(this).val(((x*100)/100-1));
    alert("Max ic50 for intermediate binding cannot excede max ic50 for weak binding")
  }
});

$("#drna_max_ic_weak").on("change", function(e){
    var x = $("#drna_max_ic_inter").val()
  if($(this).val() < (x*100)/100+1){
    $(this).val(((x*100)/100+1));
    alert("Max ic50 for weak binding cannot be less than max ic50 for intermediate binding")
  }
});



// RNA-seq special setting
$("input[name='expression_setting']").change(function(){
    if($("#expression_default").is(':checked')){
        $("table[name='expression_table']").hide();
    }
    if($("#expression_custom").is(':checked')){
        $("table[name='expression_table']").show();
    }
});

$("input[name='variant_calling_setting']").change(function(){
    if($("#variant_default").is(':checked')){
        $("table[name='variant_table']").hide();
    }
    if($("#variant_custom").is(':checked')){
        $("table[name='variant_table']").show();
    }
});

// DNA + RNA-seq special setting
$("input[name='drna_expression_setting']").change(function(){
    if($("#drna_expression_default").is(':checked')){
        $("table[name='drna_expression_table']").hide();
    }
    if($("#drna_expression_custom").is(':checked')){
        $("table[name='drna_expression_table']").show();
    }
});


// submission setting
$("#dna_accept_privacy_statement").change(function(){
    var check_val;
    check_val = $("#dna_accept_privacy_statement:checked").val();
    if(check_val == "accept"){
        $("#dna_submission_panel").show();
    }
    else {
        $("#dna_submission_panel").hide();
    }
});

$("#rna_accept_privacy_statement").change(function(){
    var check_val;
    check_val = $("#rna_accept_privacy_statement:checked").val();
    if(check_val == "accept"){
        $("#rna_submission_panel").show();
    }
    else {
        $("#rna_submission_panel").hide();
    }
});

$("#drna_accept_privacy_statement").change(function(){
    var check_val;
    check_val = $("#drna_accept_privacy_statement:checked").val();
    if(check_val == "accept"){
        $("#drna_submission_panel").show();
    }
    else {
        $("#drna_submission_panel").hide();
    }
});

function validateEmail(email) {
  var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
};

$("#submit_dna").click(function() {
    if(!validateEmail($("#email_dna").val()))
    {
        alert("Email invalid!");
        return false;
    }
    if($("#email_dna").val() !=$("#re_enter_dna").val())
    {
        alert("Email re-enter not matched!");
        return false;
    }
    if($("#dna_accept_privacy_statement:checked").val() != "accept")
    {
        alert("Must accept the Privacy Statement of NARWHAL!");
        return false;
    }

});

$("#submit_rna").click(function() {
    if(!validateEmail($("#email_rna").val()))
    {
        alert("Email invalid!");
        return false;
    }
    if($("#email_rna").val() !=$("#re_enter_rna").val())
    {
        alert("Email re-enter not matched!");
        return false;
    }
    if($("#rna_accept_privacy_statement:checked").val() != "accept")
    {
        alert("Must accept the Privacy Statement of NARWHAL!");
        return false;
    }

});

$("#submit_drna").click(function() {
    if(!validateEmail($("#email_drna").val()))
    {
        alert("Email invalid!");
        return false;
    }
    if($("#email_drna").val() !=$("#re_enter_drna").val())
    {
        alert("Email re-enter not matched!");
        return false;
    }
    if($("#drna_accept_privacy_statement:checked").val() != "accept")
    {
        alert("Must accept the Privacy Statement of NARWHAL!");
        return false;
    }

});

});




