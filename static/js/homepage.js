
$(window).load(function() {    $('.selectpicker').selectpicker({
        width:'100%',
   });

     $("#control-file-upload").hide();
     $("#custom-filtering").hide();
     $("#control").prop("checked", false);
     $("#step").selectpicker("deselectAll");
     $("#input_model").selectpicker("deselectAll");
     $("#input_model").selectpicker('val','no');
     $('#input_model').selectpicker('render');
     // $('#my-affix').affix({
    // 	 target:$("#affix-container")});
     // if($('#phenotype').val().length){
   	 //  $('select.selectpicker#input_gene').selectpicker('val', 'refgene');
   	 //  $('select.selectpicker#input_gene').prop('disabled',true);
     //     $('select.selectpicker#input_gene').selectpicker('refresh');
     //      }
     $('#my-affix').affix({
        target: $("#affix-container")});
    var phenotype = $('#phenotype');
    if (phenotype.length && phenotype.val().length) {
        var inputGene = $('select.selectpicker#input_gene');
        inputGene.selectpicker('val', 'refgene');
        inputGene.prop('disabled', true);
        inputGene.selectpicker('refresh');
    }
     });
//file upload
$(document).on('change', '.btn-file :file', function() {
  var input = $(this),
      numFiles = input.get(0).files ? input.get(0).files.length : 1,
      label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
  input.trigger('fileselect', [numFiles, label]);
});

$(document).ready( function() {
	  var disease_model =  $("#input_model");
	  var check_term =   $('input#term');
	  var build_select = $('#ref_genome');
	  var gene_definition = $('#input_gene');
	  build_select.change(function(){
		if(build_select.children("option:selected").val() == "hg18")
		{
		  $("#exac03").hide();
		  $("#step").selectpicker('refresh');
		  disease_model.find("option[value=custom]").show();
		  disease_model.prop('disabled', false);
		  disease_model.selectpicker('refresh');
		  gene_definition.children("option[value=ensgene]").show();
		  gene_definition.children("option[value=gencodegene]").show();
		  gene_definition.selectpicker('refresh');
		}
		else if(build_select.children("option:selected").val() == "hg38")
		{

		  if (disease_model.find("option[value=custom]").prop("selected")) {
			  disease_model.find("option:selected").prop("selected",false);
		      disease_model.find("option[value=no]").prop("selected",true);
		  }
		  disease_model.find("option[value=custom]").hide();
		  disease_model.selectpicker('refresh');
		  $('#custom-filtering').fadeOut(300);
		  gene_definition.children("option[value=ensgene]").hide();
		  gene_definition.children("option[value=gencodegene]").hide();
		  gene_definition.selectpicker('refresh');
		}
		else if(build_select.children("option:selected").val() == "hg19")
		{
		  $("#exac03").show();
		  disease_model.find("option[value=custom]").show();
		  $("#step").selectpicker('refresh');
		  disease_model.prop('disabled', false);
		  disease_model.selectpicker('refresh');
		  gene_definition.children("option[value=ensgene]").show();
		  gene_definition.children("option[value=gencodegene]").show();
		  gene_definition.selectpicker('refresh');
		}
	  })


	  check_term.prop('checked','true');
	  check_term.change(function(){
			  $('button[type="submit"]').toggleClass('disabled');
	  });

	  $("[data-toggle='popover']").popover({container: 'body',
	   	  trigger: 'click',
	   	 html:true
	   	  });
    $('.btn-file :file').on('fileselect', function(event, numFiles, label) {

        var input = $(this).parents('.input-group').find(':text'),
            log = numFiles > 1 ? numFiles + ' files selected' : label;

        if( input.length ) {
            input.val(log);
        } else {
            if( log ) alert(log);
        }
        });
//modal format
      $(".modal").modal({
    	  keyboard: false,
    	  show:false,
    	  backdrop:"static"
      });


      disease_model.change(function(){
     	 if(disease_model.find("option:selected").val()=="custom" )
     		 { $("#custom-filtering").fadeIn(500); }
     	 else{ $("#custom-filtering").fadeOut(300);  }

      });
      $("#control").click(function(){
    	 if($(this).prop("checked")) { $("#control-file-upload").fadeIn(500);}
    	 else  {$("#control-file-upload").fadeOut(300);}
      });

//The autocomplete
      var disease_input=$("#phenotype");
      var disease_count;
      var old_string;
      var url = document.URL;
     url =  url.replace(/index\.(php|html)/,"");
      $.when(
        $.get(url+'hot_disease_term.txt', function (data) {
       	   disease_count = data.split("\n");
       	   disease_count.pop();
   	   })
          ).then(function(){
          disease_input.autocomplete({
   	   source: function( request, response ) {
   	   var terms = request.term.split(/\s*[^' ,_\.\w\-\[\]\(\)\{\}\/]+\s*/);
   	   var term = terms[terms.length-1];
   	   if(terms.length>=2) {old_string = terms.splice(0,terms.length-1).join("\n");
   	                        old_string += "\n"; }
   	   else {old_string ="";}
          var matcher = new RegExp( "^" + $.ui.autocomplete.escapeRegex( term ), "i" );
          var list = $.grep(disease_count , function( item ){return matcher.test( item );} );
          if(list.length>=50){ list=list.slice(list.length-50);}
          list = list.reverse();
          response(list);
   	   },
   	   minLength:0,
   	   position: { my : "left bottom", at: "left top" },
   	   select: function( event, ui ) {
   		   event.preventDefault();
   		   disease_input.val ( old_string + ui.item.value ); }
        });
      });
  //turn off Reference Genome selection when using Phenolyzer
       $('#phenotype').bind('input propertychange', function() {
    	      if(this.value.length){
    	    	  $('select.selectpicker#input_gene').selectpicker('val', 'refgene');
    	    	  $('select.selectpicker#input_gene').prop('disabled',true);
    	          $('select.selectpicker#input_gene').selectpicker('refresh');
    	      }
    	      else
    	      {
    	    	  $('select.selectpicker#input_gene').prop('disabled',false);
    	    	  $('select.selectpicker#input_gene').selectpicker('refresh');
    	      }
    	});

});
