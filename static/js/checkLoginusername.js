$(document).ready(function(){
    $('#username').change( function(e){
        var username = $('#username').val();

        if(username != ''){
  
           $.ajax({
              url: '/checkloginusername',
              type: 'post',
              data: {username: username},
              success: function(response){
                    if (response == "No User"){
                        $('#uname_response').html("User does not exist").css({'color':'red', 'text-align':'right'});
                        $('#button').prop('disabled', true);
                    }else{
                        $('#uname_response').html("");
                        $('#button').removeAttr('disabled');
                    }
               }
           });
        }else{
           $("#uname_response").html("");
        }
    })
})